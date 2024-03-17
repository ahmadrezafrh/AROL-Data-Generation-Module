# -*- coding: utf-8 -*-


import os, sys
import warnings
import contextlib
import logging
import torch.multiprocessing as mp
import pickle
import shutil

from modules.preprocessing import Extract
from modules.preprocessing import ExtractPlc
from modules.trainer import Trainer
from modules.config import EQTQ, PLC, DRIVE, TrainArgs, InferArgs
from tqdm import tqdm
from functools import partialmethod

tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
warnings.filterwarnings("ignore")



def main(inf_args, train_args):
    
    if inf_args.category=='eqtq':
        data_obj = EQTQ(heads=inf_args.heads, machinery=inf_args.machinery)
    if inf_args.category=='drive':
        data_obj = DRIVE(heads=inf_args.heads, machinery=inf_args.machinery)
    if inf_args.category=='plc':
        data_obj = PLC(heads=inf_args.heads, machinery=inf_args.machinery)
    

        
    data_obj.set_sensors(data_obj.all_sensors) 
    data_obj.set_unk_variables()
    
    if inf_args.category=='plc':
        extract_obj = ExtractPlc(data_obj.sensors, inf_args.category, inf_args.machinery)
    else:
        extract_obj = Extract(data_obj.sensors, inf_args.category, inf_args.machinery)
    _ = extract_obj.get_raw_data()
    
    extracted_data = extract_obj.extract_raw_data()
    
    pre_data, det_sensors = extract_obj.preprocess_data(extracted_data)
    if inf_args.sensor in det_sensors:
        return 0
    filled_df = extract_obj.fill_data(extracted_data, det_sensors)

    data_obj.load_data(filled_df)
    train_data = data_obj.get_sensor(inf_args.sensor)
    
    train_data = train_data[~train_data.index.duplicated(keep='first')]
    for var in data_obj.unk_variables:
        train_data[var] = train_data[var].abs()
    
    
    train_args.set_train_cutoff(train_data)
    trainer = Trainer(
                learning_rate = train_args.learning_rate,
                epochs = train_args.epochs,
                batch_size = train_args.batch_size,
                device = train_args.accelerator,
                )


    trainer.create_dataloaders(
                train_data,
                train_args.training_cutoff,
                train_args.max_prediction_length,
                train_args.max_encoder_length,
                train_args.target,
                data_obj.unk_variables,
                train_args.group_ids
            )

    _ = trainer.set_model(
                train_args.hidden_size,
                train_args.hidden_continuous_size,
                train_args.attention_head_size,
                train_args.dropout
            )   

    _ = trainer.set_trainer(
                inf_args.machinery,
                inf_args.category,
                inf_args.sensor,
                train_args.target,
                train_args.devices,
                train_args.logs_dir,
                train_args.checkpoints_dir,
                train_args.clipping,
                train_args.model_summary,
                train_args.min_delta,
                train_args.patience,
                train_args.verbose,
                train_args.early_mode,
            )

    if inf_args.lr_tuning:
        _ = trainer.find_lr(replace=train_args.lr_tuning)
        
    if train_args.path:
        print("loading pretrained model")
        trainer.load_model(train_args.path)
    else:
        print("model does not exists")
        print("start training model")
        trainer.fit()
        print("model have been trained successfully")


    return det_sensors



def run_eqtq_drive(task, i):
    width = 50
    logging.disable(sys.maxsize)
    with open('./pickles/det_sensors.pickle', 'rb') as handle:
        det_sensors = pickle.load(handle)
    for pid in task:
        inf_args = InferArgs(heads=pid[0], category=pid[1], sensor=pid[2], machinery=pid[3])
        train_args = TrainArgs(target=[pid[4]])
        dist = f"MODEL: {pid[3]+',': <{7}} {pid[1]+',': <{7}} {pid[2]+',': <{17}} {pid[4]+','}"
        try:
            with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
                _ = main(inf_args, train_args)
            if pid[2] in list(det_sensors[pid[1]].keys()):
                print(f"{dist : <{width}}  TRAINING: SUCCESSFULL,  DETERMINISTIC: TRUE,   PID: {os.getpid()}")
            else:
                print(f"{dist : <{width}}  TRAINING: SUCCESSFULL,  DETERMINISTIC: FALSE,  PID: {os.getpid()}")
    
        except Exception as e:
            print(f"{dist : <{width}}  TRAINING: FAILED,  PID: {os.getpid()}, {e}")
        
        
def run_plc(task, i):
    width = 50
    logging.disable(sys.maxsize)
    with open('./pickles/det_sensors.pickle', 'rb') as handle:
        det_sensors = pickle.load(handle)
    for pid in task:
        inf_args = InferArgs(category=pid[0], sensor=pid[1], machinery=pid[2])
        train_args = TrainArgs(target=['value'])
        dist = f"MODEL: {pid[2]+',': <{7}} {pid[0]+',': <{7}} {pid[1]+',': <{17}}"
        try:
            with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
                _ = main(inf_args, train_args)
            if pid[1] in list(det_sensors[pid[0]].keys()):
                print(f"{dist : <{width}}  TRAINING: SUCCESSFULL,  DETERMINISTIC: TRUE,   PID: {os.getpid()}")
            else:
                print(f"{dist : <{width}}  TRAINING: SUCCESSFULL,  DETERMINISTIC: False,  PID: {os.getpid()}")
        except Exception as e:
            print(f"{dist : <{width}}  TRAINING: FAILED,  PID: {os.getpid()}, {e}")

def split(lst,n):
    return [lst[i::n] for i in range(n)]



def train():
    train_args = TrainArgs
    if os.path.exists(train_args.checkpoints_dir):
        shutil.rmtree(train_args.checkpoints_dir)
    
    eqtq_sensors = EQTQ().all_sensors
    drive_sensors = DRIVE().all_sensors
    plc_sensors = PLC().all_sensors
    machines = {
        'XB056' : 1,  
        'JF890' : 24,  
        'WM100' : 24,  
        'JF891' : 24,  
        'XB098' : 1,  
        'JF893' : 24,  
    }
    
    categories = ['eqtq', 'drive']
    
    
    tasks=[]
    for machinery in machines.keys():
        heads = [f'Head_{i+1:>02}' for i in range(machines[machinery])]
        n_heads = len(heads)
        for category in categories:
            if category=='drive':
                sensors = drive_sensors
            if category=='eqtq':
                sensors = eqtq_sensors
            for sensor in sensors:
                for head in heads:
                    tasks.append([n_heads, category, sensor, machinery, head])
                    
                    
    tasks = split(tasks, train_args.n_process)
    processes = []
    for i in range(train_args.n_process):
        try:
           mp.set_start_method('spawn', force=True)
           print("spawned")
        except RuntimeError:
           pass
        p = mp.Process(target=run_eqtq_drive, args=(tasks[i],i))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()

    categories = ['plc']
    tasks=[]
    for machinery in machines.keys():
        for category in categories:
            sensors = plc_sensors
            for sensor in sensors:
                tasks.append([category, sensor, machinery])
                    
                    
    tasks = split(tasks, train_args.n_process)
    processes = []
    for i in range(train_args.n_process):
        try:
           mp.set_start_method('spawn', force=True)
           print("spawned")
        except RuntimeError:
           pass
        p = mp.Process(target=run_plc, args=(tasks[i],i))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()
        
    


if __name__=="__main__":
    train()
    


