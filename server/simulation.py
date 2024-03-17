import os
import random
import logging
import time
import contextlib
import shutil
import json
from bson.json_util import dumps
from concurrent.futures import ThreadPoolExecutor
from global_struct import Thread_struct
from modules.utils import put_mongo, init_col, init_col_plc, put_mongo_plc
from modules.generators import Generate, GeneratePlc

logging.basicConfig(format='%(message)s', level=logging.INFO)

def initialize_thread_pool(workers):
    # We limit the number of threads in the pool to the number logic threads of the cpu
    if workers > os.cpu_count() - 1:
        workers = os.cpu_count() - 1 
    return ThreadPoolExecutor(max_workers=workers)


def run_action_sensor(sensor_data):
    try:
        generator = sensor_data['sensor']['gen']
        fault = sensor_data['fault']

        if fault:   
            sample = generator.gen_fault()
            
            if sensor_data['sensor']['category'] == 'plc':
                put_mongo_plc(sample, sensor_data, Thread_struct.mongo.db)
                with Thread_struct.lock:
                    Thread_struct.num_faults_generated +=1
                logging.info(f"FAULT --> {sensor_data['machinery_uid']} - {sensor_data['sensor']['category']} - {sensor_data['sensor']['name']} - {round(sample.value, 3)} - {sample.name}")
            else:
                put_mongo(sample, sensor_data, Thread_struct.mongo.db)
                heads = [f'Head_{i:>02}' for i in sensor_data['sensor']['heads']]
                with Thread_struct.lock:
                    Thread_struct.num_faults_generated += len(heads)
                for head in heads:
                    logging.info(f"FAULT --> {sensor_data['machinery_uid']} - {sensor_data['sensor']['category']} - {sensor_data['sensor']['name']} - {head} - {round(sample[head][head],3)} - {sample[head].name}")
        else: 
            
            sample = generator.get_values()
            
            if sensor_data['sensor']['category'] == 'plc':
                put_mongo_plc(sample, sensor_data, Thread_struct.mongo.db)
                with Thread_struct.lock:
                    Thread_struct.num_samples_generated += 1
                logging.info(f"DATA --> {sensor_data['machinery_uid']} - {sensor_data['sensor']['category']} - {sensor_data['sensor']['name']} - {round(sample.value,3)} - {sample.name}")
            else:
                put_mongo(sample, sensor_data, Thread_struct.mongo.db)
                heads = [f'Head_{i:>02}' for i in sensor_data['sensor']['heads']]
                with Thread_struct.lock:
                    Thread_struct.num_samples_generated += len(heads)
                for head in heads:
                    logging.info(f"DATA --> {sensor_data['machinery_uid']} - {sensor_data['sensor']['category']} - {sensor_data['sensor']['name']} - {head} - {round(sample[head][head],3)} - {sample[head].name}")

    except Exception as e:
        print(f"An error occurred: {e}")

def run_action_pool(machineries, mongo, dirpath='./generated_data'):
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
    os.mkdir(dirpath)
    mongo.db['eqtq'].drop()
    mongo.db['drive'].drop()
    mongo.db['plc'].drop()
    
    simulation_time = 0
    Thread_struct.num_samples_generated = 0
    Thread_struct.num_faults_generated = 0

    cats = []
    machineryFault = dict()
    for machinery in machineries:
        machineryFault[machinery['uid']] = 0
        for sensor in machinery["sensorsSelected"]:
            cats.append(sensor['category'])
            sensor_data = {"machinery_uid": machinery['uid'], "sensor": sensor}
            if sensor['category']=='plc':
                with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
                    gen_object = GeneratePlc(sensor_data)
            else:
                with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
                    gen_object = Generate(sensor_data)
            sensor['gen'] = gen_object
            
            if sensor['category']=='plc':
                init_col_plc(machinery['uid'], sensor, mongo.db)
            else:
                init_col(machinery['uid'], sensor, mongo.db)

    Thread_struct.mongo = mongo
    time.sleep(1)      
    while not Thread_struct.stop_generation.is_set():
        simulation_time += 1
        logging.info(f"{simulation_time}...")

        for machinery in machineries:
            if simulation_time % machinery["faultFrequency"] == 0:
                prob = random.randint(1, 100)
                if prob <= machinery["faultProbability"]:
                    machineryFault[machinery['uid']] = 1

            shuffled_sensor = machinery["sensorsSelected"]
            random.shuffle(shuffled_sensor)
            for sensor in shuffled_sensor:
                if simulation_time % sensor["dataFrequency"] == 0:
                    fault = machineryFault[machinery['uid']]
                    sensor_data = {"machinery_uid": machinery['uid'], "sensor": sensor, "fault" : fault}
                    if machineryFault[machinery['uid']] == 1:
                        machineryFault[machinery['uid']] = 0
                    Thread_struct.thread_pool_executor.submit(run_action_sensor, sensor_data)
            
        time.sleep(1)

    for col in set(cats):
        with open(f"{dirpath}/MongoData{col.upper()}.json", 'wb') as jsonfile:
            jsonfile.write(dumps(mongo.db[col].find(), indent=2, sort_keys=True).encode())
    
    #os.system("mongodump --db arol -o generated_data")
    for col in set(cats):
        shutil.move(f"{dirpath}/arol/{col}.bson", f"{dirpath}/MongoData{col.upper()}.bson")
        
    shutil.rmtree(f"{dirpath}/arol")
    logging.info('The simulation has been interrupted')
    return simulation_time
