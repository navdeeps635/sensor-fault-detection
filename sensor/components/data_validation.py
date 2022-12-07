import os,sys
import numpy as np
import pandas as pd
from sensor.entity import artifact_entity, config_entity
from sensor.exception import SensorException
from sensor.logger import logging
from scipy.stats import ks_2samp
from typing import Optional
from sensor import utils
from sensor.config import TARGET_COLUMN

class DataValidation:
    
    def __init__(self,
                data_validation_config:config_entity.DataValidationConfig,
                data_ingestion_artifact:artifact_entity.DataTransformationArtifact):
    
        try:
            logging.info(f"{'>>'*5} Data Validation {'<<'*5}")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.validation_error = dict()

        except Exception as e:
            raise SensorException(e,sys)

    def drop_missing_values_columns(self, df:pd.DataFrame,report_key_name:str)-> Optional[pd.DataFrame]:
        """
        This function will drop columns which contains missing values more than specified threshold
        
        df: accepts a pandas DataFrame
        threshold: percentage criteria to drop a column
        ===============================================
        return pandas dataframe if atleast a single column is available
        """

        try:
            threshold = self.data_validation_config.missing_threshold

            #calculate percentage of missing values in each feature
            null_report = df.isnull().mean()

            logging.info(f"select column names containing null values more than {threshold*100}%")
            #select column names containing null values more than threshold
            drop_column_names = null_report[null_report>0.7].index
            
            logging.info(f"columns to drop:{list(drop_column_names)}")
            #store dropped column names in dictionary
            self.validation_error[report_key_name] = list(drop_column_names)

            df.drop(list(drop_column_names), axis =1, inplace = True)

            #return none if no column left
            if len(df.columns) == 0:
                return None
            return df
        except Exception as e:
            raise SensorException(e,sys)

    def is_required_column_exists(self,base_df:pd.DataFrame,current_df:pd.DataFrame,report_key_name:str)->bool:

        try:
            base_columns = base_df.columns
            current_columns = current_df.columns

            #check missing columns in current_df
            missing_columns = []
            for base_column in base_columns:
                if base_column not in current_columns:
                    logging,info(f"column:[{base} is not available.]")
                    missing_columns.append(base_column)
            
            #store missing column names in dictionary
            if len(missing_columns)>0:
                self.validation_error[report_key_name] = missing_columns
                return False
            return True                    
        except Exception as e:
            raise SensorException(e,sys)

    def data_drift(self,base_df:pd.DataFrame,current_df:pd.DataFrame,report_key_name:str):
        try:
            drift_report = dict()

            base_columns = base_df.columns
            current_columns = current_df.columns

            for base_column in base_columns:
                base_data, current_data = base_df[base_column],current_df[base_column]
                
                #null hypothesis is that both data drawn from same distribution
                distribution = ks_2samp(base_data, current_data)

                if distribution.pvalue>0.05:
                    drift_report[base_column] = {'pvalue':float(distribution.pvalue),"same_distribution":True}
                else:
                    drift_report[base_column] = {'pvalue':float(distribution.pvalue),"same_distribution":False}

            self.validation_error[report_key_name] = drift_report
        except Exception as e:
            raise SensorException(e,sys)

    def initiate_data_validation(self)-> artifact_entity.DataIngestionArtifact:
        try:
            logging.info(f"reading base dataframe")
            base_df = pd.read_csv(self.data_validation_config.base_file_path)
            
            logging.info(f"replacing 'na' values with np.NaN in base dataframe")
            #replace 'na' values in base_df with np.NaN 
            base_df.replace({"na":np.NAN},inplace = True)
            
            logging.info(f"drop null values columns from base dataframe")
            base_df = self.drop_missing_values_columns(df = base_df,report_key_name = "missing_values_within_base_dataset")

            logging.info(f"reading train dataframe")
            train_df = pd.read_csv(self.data_ingestion_artifact.train_file_path)

            logging.info(f"reading test dataframe")
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)

            logging.info(f"drop null values columns from training dataframe")
            train_df = self.drop_missing_values_columns(df = train_df,report_key_name = "missing_values_within_train_dataset")
            
            logging.info(f"drop null values columns from test dataframe")
            test_df = self.drop_missing_values_columns(df = test_df,report_key_name = "missing_values_within_test_dataset")

            exclude_columns = TARGET_COLUMN
            utils.convert_column_float(df = base_df, exclude_columns = exclude_columns)
            utils.convert_column_float(df = train_df, exclude_columns = exclude_columns)
            utils.convert_column_float(df = test_df, exclude_columns = exclude_columns)


            logging.info(f"is all required columns present in training dataframe")
            train_df_columns_status = self.is_required_column_exists(base_df = base_df, current_df = train_df,report_key_name="missing_columns_within_train_dataset")
            
            logging.info(f"is all required columns present in test dataframe")
            test_df_columns_status = self.is_required_column_exists(base_df = base_df, current_df = test_df,report_key_name="missing_columns_within_test_dataset")

            if train_df_columns_status:
                logging.info(f"As all columns are available in training dataframe hence detecting data drift")
                self.data_drift(base_df= base_df, current_df= train_df,report_key_name="data_drift_within_train_dataset")

            if test_df_columns_status:
                logging.info(f"As all columns are available in test dataframe hence detecting data drift")
                self.data_drift(base_df= base_df, current_df= test_df,report_key_name="data_drift_within_test_dataset")   
            
            #write the report
            logging.info(f"writing report in yaml file")
            utils.write_yaml_file(file_path = self.data_validation_config.report_file_path,
            data = self.validation_error) 

            data_validation_artifact = artifact_entity.DataValidationArtifact(report_file_path = self.data_validation_config.report_file_path)
            logging.info(f"Data validation artifact: {data_validation_artifact}")
            return data_validation_artifact

        except Exception as e:
           raise SensorException(e,sys)