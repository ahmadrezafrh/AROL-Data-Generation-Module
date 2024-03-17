# -*- coding: utf-8 -*-

import pandas as pd
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import warnings
import os
import json
import copy
warnings.filterwarnings("ignore")


class Extract:
    """
    This class have been designed to extract and transform raw data
    into a new space for future analysis.
    
    
    Methods:
        get_raw_data():
            This method extracts raw data from MongoD json files available in ./data folder.
        extract_raw_data():
            This is the first step to get the data based on heads and different sensors.
        preprocess_data(extr_df):
            Preprocesses the data to from original timestamps.
        fill_data(df, det_sensors):
            Fill the NaN values in the DataFrame.
    """
    def __init__(
            self,
            sensors: list,
            category: str,
            machinery: str,
            show_fig: bool =False,
            save_fig: bool = True,
            figs_dir: str ='./figs',
            plt_style: str = 'Solarize_Light2',
            data_path: str = './data',
            verbose: bool = True
            ):

        """
        Initialize a new instance of Extract.
        
        Args:
            sensors (list): list of all sensors we want to analyze
            category (str): name of category ['eqtq', 'drive']
            machinery (str): name of machinery
            show_fig (bool): whether to show the figs while extracting
            save_fig (bool): whether to save the figs while extracting
            figs_dir (str): figs directory.
            plt_style (str): plot styles.
            data_path (str): original data path of the sensors.
            verbose (bool): whether to print any information regarding extraction.
        """
        self.verbose = verbose
        self.figs_dir = figs_dir
        self.sensors = sensors.copy()
        self.machinery = machinery
        self.category = category
        self.category_path = os.path.join(data_path, 'MongoData' + category.upper() +'.json')
        self.raw_data = None
        self.verbose = verbose
        if show_fig: self._set_plt_style(plt_style)
        
    def _set_plt_style(self, plt_style):
        plt.style.use(plt_style)
        
    
    def _set_sensors_dict(self):
        self.sensor_dict = {key: pd.DataFrame(columns=self.raw_data.folder.unique()) for key in self.sensors}
        
    def _set_data(self):
        
        with open(self.category_path, 'r') as datafile:
            data = json.load(datafile)
        self.raw_data = pd.DataFrame(data)
        if self.verbose:
            print(f'\n{self.raw_data.folder.unique().shape[0]} heads and {len(self.sensors)} sensors detected in "{self.category}" sensor category.')

    def get_raw_data(self):
        """
        Returns:
            pd.DataFrame: first dataframe object of the sensors data
        """
        if self.raw_data is None:
            self._set_data()
        return self.raw_data
        
    def extract_raw_data(self):
        """
        Returns:
            dict: a dictionary containing all heads as values and sensors and keys
        """
        
        self._set_sensors_dict()
        sensors_cpy = self.sensors.copy()
        if self.verbose:
            print('Extracting raw data.')
    
        for head in self.raw_data.folder.unique():
            df_head = pd.DataFrame(self.raw_data[self.raw_data.folder==head].samples.sum())
            df_head = df_head.dropna()
            # df_head.value = df_head.value.map(lambda x: float(x[list(x.keys())[0]]))
            # We need to correct the timestamps
            df_head.time = df_head.time.map(lambda x: int(x[list(x.keys())[0]]))
            df_head.index = df_head.set_index('time').index.astype(int)/1000

            df_head = df_head.drop_duplicates()
            for sensor in sensors_cpy:
                # In this function we try to understand the relationship between deifferent heads
                # We delete the index, so we can join different heads, this is a prototype. 
                df_by_sensor = df_head[df_head.name.str.contains(sensor)]
                ins_df = pd.concat([self.sensor_dict[sensor], df_by_sensor.value.rename(head).to_frame()])
                self.sensor_dict[sensor] = ins_df
                
        for sensor in sensors_cpy:     
            self.sensor_dict[sensor] = self.sensor_dict[sensor].dropna(axis='columns', how='all').sort_index().rename(index={'time':'date'})
            self.sensor_dict[sensor].index = pd.to_datetime(self.sensor_dict[sensor].index, unit='s')
                
        return self.sensor_dict
    
    
    
    def preprocess_data(self, extr_df):
        """
        Args:
            extr_df (dict): a dictionary containing all heads as values and sensors and keys.
        
        Returns:
            tuple[dict, list]: A new dictionary of the preprocessed sensors
                               and deterministic sensors.
        """
        deterministic_sensor = []
        new_df = extr_df
        for sensor in self.sensors:
            # We group the data for each sensor based on the days
            results = [group[1] for group in new_df[sensor].groupby(new_df[sensor].index.date)]
            # result[2].interpolate(method='linear').plot(legend=False)
            tot_var = 0
            new_results = []
            for result in results:
                # We remove results that do not have sufficent variance in their heads. We catogorize them as deterministic sensors
                tot_var += result.var().sum()
                if result.var().sum() > 1e-1: new_results.append(result)
            
            if len(new_results)==0:
                if self.verbose:
                    print(f'Sensor {sensor} has total variance of {tot_var} and is deterministic.')
                deterministic_sensor.append(sensor)
                continue
            new_df[sensor] = pd.concat(new_results)
        return new_df, deterministic_sensor
    
    def _split_sensors(self, df, deterministic_sensor):
        _ = [df.pop(k, None) for k in deterministic_sensor]
        new_sesnors = [sensor for sensor in self.sensors if sensor not in deterministic_sensor]
        return new_sesnors
        
    
    def fill_data(self, df, det_sensors): 
        """
        Args:
            extr_df (dict): a dictionary containing all heads as values and sensors and keys.
        
        Returns:
            tuple[dict, list]: A new dictionary of the preprocessed sensors
                               and deterministic sensors.
        """
        filled = copy.deepcopy(df)
        for sensor in self.sensors:
            filled[sensor] = df[sensor].interpolate(method='linear').dropna(axis=0)
            filled[sensor] = filled[sensor].query('~index.duplicated()')
            
        if self.verbose:
            print('NaN values have been filled.')
        return filled
    
        

