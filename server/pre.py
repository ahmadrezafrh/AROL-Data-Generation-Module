# -*- coding: utf-8 -*-

import pandas as pd
from modules.preprocessing import Extract, ExtractPlc, plot_heads, plot_correlation
from modules.config import PLC, DRIVE, EQTQ
import os
import plotly.express as px



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






plc = PLC()
drive = DRIVE()
eqtq = EQTQ()


n_colors = 24
colors = px.colors.sample_colorscale("greys", [n/(n_colors -1) for n in range(n_colors)]) 
colors = px.colors.qualitative.Set2 


plc_data = ExtractPlc(category='plc', sensors=plc.all_sensors, machinery='JF890' ,show_fig=False, save_fig=True, verbose=False)
raw_plc = plc_data.get_raw_data()
extracted_raw_plc = plc_data.extract_raw_data()
pre_plc, det_plc = plc_data.preprocess_data(extracted_raw_plc)
fiiled_plc = plc_data.fill_data(pre_plc, det_plc)
for sensor in plc.all_sensors:
    if sensor not in det_plc:
        sensor_plc =  sensor
        plot_heads(fiiled_plc[sensor_plc], sensor_plc, 'plc', colors, True)


drive_data = Extract(category='drive', sensors=drive.all_sensors, machinery='JF890' ,show_fig=False, save_fig=True, verbose=False)
raw_drive = drive_data.get_raw_data()
extracted_raw_drive = drive_data.extract_raw_data()
pre_drive, det_drive = drive_data.preprocess_data(extracted_raw_drive)
fiiled_drive = drive_data.fill_data(pre_drive, det_drive)
for sensor in drive.all_sensors:
    if sensor not in det_drive:
        sensor_drive =  sensor
        plot_correlation(fiiled_drive[sensor_drive], sensor_drive, 'drive', True)
        plot_heads(fiiled_drive[sensor_drive], sensor_drive, 'drive', colors, True)



eqtq_data = Extract(category='eqtq', sensors=eqtq.all_sensors, machinery='JF890' ,show_fig=False, save_fig=True, verbose=False)
raw_eqtq = eqtq_data.get_raw_data()
extracted_raw_eqtq = eqtq_data.extract_raw_data()
pre_eqtq, det_eqtq = eqtq_data.preprocess_data(extracted_raw_eqtq)
fiiled_eqtq = eqtq_data.fill_data(pre_eqtq, det_eqtq)
for sensor in eqtq.all_sensors:
    if sensor not in det_eqtq:
        sensor_eqtq =  sensor
        plot_correlation(fiiled_eqtq[sensor_eqtq], sensor_eqtq, 'eqtq', True)
        plot_heads(fiiled_eqtq[sensor_eqtq], sensor_eqtq, 'eqtq', colors, True)



sample_heads = ['Head_09', 'Head_10', 'Head_11', 'Head_12']
print(fiiled_eqtq['AverageFriction'].head()[sample_heads].to_latex(float_format="{:.2f}".format))










# inf_args = InferArgs(heads=24, category='eqtq', sensor='AverageFriction', machinery='JF890')
# train_args = TrainArgs(target=['Head_01'])
# def main(inf_args, train_args):
    
#     if inf_args.category=='eqtq':
#         data_obj = EQTQ(heads=inf_args.heads, machinery=inf_args.machinery)
#     if inf_args.category=='drive':
#         data_obj = DRIVE(heads=inf_args.heads, machinery=inf_args.machinery)
#     if inf_args.category=='plc':
#         data_obj = PLC(heads=inf_args.heads, machinery=inf_args.machinery)
    

        
#     data_obj.set_sensors(data_obj.all_sensors) 
#     data_obj.set_unk_variables()
    
#     if inf_args.category=='plc':
#         extract_obj = ExtractPlc(data_obj.sensors, inf_args.category, inf_args.machinery)
#     else:
#         extract_obj = Extract(data_obj.sensors, inf_args.category, inf_args.machinery)
#     _ = extract_obj.get_raw_data()
    
#     extracted_data = extract_obj.extract_raw_data()
    
#     pre_data, det_sensors = extract_obj.preprocess_data(extracted_data)
#     if inf_args.sensor in det_sensors:
#         return 0
#     filled_df = extract_obj.fill_data(extracted_data, det_sensors)

#     data_obj.load_data(filled_df)
#     train_data = data_obj.get_sensor(inf_args.sensor)
    
#     train_data = train_data[~train_data.index.duplicated(keep='first')]
#     for var in data_obj.unk_variables:
#         train_data[var] = train_data[var].abs()
    
    
#     train_args.set_train_cutoff(train_data)
#     trainer = Trainer(
#                 learning_rate = train_args.learning_rate,
#                 epochs = train_args.epochs,
#                 batch_size = train_args.batch_size,
#                 device = train_args.accelerator,
#                 )


#     trainer.create_dataloaders(
#                 train_data,
#                 train_args.training_cutoff,
#                 train_args.max_prediction_length,
#                 train_args.max_encoder_length,
#                 train_args.target,
#                 data_obj.unk_variables,
#                 train_args.group_ids
#             )

#     _ = trainer.set_model(
#                 train_args.hidden_size,
#                 train_args.hidden_continuous_size,
#                 train_args.attention_head_size,
#                 train_args.dropout
#             )   

#     _ = trainer.set_trainer(
#                 inf_args.machinery,
#                 inf_args.category,
#                 inf_args.sensor,
#                 train_args.target,
#                 train_args.devices,
#                 train_args.logs_dir,
#                 train_args.checkpoints_dir,
#                 train_args.clipping,
#                 train_args.model_summary,
#                 train_args.min_delta,
#                 train_args.patience,
#                 train_args.verbose,
#                 train_args.early_mode,
#             )

#     if inf_args.lr_tuning:
#         _ = trainer.find_lr(replace=train_args.lr_tuning)
        
#     if train_args.path:
#         print("loading pretrained model")
#         trainer.load_model(train_args.path)
#     else:
#         print("model does not exists")
#         print("start training model")
#         trainer.fit()
#         print("model have been trained successfully")


#     return trainer


# trainer = main(inf_args, train_args)
# trainer.load_model('checkpoints/JF890/eqtq/Head_01/AverageFriction.ckpt')

# trainer.val_predict(True)
# trainer.pred_by_variable(True)






