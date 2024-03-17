# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Union

def sensor_check(all_sensors: list, sensor: Union[str, list]) -> bool:
    """Returns True if all_sensors contains all elements of sensor list, False otherwise."""  
    if isinstance(sensor, str): return sensor in all_sensors
    sit = [element in all_sensors for element in sensor]
    return sum(sit)==len(sensor)


@dataclass
class TrainArgs:
    max_prediction_length: int = 5
    n_process: int = 3
    max_encoder_length: int = 10
    learning_rate: float = 0.09
    epochs: int = 1
    batch_size: int = 32
    clipping: float = 0.1
    accelerator: str = "cuda"
    devices: str = "auto"
    model_summary: bool = False
    min_delta: float = 1e-4
    patience: int = 10
    verbose: bool = False
    early_mode: str = "min"
    hidden_size: int = 8
    hidden_continuous_size: int = 8
    attention_head_size: int = 8
    dropout: float = 0.1
    target: list = field(default_factory=lambda: ['Head_01'])
    group_ids: list = field(default_factory=lambda: ["day"])
    path: str = None
    lr_tuning: str = True
    logs_dir: str = "./logs"
    checkpoints_dir: str = "./checkpoints"
    
            
    def set_train_cutoff(self, train_data):
        self.training_cutoff = train_data['time_idx'].max() - self.max_prediction_length
        
@dataclass
class InferArgs:
    heads: int = 24
    lr_tuning: bool = True
    sensor: str = 'LockDegree'
    category: str = 'eqtq'
    machinery: str = 'ejda1'



@dataclass
class BaseSensorData:
    machinery: str = None
    heads: int = None
    sensors: list = field(default_factory=list)

    
    def set_heads(self, heads: int) -> None:
        assert isinstance(heads, int), "Heads should be integer"
        assert ((heads>24) & (heads<1)), "Heads should be an integer between 1 to 24"
        self.heads = len(heads)
    
    def set_sensors(self, sensors: list) -> None:
        assert isinstance(sensors, list), "Sensors should be a list"
        assert sensor_check(self.all_sensors, sensors)
        self.sensors = sensors
        
    def add_sensor(self, sensor: str) -> None:
        assert isinstance(sensor, str), "Sensor should be string"
        assert sensor_check(self.all_sensors, sensor)
        if sensor not in self.sensors:
            self.sensors.append(sensor)
        
    def remove_sensor(self, sensor: str) -> None:
        assert isinstance(sensor, str), "Sensor should be string"
        assert sensor_check(self.sensors, sensor)
        if sensor in self.sensors:
            self.sensors.remove(sensor)

    def load_data(self, dataframe):
        self.dataframe = dataframe
    
    def get_sensor(self, sensor):
        self.data = self.dataframe[sensor][self.unk_variables]
        self.data = self.data[~self.data.index.duplicated(keep='first')]
        self.data['day'] = self.data.index.day.astype(str).astype("category")
        self.data["time_idx"] = self.data.reset_index().drop(columns=['index']).index
        return self.data

    def set_unk_variables(self):
        self.unk_variables = [f'Head_{i+1:>02}' for i in range(self.heads)]



@dataclass
class EQTQ(BaseSensorData):
    all_sensors: list = field(default_factory=lambda: ['LockDegree', 'Index', 
                    'stsClosureOK', 'stsNoLoad', 
                    'MaxLockPosition','stsBadClosure',
                    'AverageTorque', 'stsTotalCount',
                    'MinLockPosition', 'stsNoClosure', 'AverageFriction'])
    
@dataclass
class PLC(BaseSensorData):
    all_sensors: list = field(default_factory=lambda: ['OperationMode', 'Alarm', 
                    'OperationState', 'MainMotorSpeed', 
                    'MainMotorCurrent','HeadMotorSpeed',
                    'HeadMotorCurrent', 'ProdSpeed',
                    'PowerVoltage', 'PowerCurrent', 'AirConsumption',
                    'LubeLevel', 'test1', 'test2', 'test3', 'TotalProduct'])
    
    def set_unk_variables(self):
        self.unk_variables = ['value']
    
    def get_sensor(self, sensor):
        self.data = self.dataframe[sensor][self.unk_variables]
        self.data = self.data[~self.data.index.duplicated(keep='first')]
        self.data['day'] = self.data.index.day.astype(str).astype("category")
        self.data["time_idx"] = self.data.reset_index().index
        return self.data
        
    
@dataclass
class DRIVE(BaseSensorData):
    all_sensors: list = field(default_factory=lambda: ['Tcpu','Twindings','Tboard','Tplate'])




    
