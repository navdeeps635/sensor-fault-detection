import pymongo
import pandas as pd
import json
import os
from dataclasses import dataclass



# Provide the mongodb localhost url to connect python to mongodb.
@dataclass
class EnvironMentVariable:
    mongodb_url:str = os.getenv("MONGODB_URL")

env_var = EnvironMentVariable()

mongo_client = pymongo.MongoClient(env_var.mongodb_url)
TARGET_COLUMN = "class"