class ExtractPlc:
    """
    This class have been designed to extract and transform raw data
    into a new space for future analysis. It is specifcally designed
    for the plc sensor category.
    
    
    Methods:
        get_raw_data():
            This method extracts raw data from MongoD json files available in ./data folder.
        extract_raw_data():
            This is the first step to get the data based on heads and different sensors.
        preprocess_data(extr_df):
            Preprocesses the data to from original timestamps.
        fill_data(df, det_sensors):
            Fill the NaN values in the DataFrame.
    """
    def __init__(
            self,
            sensors: list,
            category: str,
            machinery: str,
            show_fig: bool =False,
            save_fig: bool = True,
            figs_dir: str ='./figs',
            plt_style: str = 'Solarize_Light2',
            data_path: str = './data',
            verbose: bool = True
            ):
        """
        Initialize a new instance of Extract.
        
        Args:
            sensors (list): list of all sensors we want to analyze
            category (str): name of category ['eqtq', 'drive']
            machinery (str): name of machinery
            show_fig (bool): whether to show the figs while extracting
            save_fig (bool): whether to save the figs while extracting
            figs_dir (str): figs directory.
            plt_style (str): plot styles.
            data_path (str): original data path of the sensors.
            verbose (bool): whether to print any information regarding extraction.
        """
        self.verbose=verbose
        self.figs_dir = figs_dir
        self.sensors = sensors.copy()
        self.machinery = machinery
        self.category = category
        self.category_path = os.path.join(data_path, 'MongoData' + category.upper() +'.json')
        self.raw_data = None
        self.verbose = verbose
        # we define some addiftional sensor to be identified as deterministc sesnsors
        self.additional_det = ['Alarm', 'OperationState', 'TotalProduct']

        if show_fig: self._set_plt_style(plt_style)
        
    def _set_plt_style(self, plt_style):
        plt.style.use(plt_style)
        
    
    def _set_sensors_dict(self):
        self.sensor_dict = {key: pd.DataFrame(columns=['value']) for key in self.sensors}
        
    def _set_data(self):
        with open(self.category_path, 'r') as datafile:
            data = json.load(datafile)
        self.raw_data = pd.DataFrame(data)
        if self.verbose:
            print(f'\n1 head and {len(self.sensors)} sensors detected in "{self.category}" sensor category.')

    def _split_sensors(self, df, deterministic_sensor):
        _ = [df.pop(k, None) for k in deterministic_sensor]
        new_sesnors = [sensor for sensor in self.sensors if sensor not in deterministic_sensor]
        return new_sesnors
    
    
    def get_raw_data(self):
        """
        Returns:
            pd.DataFrame: first dataframe object of the sensors data
        """
        if self.raw_data is None:
            self._set_data()
        return self.raw_data
        
    def extract_raw_data(self):
        """
        Returns:
            dict: a dictionary containing all heads as values and sensors and keys
        """
        
        self._set_sensors_dict()
        sensors_cpy = self.sensors.copy()
        if self.verbose:
            print('Extracting raw data.')
        self.raw_data = self.raw_data.drop(columns=["_id", "day", "first_time", "last_time", "nsamples"])
        self.raw_data = self.raw_data[self.raw_data.variable!='RunningTime']
        self.raw_data = self.raw_data[self.raw_data.variable!='PowerOnTime']
        
        for sensor in sensors_cpy:
            # In this function we try to understand the relationship between deifferent heads
            # We delete the index, so we can join different heads, this is a prototype. 
            df_by_sensor = self.raw_data[self.raw_data.variable.str.contains(sensor)]
            df_all = pd.DataFrame(df_by_sensor.samples.sum())
            df_all.time = df_all.time.map(lambda x: int(x[list(x.keys())[0]]))
            df_all.index = df_all.set_index('time').index.astype(int)/1000
            df_all = df_all.drop_duplicates()
            self.sensor_dict[sensor] = df_all
            
        for sensor in sensors_cpy:     
            self.sensor_dict[sensor] = self.sensor_dict[sensor].dropna(axis='columns', how='all').sort_index().rename(index={'time':'date'})
            self.sensor_dict[sensor].index = pd.to_datetime(self.sensor_dict[sensor].index, unit='s')
            self.sensor_dict[sensor] = self.sensor_dict[sensor].drop(columns='time')
            
        return self.sensor_dict
    
    
    
    def preprocess_data(self, extr_df):
        """
        Args:
            extr_df (dict): a dictionary containing all heads as values and sensors and keys.
        
        Returns:
            tuple[dict, list]: A new dictionary of the preprocessed sensors
                               and deterministic sensors.
        """
        deterministic_sensor = []
        new_df = extr_df
        for sensor in self.sensors:
            # We group the data for each sensor based on the days
            results = [group[1] for group in new_df[sensor].groupby(new_df[sensor].index.date)]
            # result[2].interpolate(method='linear').plot(legend=False)
            tot_var = 0
            new_results = []
            for result in results:
                # We remove results that do not have sufficent variance in their heads. We catogorize them as deterministic sensors
                if len(result)<=1:
                    continue
                tot_var += result.value.var().sum()
                if result.value.var().sum() > 1e-1: new_results.append(result)

            if len(new_results)==0:
                
                if self.verbose:
                    print(f'Sensor {sensor} has total variance of {tot_var} and is deterministic.')
                deterministic_sensor.append(sensor)
                continue
            deterministic_sensor.extend(self.additional_det)
            
            new_df[sensor] = pd.concat(new_results)
        return new_df, deterministic_sensor
    

        
    
    def fill_data(self, df, det_sensors): 
        """
        Args:
            extr_df (dict): a dictionary containing all heads as values and sensors and keys.
        
        Returns:
            tuple[dict, list]: A new dictionary of the preprocessed sensors
                               and deterministic sensors.
        """
        filled = copy.deepcopy(df)
        for sensor in self.sensors:
            filled[sensor] = df[sensor].interpolate(method='linear').dropna(axis=0)
            filled[sensor] = filled[sensor].query('~index.duplicated()')
        
        if self.verbose:
            print('NaN values have been filled.')
        return filled
    



