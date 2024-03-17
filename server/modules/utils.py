# -*- coding: utf-8 -*-

import os
import pandas as pd


def create_dir(path) -> None:
    if not os.path.exists(path):
       os.makedirs(path)
       
      
def create_dict(machinery, head, date):
    """
    This function creates an initial dictionary to be used to inserted in the
    DB.

    Args:
        machinery (str): extracted dataframe for a specific sensor.
        head (str): sensor head.
        date (int): date of initialization.

    Returns:
        dict: dcitionary of one head corresponding to it's category
    """
    head_dict = {
        "machinery_uid": machinery,
        "folder": head,
        "day": date.strftime('%a %b %d %Y'),
        "first_time": "",
        "last_time": "",
        "n_samples": 0,
        "samples": []
        }
    return head_dict

def create_dict_plc(machinery, variable, date):
    """
    This function creates an initial dictionary to be used to inserted in the
    DB.

    Args:
        machinery (str): extracted dataframe for a specific sensor.
        head (str): sensor head.
        date (int): date of initialization.

    Returns:
        dict: dcitionary of one head corresponding to it's category
    """
    var_dict = {
        "machinery_uid": machinery,
        "day": date.strftime('%a %b %d %Y'),
        "variable": variable,
        "first_time": "",
        "last_time": "",
        "n_samples": 0,
        "samples": []
        }
    return var_dict



def init_col(machinery, sensor, col):
    """
    Initializes the generation collection DB for further processing and adding
    new data.

    Args:
        machinery (pd.DataFrame): extracted dataframe for a specific sensor.
        sensor (str): sensor dictionary in metadata.
        col (flask_pymongo.wrappers.Collection): db collection to be used to put the data

    Returns:
        None
    """
    date = pd.Timestamp.now()
    heads = [f'Head_{i:>02}' for i in sensor['heads']]
    sensor['head_ids'] = {}
    for head in heads:
        itm = col[sensor['category']].find_one({'machinery_uid': machinery, 'folder': head})
        if itm:
            sensor['head_ids'][head] = itm.get('_id')
        else:
            head_dict = create_dict(machinery, head, date)
            x = col[sensor['category']].insert_one(head_dict)
            sensor['head_ids'][head] = x.inserted_id 


def init_col_plc(machinery, sensor, col):
    """
    Initializes the generation collection DB for further processing and adding
    new data.

    Args:
        machinery (pd.DataFrame): extracted dataframe for a specific sensor.
        sensor (dict): sensor dictionary in metadata.
        col (flask_pymongo.wrappers.Collection): db collection to be used to put the data

    Returns:
        None
    """
    date = pd.Timestamp.now()
    var_dict = create_dict_plc(machinery, sensor['name'], date)
    x = col[sensor['category']].insert_one(var_dict)
    sensor['id'] = x.inserted_id 



def put_mongo(sample, metadata, col):
    """
    This function is used to put the data in the db collection. For each category
    and each available heads we have tu put it in the category collection. 

    Args:
        sample (dict): dictionary of the generated samples (one sample for each head).
        metadata (dict): metadata in each action_pool in the simulation.
        col (flask_pymongo.wrappers.Collection): db collection to be used to put the data

    Returns:
        None
    """
    heads = [f'Head_{i:>02}' for i in metadata['sensor']['heads']]
    db_heads = [f'H{i:>02}_' for i in metadata['sensor']['heads']]
    for c, head in enumerate(heads):
        x = metadata['sensor']['head_ids'][head]
        date = int(sample[head].name.timestamp() * 1000)
        name = db_heads[c] + metadata['sensor']['name']
        col[metadata['sensor']['category']].update_one(
            filter = {'_id': x},
            update = {
                 '$push': {'samples': {'name': name, 'value': round(sample[head][head].item(), 3), 'time': date}},
                 "$set": { "last_time": date},
                 '$inc': {'n_samples': 1}
            })
        
        col[metadata['sensor']['category']].update_one(
            filter = {'$and': [{'_id': x}, {'first_time': {"$eq":""}}]},
            update = {"$set" : {"first_time" : date}},
        )
        
        
def put_mongo_plc(sample, metadata, col):
    """
    This function is used to put the data in the db collection. For each category
    and each available heads we have tu put it in the category collection. 

    Args:
        sample (dict): dictionary of the generated samples (one sample for each head).
        metadata (dict): metadata in each action_pool in the simulation.
        col (flask_pymongo.wrappers.Collection): db collection to be used to put the data

    Returns:
        None
    """
    x = metadata['sensor']['id']
    date = int(sample.name.timestamp() * 1000)
    col['plc'].update_one(
        filter = {'_id': x},
        update = {
             '$push': {'samples': {'value': round(sample['value'].item(), 3), 'time':date}},
             "$set": { "last_time": date},
             '$inc': {'n_samples': 1}
        })
    
    col['plc'].update_one(
        filter = {'$and': [{'_id': x}, {'first_time': {"$eq":""}}]},
        update = {"$set" : {"first_time" : date}},
    )        