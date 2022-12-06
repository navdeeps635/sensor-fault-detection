import yaml
import pandas as pd
import os, sys
from sensor.config import mongo_client
from sensor.logger import logging
from sensor.exception import SensorException

def get_collection_as_datarame(database_name:str,collection_name:str)->pd.DataFrame:
    """
    This Function returns collectiona as a dataframe
    database_name: database name
    collection_name: collection name
    ================================
    return Pandas dataframe of a collection
    """
    
    try:
        logging.info(f"Reading data from database: [{database_name}] and collection: [{collection_name}]")
        coll_data = list(mongo_client[database_name][collection_name].find())
        df = pd.DataFrame(coll_data)
        logging.info(f"Found Columns: {df.columns}")

        if "_id" in df.columns:
            logging.info(f"Dropping column: _id")
            df = df.drop("_id",axis = 1)
        logging.info(f"Rows and columns in dataframe: {df.shape}")
        return df
    except Exception as e:
        raise SensorException(e, sys)

def write_yaml_file(file_path, data:dict):
    try:
        file_dir = os.path.dirname(file_path)
        os.makedirs(file_dir,exist_ok=True)

        with open(file_path,'w') as file_writer:
            yaml.dump(data,file_writer)
    
    except Exception as e:
        raise SensorException(e, sys)

def convert_column_float(df:pd.DataFrame,exclude_columns:list)->pd.DataFrame:
    try:
        for column in df.columns:
            if column not in exclude_columns:
                df[column] = df[column].astype('float')
        return df
    
    except Exception as e:
        raise SensorException(e, sys)

if __name__ == '__main__':
    try:
        get_collection_as_datarame(database_name = "aps", collection_name = "sensor")
    except Exception as e:
        print(e)
