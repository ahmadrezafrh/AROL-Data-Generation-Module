from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from global_struct import Thread_struct
from train import train
import torch
import util
import simulation
import os
import time

app = Flask(__name__)    
CORS(app)

mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/arol')
host = os.environ.get('HOST', 'localhost')
app.config['MONGO_URI'] = mongo_uri
mongo = PyMongo(app)


@app.route('/generate/configuration', methods=['POST'])
def insert_configuration():
    try:
        data = request.json

        ret, msg = util.validate(data, 'configuration')
        if not ret:
            return jsonify(msg), 400
        
        result = mongo.db.configurations.insert_one(data)
        inserted_configuration = mongo.db.configurations.find_one({"_id": result.inserted_id})
        if inserted_configuration:
            inserted_configuration['_id'] = str(inserted_configuration['_id'])
            return jsonify({'message': 'Configuration saved', 
                        'configuration': inserted_configuration}), 200

    except Exception as e:
        print(f"Error while inserting configuration: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/generate/configuration/<string:name>', methods=['PUT'])
def update_configuration(name):
    try:
        print(name)
        if not name or not isinstance(name, str):
            return jsonify({'error': 'The name parameter must be provided as a valid string'}), 400
        
        data = request.json

        ret, msg = util.validate(data, 'machinery')
        if not ret:
            return jsonify(msg), 400

        update_result = mongo.db.configurations.update_one({"name": name}, {"$set": {"machineriesSelected": data['machineriesSelected']}})
        print(update_result)
        if update_result.matched_count > 0:
            if update_result.modified_count > 0:
                updated_configuration = mongo.db.configurations.find_one({"name": name})
                updated_configuration['_id'] = str(updated_configuration['_id'])
                return jsonify({'message': 'Update saved', 'configuration': updated_configuration}), 200
            else:
                return jsonify({'message': 'No changes to save'}), 204
        else:
            return jsonify({'error': 'Document not found'}), 404 


    except Exception as e:
        print(f"Error while updating configuration: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/generate/configurations/<string:name>', methods=['GET'])
def get_configuration(name):
    try:
        if not name or not isinstance(name, str):
            return jsonify({'error': 'The name parameter must be provided as a valid string'}), 400
           
        configuration = mongo.db.configurations.find_one({"name": name})
        if configuration:
            configuration['_id'] = str(configuration['_id'])
            return jsonify({'message': 'Configuration retrievd with success', 'configuration': configuration}), 200
        else:
            return jsonify({'error': 'Configuration not found'}), 404  
        
    except Exception as e:
        print(f"Error while retrieving configurations information: {e}")
        return jsonify({'error': 'Internal server error '}), 500


@app.route('/generate/configuration/names', methods=['GET'])
def get_configurationsNames():
    try:
        configurationsNames = []
        configurations = list(mongo.db.configurations.find())
        for config in configurations:
            configurationsNames.append(config['name'])

        return jsonify({'configurationsNames': configurationsNames}), 200
    except Exception as e:
        print(f"Error while retrieving configurations information: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    

@app.route('/generate/configuration/<string:name>', methods=['DELETE'])
def delete_configuration(name):
    try:
        if not name or not isinstance(name, str):
            return jsonify({'error': 'The name parameter must be provided as a valid string'}), 400
           
        result = mongo.db.configurations.delete_one({"name": name})
        if result.deleted_count:
            return jsonify({'message': 'Configuration deleted'}), 200
        else:
            return jsonify({'error': 'Configuration not found'}), 404

    except Exception as e:
        print(f"Error while deleting configuration: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/generate/model/status', methods=['GET'])
def status_model():
    try:
        if os.path.exists("./checkpoints"):
            return jsonify({'message': 'Model already trained', 'trained': True}), 200
        else:
            return jsonify({'message': 'Model not trained trained', 'trained': False }), 200
    except Exception as e:
        print(f"Error in training model request: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/generate/model/train', methods=['PUT'])
def train_model():
    try:
        train()
        return jsonify({'message': 'Model trained'}), 200
    except Exception as e:
        print(f"Error in training model request: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/generate/simulation/run', methods=['POST'])
def run_Simulation():
    try:
        data = request.json

        ret, msg = util.validate(data, 'machinery')

        if not ret:
            return jsonify(msg), 400

        machineries = data["machineriesSelected"] 

        # THREAD POOL
        Thread_struct.thread_pool_executor = simulation.initialize_thread_pool(sum(len(m["sensorsSelected"]) for m in machineries))

        simulation_time = simulation.run_action_pool(machineries, mongo)

        Thread_struct.thread_pool_executor.shutdown() # wait for all the task to be completed
        Thread_struct.stop_generation.clear()

        return jsonify({'message': 'generation of data of the configuration', 
                        'samples_generated': Thread_struct.num_samples_generated,
                        'faults_generated': Thread_struct.num_faults_generated,
                        'simulation_time': simulation_time,
                        }), 200
                        

    except Exception as e:
        print(f"Error while running a configuration {e}")
        return jsonify({'error': 'Internal server error'}), 505


@app.route('/generate/simulation/stop', methods=['PUT'])
def stop_simulation():
    try:
        if Thread_struct.thread_pool_executor is not None:
            Thread_struct.stop_generation.set()
            torch.cuda.empty_cache()

            return jsonify({'message': 'Simulation stopped'}), 200
        else:
            return jsonify({'message': 'No action to interrumpt'}), 204
        
    except Exception as e:
        print(f"Error while stopping simulation: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host=host, debug=True)