def plot_heads(df, sensor, category, colors, show_fig, save_folder='./figs/data') -> None:
    """
    Plot all heads sensor data based on the sensor in each category. All the 
    plots should be based on the output of filled_data() method in Extract class.

    Args:
        df (pd.DataFrame): extracted dataframe for a specific sensor.
        sensor (str): sensor name.
        category (str): sensor category.
        colors (list): colors for different heads.
        show_fig (bool): show figures while running the function.
        save_folder (str): folder to save the plots.

    Returns:
        None
    """
    save_dir = save_folder + '/' + category
    os.makedirs(save_dir, exist_ok=True)
    results = [group[1] for group in df.groupby(df.index.date)]
    for result in results:
        fig = go.Figure()
        fig = px.line(result, x=result.index, y=result.columns, title=f'{category} Sensor Category - {sensor.capitalize()} Sensor - Day {result.index[0].day}', color_discrete_sequence=colors)
        fig.update_xaxes(
            tickangle = 90,
            tickformat="%H:%M:%S", # the date format you want 
        )
        
        pio.write_image(fig, f"{save_dir}/{sensor}_heads_{result.index[0].day}.png", width=1320, height=720)
        if show_fig:
            fig.show()
        
    
    df = df.reset_index(drop=True)
    fig = go.Figure()
    fig = px.line(df, x=df.index, y=df.columns, title=f'{category} Sensor Category - {sensor.capitalize()} Sensor', color_discrete_sequence=colors)
    fig.update_xaxes(visible=False)
    pio.write_image(fig, f"{save_dir}/{sensor}_heads.png", width=1320, height=720)
    if show_fig:
        fig.show()
        

        
            
            
def plot_correlation(df, sensor, category, show_fig, save_folder='./figs/correlation') -> None:
    """
    Plot correlations of different heads in each category. All the 
    plots should be based on the output of filled_data() method in Extract class.

    Args:
        df (pd.DataFrame): extracted dataframe for a specific sensor.
        sensor (str): sensor name.
        category (str): sensor category.
        show_fig (bool): show figures while running the function.
        save_folder (str): folder to save the plots.

    Returns:
        None
    """
    
    df = df.reset_index(drop=True)
    save_dir = save_folder + '/' + category
    os.makedirs(save_dir, exist_ok=True)

    f = plt.figure(figsize=(19, 15))
    plt.matshow(df.corr(), fignum=f.number)
    plt.xticks(range(df.select_dtypes(['number']).shape[1]), df.select_dtypes(['number']).columns, fontsize=8, rotation=45)
    plt.yticks(range(df.select_dtypes(['number']).shape[1]), df.select_dtypes(['number']).columns, fontsize=8)
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=10)
    plt.title(f'{category} Heads Correlation Matrix - {sensor.capitalize()} Sensor', fontsize=12)
    plt.savefig(f"{save_dir}/{sensor}_corr.png",bbox_inches='tight')
    
    if show_fig:
        plt.show()
