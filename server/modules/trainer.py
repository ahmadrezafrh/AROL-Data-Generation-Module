# -*- coding: utf-8 -*-
import os
import pandas as pd
import matplotlib.pyplot as plt
import lightning.pytorch as pl

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
from dataclasses import field

from lightning.pytorch.callbacks import EarlyStopping, LearningRateMonitor, ModelCheckpoint
from lightning.pytorch.loggers import TensorBoardLogger
from lightning.pytorch.tuner import Tuner

from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
from pytorch_forecasting.data import GroupNormalizer
from pytorch_forecasting.metrics import MAE, QuantileLoss
from pytorch_forecasting.data.encoders import EncoderNormalizer, MultiNormalizer, TorchNormalizer
import torch


class Trainer:
    """
    This class have been designed to train, evaluate and validate the output
    data of the Extract() class. We accelerate the work and modularity using
    this wrapper.
    """
    def __init__(
            self,
            learning_rate: float = 0.09,
            epochs: int = 50,
            batch_size: int = 128,
            device: str = 'cpu'
            ):
        """
        Initialize a new instance of Extract.
        
        Args:
            learning_rate (list): learning rate value in the optimization
            epochs (str): how many times models should be trained
            batch_size (str): number of batches
            device (bool): which device we want to do the training
        """
        
        self.device = device
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.epochs = epochs
        
    def create_dataloaders(
            self,
            data: pd.DataFrame,
            training_cutoff: int,
            max_prediction_length: int,
            max_encoder_length: int,
            target: list = field(default_factory=list),
            unk_vars: list = field(default_factory=list),
            group_ids: list = field(default_factory=list),
            ):
        
        """
        This method creates dataloaders to be passed to the trainer module.
        
        Args:
            data (pd.DataFrame): the preprocessed data from Extract class
            training_cutoff (int): cut of for the trianing data to avoid errors
            max_prediction_length (int): prediction length of the output
            max_encoder_length (int): input data length
            target (list): which head or column we want to predict
            unk_vars (list): which variables are important for predicting the output
            group_ids (list): grouping based on a certain categorical column
        """
        if len(target)==1:
            target=target[0]

        self.training = TimeSeriesDataSet(
            data[lambda x: x.time_idx <= training_cutoff],
            time_idx="time_idx",
            target=target,
            group_ids=group_ids,
            min_encoder_length=max_encoder_length // 2,  # keep encoder length long (as it is in the validation set)
            max_encoder_length=max_encoder_length,
            min_prediction_length=1,
            max_prediction_length=max_prediction_length,
            static_categoricals=group_ids,
            time_varying_known_reals=["time_idx"],
            time_varying_unknown_reals=[target],
            # target_normalizer=MultiNormalizer(
            #     [EncoderNormalizer(), TorchNormalizer()]
            # ),  # Use the NaNLabelEncoder to encode categorical target
            target_normalizer=GroupNormalizer(
                groups=group_ids, transformation="softplus"
            ),  # use softplus and normalize by group
            add_relative_time_idx=True,
            add_target_scales=True,
            add_encoder_length=True,
        )

        # create validation set (predict=True) which means to predict the last max_prediction_length points in time
        # for each series
        self.validation = TimeSeriesDataSet.from_dataset(self.training, data, predict=True, stop_randomization=True)
        self.train_dataloader = self.training.to_dataloader(train=True, batch_size=self.batch_size, num_workers=0)
        self.val_dataloader = self.validation.to_dataloader(train=False, batch_size=self.batch_size * 10, num_workers=0)

    # configure network and trainer
    
    def set_trainer(
            self,
            machinery: str,
            category: str,
            sensor: str,
            head: str,
            devices: str,
            logs_dir: str,
            checkpoints_dir: str,
            clipping: float = 0.1,
            model_summary: bool = False,
            min_delta: float = 1e-4,
            patience: int = 10,
            verbose: bool = False,
            early_mode: str = "min",
            ):
        
        """
        This method creates dataloaders to be passed to the trainer module.
        
        Args:
            machinery (str): machinery name
            category (str): category of the machine
            sensor (str): name of the sensor available in the specific category
            head (str): which is the main head of the sensor to predict based on it
            devices (str): which devices should be used for training
            checkpoints_dir (str): checkpoints directory to save the model
            logs_dir (str): logs directory to save the model losses for tensorboard
            clipping (float): model parameter
            model_summary (bool): whether to have model summary
            min_delta (float): parameter of the model
            patience (int): patience for the validation loss to decrease
            verbose (bool): whether to print logs in the training
            early_mode (str): which algorithm we use for stopping the training 
            
        
        Returns:
            pl.Trainer: the trainer object for training the model
        """
        early_stop_callback = EarlyStopping(monitor="val_loss", min_delta=min_delta, patience=patience, verbose=False, mode=early_mode)

        pl.seed_everything(42)
        

        # DEFAULTS used by the Trainer
        checkpoint_callback = ModelCheckpoint(
            dirpath=f'{checkpoints_dir}/{machinery}/{category}/{head[0]}',
            filename=f'{sensor}',
            save_top_k=1,
            verbose=False,
            monitor='val_loss',
            mode='min',
        )
        

        lr_logger = LearningRateMonitor()  # log the learning rate
        logger = TensorBoardLogger(f"{checkpoints_dir}/{logs_dir}/{machinery}-{category}-{sensor}/{head[0]}")  # logging results to a tensorboard
        self.trainer = pl.Trainer(
            max_epochs=self.epochs,
            accelerator=self.device,
            devices=devices,
            enable_model_summary=model_summary,
            gradient_clip_val=clipping,
            limit_train_batches=50,  # coment in for training, running valiation every 30 batches
            # fast_dev_run=True,  # comment in to check that networkor dataset has no serious bugs
            callbacks=[lr_logger, early_stop_callback, checkpoint_callback],
            logger=logger,
            default_root_dir=checkpoints_dir,
        )
        
        return self.trainer
    
    def set_model(
            self,
            hidden_size: int = 8,
            hidden_continuous_size: int = 8,
            attention_head_size: int = 2,
            dropout: float = 0.1
            ):
        """
        This method sets the model for the training. The model has different
        parameters which needs to be writted in the config.py file.
        
        Args:
            hidden_size (int): number of attention layers
            hidden_continuous_size (int): number of attention continuous layers machine
            attention_head_size (int): how many heads for each attention heads
            dropout (float): dropout value to avoid overfit
            
        
        Returns:
            TemporalFusionTransformer: the built model
        """
        self.tft = TemporalFusionTransformer.from_dataset(
            self.training,
            # not meaningful for finding the learning rate but otherwise very important
            learning_rate=self.learning_rate,
            hidden_size=hidden_size,  # most important hyperparameter apart from learning rate
            # number of attention heads. Set to up to 4 for large datasets
            attention_head_size=attention_head_size,
            dropout=dropout,  # between 0.1 and 0.3 are good values
            hidden_continuous_size=hidden_continuous_size,  # set to <= hidden_size
            loss=QuantileLoss(),
            optimizer="Ranger"
            # reduce learning rate if no improvement in validation loss after x epochs
            # reduce_on_plateau_patience=1000,
        )
        print(f"Number of parameters in network: {self.tft.size()/1e3:.1f}k")
        return self.tft


    def find_lr(
            self,
            replace = True
            ):
        """
        This method sets the model for the training. The model has different
        parameters which needs to be writted in the config.py file.
        
        Args:
            hidden_size (int): number of attention layers
            hidden_continuous_size (int): number of attention continuous layers machine
            attention_head_size (int): how many heads for each attention heads
            dropout (float): dropout value to avoid overfit
            
        
        Returns:
            TemporalFusionTransformer: the built model
        """
        res = Tuner(self.trainer).lr_find(
            self.tft,
            train_dataloaders=self.train_dataloader,
            val_dataloaders=self.val_dataloader,
            max_lr=10.0,
            min_lr=1e-6,
        )
        
        print(f"suggested learning rate: {res.suggestion()}")
        if replace:
            self.learning_rate = res.suggestion()
            self.tft.learning_rate = res.suggestion()
            print('learning rate have been replaced with the suggestion')
        return res.suggestion()



    def load_model(self, path):
        """
        Loads the available TFT models. It is used in the Generation class
        to generate new output.
        
        Args:
            path (str): path to the trained model's checkpoint
            
        
        Returns:
            TemporalFusionTransformer: the built model
        """
        self.model = TemporalFusionTransformer.load_from_checkpoint(path, map_location=torch.device(self.device))



    def fit(
        self,
        ):
        """
        Trains the model and saves best models based on the validation loss.
        """
        self.trainer.fit(
            self.tft,
            train_dataloaders=self.train_dataloader,
            val_dataloaders=self.val_dataloader,
        )
        best_model_path = self.trainer.checkpoint_callback.best_model_path
        self.model = TemporalFusionTransformer.load_from_checkpoint(best_model_path, map_location=torch.device(self.device))



    def val_predict(
            self,
            plot: bool = True
            ):
        """
        Predict values of the validation DataLoader. 
        
        Args:
            plot (bool): whether to show the plot of the prediction or not
            
        
        Returns:
            torch.Tensor: output prediction
        """
        predictions = self.model.predict(self.val_dataloader, return_y=True, trainer_kwargs=dict(accelerator=self.device))
        MAE()(predictions.output, predictions.y)
        raw_predictions = self.model.predict(self.val_dataloader, mode="raw", return_x=True)
        if plot:
            self.model.plot_prediction(raw_predictions.x, raw_predictions.output, idx=0, add_loss_to_title=True)
        return predictions

    def pred_by_variable(
            self,
            plot: bool = True
            ):
        """
        Predict values of the validation DataLoader based on the variable. 
        
        Args:
            plot (bool): whether to show the plot of the prediction or not
            
        
        Returns:
            torch.Tensor: output prediction
        """
        predictions = self.model.predict(self.val_dataloader, return_x=True, trainer_kwargs=dict(accelerator=self.device))
        predictions_vs_actuals = self.model.calculate_prediction_actual_by_variable(predictions.x, predictions.output)
        if plot:
            self.model.plot_prediction_actual_by_variable(predictions_vs_actuals)   
        return predictions


    def raw_predict(
            self,
            selected_day: int,
            plot: bool = True
            ):
        """
        Predicting data using a specific day for encoder input data
        
        Args:
            plot (bool): whether to show the plot of the prediction or not
            selected_day (int): the day to be used for the encoder input
            
        
        Returns:
            torch.Tensor: output prediction
        """
        
        raw_prediction = self.model.predict(
            self.training.filter(lambda x: (x.day == f"{selected_day}")),
            mode="raw",
            return_x=True,
            trainer_kwargs=dict(accelerator=self.device)
        )
        self.model.plot_prediction(raw_prediction.x, raw_prediction.output, idx=0)
        if plot:
            plt.show()
        return raw_prediction


    def predict(
            self,
            data,
            plot: bool = True
            ):
        """
        Predicting based on the data we pass to this function. We use this method
        in the Generat() class to predict new values
        
        Args:
            data (pd.DataFrame): dataframe in the Extract() class format
            selected_day (int): the day to be used for the encoder input
            
        
        Returns:
            torch.Tensor: output prediction
        """
        new_raw_predictions = self.model.predict(data, mode="raw", return_x=True, trainer_kwargs=dict(logger=False, accelerator=self.device))
        if plot:
            self.model.plot_prediction(new_raw_predictions.x, new_raw_predictions.output, idx=0, show_future_observed=False)
            plt.show()
            
        return new_raw_predictions