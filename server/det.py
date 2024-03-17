# -*- coding: utf-8 -*-
import pandas as pd
import os
import warnings
import pickle

from modules.config import EQTQ, DRIVE, PLC, InferArgs
from modules.preprocessing import Extract
from modules.preprocessing import ExtractPlc

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
warnings.filterwarnings("ignore")


def create_det_dict(args, data, det_dict):
        
    data.set_sensors(data.all_sensors) 
    extract_obj = Extract(data.sensors, args.category, args.machinery)
    raw = extract_obj.get_raw_data()
    
    extracted_data = extract_obj.extract_raw_data()
    pre_data, det_sensors = extract_obj.preprocess_data(extracted_data)
    det_dict[args.category] = dict.fromkeys(det_sensors)
    heads = [f'Head_{i+1:>02}' for i in range(24)]
    for det in det_sensors:
        df_det = pre_data[det]
        det_dict[args.category][det] = dict.fromkeys([f'Head_{i+1:>02}' for i in range(24)])
        for head in heads:
            vals = df_det[[head]].dropna()
            value = float(vals.iloc[0])
            det_dict[args.category][det][head] = value
    

    sensors_cpy = data.all_sensors.copy()
    sensor_dict = {key: pd.DataFrame(columns=raw.folder.unique()) for key in sensors_cpy}

    for head in raw.folder.unique():
        df_head = pd.DataFrame(raw[raw.folder==head].samples.sum())
        df_head = df_head.dropna()
        # df_head.value = df_head.value.map(lambda x: float(x[list(x.keys())[0]]))
        # We need to correct the timestamps
        df_head.time = df_head.time.map(lambda x: float(x[list(x.keys())[0]]))
        df_head.index = df_head.set_index('time').index.astype(int)/1000
        # df_head.index = pd.to_datetime(df_head.index/1000, unit='s')
        # df_head = df_head.drop_duplicates()
        for sensor in sensors_cpy:
            # In this function we try to understand the relationship between deifferent heads
            # We delete the index, so we can join different heads, this is a prototype. 
            df_by_sensor = df_head[df_head.name.str.contains(sensor)]
            sensor_dict[sensor] = pd.concat([sensor_dict[sensor], df_by_sensor.value.rename(head).to_frame()])
    
    
    return det_dict, sensor_dict


def create_det_dict_plc(args, data, det_dict):
        
    data.set_sensors(data.all_sensors) 
    extract_obj = ExtractPlc(data.sensors, args.category, args.machinery)
    raw = extract_obj.get_raw_data()
    
    extracted_data = extract_obj.extract_raw_data()
    pre_data, det_sensors = extract_obj.preprocess_data(extracted_data)
    det_dict[args.category] = dict.fromkeys(det_sensors)
    for det in det_sensors:
        df_det = pre_data[det]
        det_dict[args.category][det] = {}
        vals = df_det[['value']].dropna()
        if det=='Alarm' or det=='OperationState':
            value = (float(vals.iloc[-2]), float(vals.iloc[-1]))
        else:
            value = (float(vals.iloc[0]),)
        det_dict[args.category][det]['value'] = value
    

    sensors_cpy = data.all_sensors.copy()
    sensor_dict = {key: pd.DataFrame(columns=['value']) for key in sensors_cpy}

    raw = raw.drop(columns=["_id", "day", "first_time", "last_time", "nsamples"])
    raw = raw[raw.variable!='RunningTime']
    raw = raw[raw.variable!='PowerOnTime']
    
    for sensor in sensors_cpy:
        # In this function we try to understand the relationship between deifferent heads
        # We delete the index, so we can join different heads, this is a prototype. 
        df_by_sensor = raw[raw.variable.str.contains(sensor)]
        df_all = pd.DataFrame(df_by_sensor.samples.sum())
        # df_all.value = df_all.value.map(lambda x: float(x[list(x.keys())[0]]))
        df_all.time = df_all.time.map(lambda x: float(x[list(x.keys())[0]]))
        df_all.index = df_all.set_index('time').index.astype(int)/1000
        sensor_dict[sensor] = df_all
                
    
    
    return det_dict, sensor_dict




def main():
    categories = ['eqtq', 'drive', 'plc']
    det_dict = dict.fromkeys(categories)
    sen_dict = dict.fromkeys(categories)

    
    args = InferArgs(category='eqtq')
    data = EQTQ(heads=args.heads, machinery=args.machinery)
    sen_dict['eqtq'] = dict.fromkeys(data.all_sensors)
    det_dict, sensor_dict_eqtq = create_det_dict(args, data, det_dict)
    for sensor in sensor_dict_eqtq.keys():
        value = sensor_dict_eqtq[sensor][[sensor_dict_eqtq[sensor].columns[0]]].dropna().values[0][0]
        dtype = type(value.item())
        sen_dict['eqtq'][sensor] = dtype
    
    
    args = InferArgs(category='drive')
    data = DRIVE(heads=args.heads, machinery=args.machinery)
    sen_dict['drive'] = dict.fromkeys(data.all_sensors)
    det_dict, sensor_dict_drive = create_det_dict(args, data, det_dict)
    for sensor in sensor_dict_drive.keys():
        value = sensor_dict_drive[sensor][[sensor_dict_drive[sensor].columns[0]]].dropna().values[0][0]
        dtype = type(value.item())
        sen_dict['drive'][sensor] = dtype
    
    
    args = InferArgs(category='plc')
    data = PLC(heads=args.heads, machinery=args.machinery)
    sen_dict['plc'] = dict.fromkeys(data.all_sensors)
    det_dict, sensor_dict_drive = create_det_dict_plc(args, data, det_dict)
    for sensor in sensor_dict_drive.keys():
        value = sensor_dict_drive[sensor][[sensor_dict_drive[sensor].columns[0]]].dropna().values[0][0]
        dtype = type(value.item())
        sen_dict['plc'][sensor] = dtype

    

    return det_dict, sen_dict
    
    
    
if __name__=="__main__":
    det, sen = main()
    if not os.path.isdir('./pickles'):
        os.mkdir('./pickles')
    
    with open('./pickles/det_sensors.pickle', 'wb') as handle:
        pickle.dump(det, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    with open('./pickles/type_sensors.pickle', 'wb') as handle:
        pickle.dump(sen, handle, protocol=pickle.HIGHEST_PROTOCOL)



    # path = "./checkpoints/JF890/drive/*/"
    # pattern = path + "*.ckpt"
    # result = glob.glob(pattern)
    
    # for res in result:
    #     if res.split('/')[-1].startswith('T'):
    #         continue
    #     else:
            
    #         new_name = 'T' + res.split('/')[-1]
            
    #         lst = res.split('/')[:-1]
    #         lst.append(new_name)
    #         os.rename(res, '/'.join(lst))
        
        
        

    # with open('filename.pickle', 'rb') as handle:
    #     b = pickle.load(handle)
    
    