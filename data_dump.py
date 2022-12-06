import pymongo
import pandas as pd
import json

# Provide the mongodb localhost url to connect python to mongodb.
client = pymongo.MongoClient("mongodb://localhost:27017/neurolabDB")

data_file_path = '/config/workspace/aps_failure_training_set1.csv'
database_name = 'aps'
collection_name = 'sensor'

if __name__ == '__main__':
    df = pd.read_csv(data_file_path)
    print(f'Dataset contains {df.shape[0]} rows and {df.shape[1]} columns')

    #convert dataframe to json so that we can dump these records in mongo db
    df.reset_index(drop=True,inplace=True)

    json_records = list(json.loads(df.T.to_json()).values())

    #print(json_records)

    #insert converted json record into MongoDB
    client[database_name][collection_name].insert_many(json_records)
    