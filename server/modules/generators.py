# -*- coding: utf-8 -*-

import os
import sys
import copy
import pickle
import pandas as pd
import logging
import contextlib
import random

from modules.preprocessing import ExtractPlc
from modules.preprocessing import Extract
from modules.trainer import Trainer
from modules.config import EQTQ, DRIVE, PLC, TrainArgs, InferArgs

class Generate:
    """
    This class have been designed to for generating artificial samples. In each
    method we generate a fault or a real sample. For the generation we need to
    use available dataset.
    
    
    Methods:
        predict():
            Predicting the future correct samples.
        get_type():
            Type of original values (int pr float)
        get_values():
            get predicted values.
        gen_fault():
            get fault samples with a specific algorithm.
    """
    def __init__(
        self,
        metadata,
        type_pickle: str = './pickles/type_sensors.pickle',
        det_pickle: str = './pickles/det_sensors.pickle',
    ):
        """
        Initialize a new instance of Generate.
        
        Args:
            metadata (dict): dictionary of the sensors metadata
            type_pickle (str): type of sensors generated from det.py
            det_pickle (str): deterministic sensors generated from det.py
            device (str): which device we should use for prediction
        """
        
        self.metadata = metadata
        with open(type_pickle, 'rb') as handle:
            self.sen = pickle.load(handle)   
        with open(det_pickle, 'rb') as handle:
            self.det = pickle.load(handle)
                    
        self.sensor = metadata['sensor']
        self.inf_args = InferArgs(category=self.sensor['category'], sensor=self.sensor['name'], machinery=metadata['machinery_uid'])
        self.train_args = TrainArgs(target='Head_01')
        self.device = self.train_args.accelerator
        self.heads = [f'Head_{i:>02}' for i in self.sensor['heads']]
        if self.sensor['name'] in self.det[self.sensor['category']].keys():
            self.det_sensor = True
        else:
            self.det_sensor = False
        self._set_sensor(self.inf_args.category)
        self._set_train_data()
        self._set_first_encoder_data()
        self.count = 0
        if not self.det_sensor:
            self._set_model()
            
        
        
        
    def _set_sensor(
        self,
        category,        
    ):
        if category=='drive':
            self.data_obj = DRIVE(heads=self.inf_args.heads, machinery=self.inf_args.machinery)
        elif category=='eqtq':
            self.data_obj = EQTQ(heads=self.inf_args.heads, machinery=self.inf_args.machinery)

        self.data_obj.set_sensors(self.data_obj.all_sensors) 
        self.data_obj.set_unk_variables()


    def _set_train_data(
            
          self,
          
    ):
        extract_obj = Extract(self.data_obj.sensors, self.inf_args.category, self.inf_args.machinery)
        _ = extract_obj.get_raw_data()
        extracted_data = extract_obj.extract_raw_data()
        pre_data, self.det_sensors = extract_obj.preprocess_data(extracted_data)
        filled_df = extract_obj.fill_data(extracted_data, self.det_sensors)

        self.data_obj.load_data(filled_df)
        self.train_data = self.data_obj.get_sensor(self.inf_args.sensor)
        self.train_data = self.train_data[~self.train_data.index.duplicated(keep='first')]
        if not self.det_sensor:
            for var in self.heads:
                self.train_data[var] = self.train_data[var].abs()
            self.train_args.set_train_cutoff(self.train_data)


    def _set_model(
        self
    ):
        self.model_heads = {}
        for head in self.heads:
            self.model = Trainer(device=self.device)
            self.model.load_model(f'./checkpoints/{self.inf_args.machinery}/{self.inf_args.category}/{head}/{self.inf_args.sensor}.ckpt')
            self.model_heads[head] = copy.deepcopy(self.model)
            
        
    def _set_first_encoder_data(
        self,
    ):
        self.encoder_data = {}
        for head in self.heads:
            self.encoder_data[head] = self.train_data[lambda x: x.time_idx > x.time_idx.max() - self.train_args.max_encoder_length][['time_idx',head,'day']]
        
        self._date_idx = self.encoder_data[head].index[-1]
        self._day = self._date_idx.day
        self._new_date = self._date_idx + pd.Timedelta(days=1)
        self._new_time_idx = self.encoder_data[head][['time_idx']].values[-1]  + 1
        
        
    def _update_encoder_input(
          self      
    ): 
        
        for head in self.heads:
            copy_date = copy.deepcopy(self._new_date)
            copy_idx = copy.deepcopy(self._new_time_idx)
            for i in range(self.train_args.max_prediction_length):
                row = pd.DataFrame([{'time_idx':int(copy_idx[0]), head:float(self.pred_heads[head][i]),'day':str(self._day)}],index=[copy_date], columns=self.encoder_data[head].columns)
                row.day = row.day.astype('category')
                self.encoder_data[head] = self.encoder_data[head].append(row)
                copy_date = copy_date + pd.Timedelta(seconds=1)
                copy_idx += 1
                

        self._new_date = self._new_date + pd.Timedelta(seconds=self.train_args.max_prediction_length)
        self._new_time_idx = self._new_time_idx + self.train_args.max_prediction_length
        for head in self.heads:
            self.encoder_data[head] = self.encoder_data[head][lambda x: x.time_idx > x.time_idx.max() - self.train_args.max_encoder_length][['time_idx',head,'day']]
            self.encoder_data[head].day = self.encoder_data[head].day.astype('category')
            if self.sen[self.inf_args.category][self.inf_args.sensor]==int:
                self.encoder_data[head][head] = self.encoder_data[head][head].round(0)
            
        
    def predict(
        self,        
    ):
        """
        This predicts new samples
        """
        logging.disable(sys.maxsize)
        self.pred_heads = {}
        if not self.det_sensor:
            for head in self.heads:
                with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
                    raw_prediction = self.model_heads[head].predict(
                        self.encoder_data[head],
                        plot=False
                    )
                    
                self.pred_heads[head] = raw_prediction.output.prediction[:,3,1:6].squeeze(0).squeeze(0)
            self._update_encoder_input()
        
        else:
            for head in self.heads:
                copy_date = copy.deepcopy(self._new_date)
                copy_idx = copy.deepcopy(self._new_time_idx)
                for i in range(self.train_args.max_prediction_length):
                    row = pd.DataFrame([{'time_idx':int(copy_idx[0]), head:float(self.det[self.sensor['category']][self.sensor['name']][head]),'day':str(self._day)}],index=[copy_date], columns=self.encoder_data[head].columns)
                    row.day = row.day.astype('category')
                    self.encoder_data[head] = self.encoder_data[head].append(row)
                    copy_date = copy_date + pd.Timedelta(seconds=1)
                    copy_idx = copy_idx + 1
                    
            self._new_date = self._new_date + pd.Timedelta(seconds=self.train_args.max_prediction_length)
            self._new_time_idx = self._new_time_idx + self.train_args.max_prediction_length
            for head in self.heads:
                self.encoder_data[head] = self.encoder_data[head][lambda x: x.time_idx > x.time_idx.max() - self.train_args.max_encoder_length][['time_idx',head,'day']]
                self.encoder_data[head].day = self.encoder_data[head].day.astype('category')
                if self.sen[self.inf_args.category][self.inf_args.sensor]==int:
                    self.encoder_data[head][head] = self.encoder_data[head][head].round(0)
                    
        logging.disable(logging.NOTSET) 
        self.count = copy.deepcopy(self.train_args.max_prediction_length)
                
    
    def get_type(self):
        """
        Returns:
            str: whether int or float
        """
        return self.sen[self.inf_args.category][self.inf_args.sensor]
    
    def get_values(
         self
    ):
        """
        Returns:
            dict: dictionary of predicted values
        """
        if self.count<=0:
            self.predict()
            
        values = {}
        now = pd.Timestamp.now()
        for head in self.heads:
            values[head] = self.encoder_data[head].iloc[-self.count]
            if self.sensor['name']=='AverageFriction':
                values[head][head] = -values[head][head]
            values[head].name = now
            if self.sen[self.inf_args.category][self.inf_args.sensor]==int:
                values[head][head] = values[head][head].astype("int")
        self.count -= 1
        return values
    
    def gen_fault(
        self,
        std_param=3,
        bias_percent=0.1
    ):
        """
        Args:
            std_param (int): Coefficient for generating fault.
            bias_percent (float): bias for calculating the fault sample.
        
        Returns:
            dict: dictionary of predicted fault values.
        """

        values = {}
        now = pd.Timestamp.now()
        for head in self.heads:
            values[head] = self.encoder_data[head].iloc[-1]
            if not self.det_sensor:
                std = self.encoder_data[head][head].std()
                if std==0:
                    values[head][head] = values[head][head] + bias_percent*values[head][head]
                else:
                    values[head][head] = values[head][head] + std*(std_param+random.uniform(0,1))
                
                if self.sen[self.inf_args.category][self.inf_args.sensor]==int:
                    values[head][head] = values[head][head].round(0)
                    
            values[head].name = now
            if self.sensor['name']=='AverageFriction':
                values[head][head] = -values[head][head]
            if self.sen[self.inf_args.category][self.inf_args.sensor]==int:
                values[head][head] = values[head][head].astype("int")

        return values
    
    
    
