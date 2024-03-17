# -*- coding: utf-8 -*-
import os
import warnings
import os, sys
import copy
import pickle
import pandas as pd
import logging

from modules.preprocessing import Extract
from modules.preprocessing import ExtractPlc
from modules.generators import Generate, GeneratePlc
from modules.trainer import Trainer
from modules.config import EQTQ, DRIVE, PLC, TrainArgs, InferArgs
import os
import contextlib
import logging
import random
from dataclasses import dataclass, field
from typing import Union, List
from bson.objectid import ObjectId
import pymongo
from modules.utils import *
from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.json_util import dumps

app = Flask(__name__)    
CORS(app)

mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/arol')
host = os.environ.get('HOST', 'localhost')
app.config['MONGO_URI'] = mongo_uri
mongo = PyMongo(app)




os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
warnings.filterwarnings("ignore")

with open('sample_plc.pickle', 'rb') as handle:
    metadata_plc = pickle.load(handle)
    
with open('sample.pickle', 'rb') as handle:
    metadata = pickle.load(handle)


    


metadata['sensor']['name'] = "AverageFriction"
gen = Generate(metadata)        
sample = gen.get_values()


db = create_db("JF890")
col = create_col(metadata['sensor'], db)
mongo.db.mydata['eqtq'].drop()
init_col('JF890', metadata['sensor'], mongo.db.mydata)
put_mongo(sample, metadata, mongo.db.mydata, '$numberDouble')


col = db['drive']
for m in mongo.db.mydata['eqtq'].find():
    print(m)
itm = mongo.db.mydata['eqtq'].find_one({'machinery_uid': 'JF890', 'folder': 'Head_01'})
with open(f"a.json", 'wb') as jsonfile:
    jsonfile.write(dumps(mongo.db.mydata['eqtq'].find(), indent=4, sort_keys=True).encode())
            






col = db['eqtq']
for m in col.find():
    print(m)



gen = GeneratePlc(metadata_plc)      
sample = gen.get_values()

db = create_db("JF890")
col = create_col(metadata_plc['sensor'], db)
init_col_plc(metadata_plc['sensor'], col)
put_mongo_plc(sample, metadata_plc, col)


col = db['plc']
for m in col.find():
    print(m)









metadata['sensor']['name'] = 'Index'
metadata['sensor']['category'] = 'drive'
db_heads = [f'H{i:>02}_' for i in gen.sensor['heads']]



encoder_data = gen.encoder_data[head]
encoder_data[head].std()


for i in range(10):
    print(gen.get_values()['Head_01'])


    
    
    
metadata_plc['sensor']['name'] = 'MainMotorSpeed'

gen = GeneratePlc(metadata_plc)      
  
values = gen.get_values()

for i in range(10):
    print(gen.get_values())






inf_args = InferArgs(heads=24, category='drive', sensor='board', machinery='JF890')
train_args = TrainArgs(target='Head_01')

data_obj = DRIVE(heads=inf_args.heads, machinery=inf_args.machinery)
data_obj.set_sensors(data_obj.all_sensors) 
data_obj.set_unk_variables()

extract_obj = extract(data_obj.sensors, inf_args.category, inf_args.machinery)
raw_df = extract_obj.get_raw_data()
extracted_data = extract_obj.extract_raw_data()
pre_data, det_sensors = extract_obj.preprocess_data(extracted_data)
filled_df = extract_obj.fill_data(extracted_data, det_sensors)

data_obj.load_data(filled_df)
train_data = data_obj.get_sensor(inf_args.sensor)


train_data = train_data[~train_data.index.duplicated(keep='first')]
for var in data_obj.unk_variables:
    train_data[var] = train_data[var].abs()


train_args.set_train_cutoff(train_data)
model = Trainer(
            learning_rate = train_args.learning_rate,
            epochs = train_args.epochs,
            batch_size = train_args.batch_size,
            )


model.create_dataloaders(
            train_data,
            train_args.training_cutoff,
            train_args.max_prediction_length,
            train_args.max_encoder_length,
            train_args.target,
            data_obj.unk_variables,
            train_args.group_ids
        )

model.load_model('/home/ahmadrezafrh/Desktop/SDP-Project-Group-19/q1_2_data_generation/python_server/checkpoints/JF890/drive/Head_01/board.ckpt')
encoder_data = train_data[lambda x: x.time_idx > x.time_idx.max() - train_args.max_encoder_length]

raw_prediction = model.predict(
    encoder_data,
    plot=False
)

print(encoder_data.shape)






