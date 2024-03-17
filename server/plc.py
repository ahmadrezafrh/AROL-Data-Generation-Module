# -*- coding: utf-8 -*-

import os
import warnings
from modules.trainer import Trainer
from config import EQTQ, DRIVE, PLC, TrainArgs, PArgs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
warnings.filterwarnings("ignore")
import pandas as pd
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import warnings
import os
import copy
from modules.utils import create_dir





# inf_args = PArgs
# train_args = TrainArgs()
# data_obj = PLC(machinery=inf_args.machinery)
# data_obj.set_sensors(data_obj.all_sensors) 
# data_obj.set_unk_variables()

# extract_obj = ExtractPlc(data_obj.sensors, inf_args.category, inf_args.machinery)
# raw_df = extract_obj.get_raw_data()
# extracted_data = extract_obj.extract_raw_data()
# pre_data, det_sensors = extract_obj.preprocess_data(extracted_data)
# filled_df = extract_obj.fill_data(extracted_data, det_sensors)

# data_obj.load_data(filled_df)