class GeneratePlc:
    """
    This class have been designed to for generating artificial samples. In each
    method we generate a fault or a real sample. For the generation we need to
    use available dataset.
    
    
    Methods:
        predict():
            Predicting the future correct samples.
        get_type():
            Type of original values (int pr float)
        get_values():
            get predicted values.
        gen_fault():
            get fault samples with a specific algorithm.
    """
    def __init__(
        self,
        metadata,
        type_pickle: str = './pickles/type_sensors.pickle',
        det_pickle: str = './pickles/det_sensors.pickle',
    ):
        """
        Initialize a new instance of Generate.
        
        Args:
            metadata (dict): dictionary of the sensors metadata
            type_pickle (str): type of sensors generated from det.py
            det_pickle (str): deterministic sensors generated from det.py
            device (str): which device we should use for prediction
        """
        self.metadata = metadata
        with open(type_pickle, 'rb') as handle:
            self.sen = pickle.load(handle)   
        with open(det_pickle, 'rb') as handle:
            self.det = pickle.load(handle)
                    
        self.sensor = metadata['sensor']
        self.inf_args = InferArgs(category=self.sensor['category'], sensor=self.sensor['name'], machinery=metadata['machinery_uid'])
        self.train_args = TrainArgs(target='value')
        self.device = self.train_args.accelerator
        if self.sensor['name'] in self.det[self.sensor['category']].keys():
            self.det_sensor = True
        else:
            self.det_sensor = False
            
        self._set_sensor(self.inf_args.category)
        self._set_train_data()
        self._set_first_encoder_data()
        self.count = 0
        self.det_count = 0
        if not self.det_sensor:
            self._set_model()
            
        
        
        
    def _set_sensor(
        self,
        category,        
    ):
        self.data_obj = PLC(heads=1, machinery=self.inf_args.machinery)
        self.data_obj.set_sensors(self.data_obj.all_sensors) 
        self.data_obj.set_unk_variables()


    def _set_train_data(
            
          self,
          
    ):
        extract_obj = ExtractPlc(self.data_obj.sensors, self.inf_args.category, self.inf_args.machinery)
        _ = extract_obj.get_raw_data()
        extracted_data = extract_obj.extract_raw_data()
        pre_data, self.det_sensors = extract_obj.preprocess_data(extracted_data)
        filled_df = extract_obj.fill_data(extracted_data, self.det_sensors)

        self.data_obj.load_data(filled_df)
        self.train_data = self.data_obj.get_sensor(self.inf_args.sensor)
        self.train_data = self.train_data[~self.train_data.index.duplicated(keep='first')]
        if not self.det_sensor:
            self.train_data['value'] = self.train_data['value'].abs()
            self.train_args.set_train_cutoff(self.train_data)


    def _set_model(
        self
    ):
        self.model = Trainer(device = self.device)
        self.model.load_model(f'./checkpoints/{self.inf_args.machinery}/{self.inf_args.category}/value/{self.inf_args.sensor}.ckpt')
            
        
    def _set_first_encoder_data(
        self,
    ):
        
        self.encoder_data = self.train_data[lambda x: x.time_idx > x.time_idx.max() - self.train_args.max_encoder_length][['time_idx','value','day']]
        
        self._date_idx = self.encoder_data.index[-1]
        self._day = self._date_idx.day
        self._new_date = self._date_idx + pd.Timedelta(days=1)
        self._new_time_idx = self.encoder_data[['time_idx']].values[-1]  + 1
        
        
    def _update_encoder_input(
          self      
    ): 
        
        copy_date = copy.deepcopy(self._new_date)
        copy_idx = copy.deepcopy(self._new_time_idx)
        for i in range(self.train_args.max_prediction_length):
            row = pd.DataFrame([{'time_idx':int(copy_idx[0]), "value":float(self.pred[i]),'day':str(self._day)}],index=[copy_date], columns=self.encoder_data.columns)
            row.day = row.day.astype('category')
            self.encoder_data = self.encoder_data.append(row)
            copy_date = copy_date + pd.Timedelta(seconds=1)
            copy_idx += 1
                

        self._new_date = self._new_date + pd.Timedelta(seconds=self.train_args.max_prediction_length)
        self._new_time_idx = self._new_time_idx + self.train_args.max_prediction_length
        
        self.encoder_data = self.encoder_data[lambda x: x.time_idx > x.time_idx.max() - self.train_args.max_encoder_length][['time_idx','value','day']]
        self.encoder_data.day = self.encoder_data.day.astype('category')
        if self.sen[self.inf_args.category][self.inf_args.sensor]==int:
            self.encoder_data['value'] = self.encoder_data['value'].round(0)
            
        
    def predict(
        self,        
    ):
        logging.disable(sys.maxsize)
        self.pred = {}
        if not self.det_sensor:
            with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
                raw_prediction = self.model.predict(
                    self.encoder_data,
                    plot=False
                )
            self.pred = raw_prediction.output.prediction[:,3,1:6].squeeze(0).squeeze(0)
            self._update_encoder_input()
        
        else:
            copy_date = copy.deepcopy(self._new_date)
            copy_idx = copy.deepcopy(self._new_time_idx)
            self.total_product = None
            for i in range(self.train_args.max_prediction_length):
                if len(self.det[self.sensor['category']][self.sensor['name']]['value'])==1:
                    if self.sensor['name']=='TotalProduct':
                        if self.total_product:
                            self.total_product += 10
                        else:
                            self.total_product = self.det[self.sensor['category']][self.sensor['name']]['value'][0]
                            self.total_product += 10
                        value = copy.deepcopy(self.total_product)
                    else:
                        value = self.det[self.sensor['category']][self.sensor['name']]['value'][0]
                else:
                    value = self.det[self.sensor['category']][self.sensor['name']]['value'][self.det_count]
                    self.det_count+=1
                    if self.det_count==len(self.det[self.sensor['category']][self.sensor['name']]['value']):
                        self.det_count = 0
                        
                row = pd.DataFrame([{'time_idx':int(copy_idx[0]), 'value':float(value),'day':str(self._day)}],index=[copy_date], columns=self.encoder_data.columns)
                row.day = row.day.astype('category')
                self.encoder_data = self.encoder_data.append(row)
                copy_date = copy_date + pd.Timedelta(seconds=1)
                copy_idx = self.encoder_data[['time_idx']].values[-1]  + 1
                    
            self._new_date = self._new_date + pd.Timedelta(seconds=self.train_args.max_prediction_length)
            self._new_time_idx = self._new_time_idx + self.train_args.max_prediction_length
            self.encoder_data = self.encoder_data[lambda x: x.time_idx > x.time_idx.max() - self.train_args.max_encoder_length][['time_idx','value','day']]
            self.encoder_data.day = self.encoder_data.day.astype('category')
            if self.sen[self.inf_args.category][self.inf_args.sensor]==int:
                self.encoder_data['value'] = self.encoder_data['value'].round(0)
                    
        logging.disable(logging.NOTSET) 
        self.count = copy.deepcopy(self.train_args.max_prediction_length)
                
    
    def get_type(self):
        """
        Returns:
            dict: dictionary of predicted values
        """
        return self.sen[self.inf_args.category][self.inf_args.sensor]
    
    def get_values(
         self
    ):
        """
        Returns:
            dict: dictionary of predicted values
        """
        
        if self.count==0:
            self.predict()
            
        value = self.encoder_data.iloc[-self.count]
        value.name = pd.Timestamp.now() 
        if self.sen[self.inf_args.category][self.inf_args.sensor]==int:
            value['value'] = value['value'].astype("int")
        self.count -= 1
        return value

    def gen_fault(
        self,
        std_param=3,
        bias_percent=0.1
    ):
        """
        Args:
            std_param (int): Coefficient for generating fault.
            bias_percent (float): bias for calculating the fault sample.
        
        Returns:
            dict: dictionary of predicted fault values.
        """
        
        value = self.encoder_data.iloc[-1]
        if not self.det_sensor:
            std = self.encoder_data['value'].std()
            if std==0:
                value['value'] = value['value'] + bias_percent*value['value']
            else:
                value['value'] = value['value'] + std*(std_param+random.uniform(0,1))
            
        if self.sen[self.inf_args.category][self.inf_args.sensor]==int:
            value['value'] = value['value'].astype("int")
            
        value.name = pd.Timestamp.now()  
        return value