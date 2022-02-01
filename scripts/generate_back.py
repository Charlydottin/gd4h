import os
import json
import subprocess
from pydantic import create_model 
from pymongo import MongoClient

DATABASE_NAME = "GD4H_V2"
mongodb_client = MongoClient("mongodb://localhost:27017")
DB = mongodb_client[DATABASE_NAME]

curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curr_dir)
data_dir = os.path.join(parent_dir, "data")
schema_dir = os.path.join(data_dir, "schemas")
model_dir = os.path.join(parent_dir, "gen_back")
apps_dir = os.path.join(model_dir, "apps")


def gen_pydantic_file_from_autogen_json(model_name):
    json_filepath = os.path.join(schema_dir, f"{model_name.title()}.json")
    model_filepath = os.path.join(apps_dir,f"{model_name}", f"models.py")
    subprocess.call(["pydanticgen","-i",json_filepath, "-o",model_filepath ], stderr=subprocess.STDOUT)
    return

def gen_pydantic_file_from_example_db(model_name):
    json_filepath = os.path.join(schema_dir, f"{model_name.title()}.json")
    example = DB[f"{model_name}s"].find_one({"slug": {"$nin": ["id", "_id"]}}, {"_id":0})
    
    if example is not None:
        try:
            example["_id"] = str(example["_id"])
        except KeyError:
            
            pass
        model = create_model(model_name.title(), **example)
        with open(json_filepath, "w") as f:
            f.write( json.dumps(model.schema_json(), indent=4)) 
        model_filepath = os.path.join(apps_dir,f"{model_name}", f"models.py")
        subprocess.call(["pydanticgen","-i",json_filepath, "-o",model_filepath ], stderr=subprocess.STDOUT)
    return

def gen_pydantic_file_from_json_model(model_name):
    ''' import model from json_schema file
    expose a pydantic.model
    '''
    json_filepath = os.path.join(schema_dir, f"{model_name.title()}.json")
    with open(json_filepath, "r") as f:
        json_schema = json.load(f)
    model = create_model(model_name.title(), **json_schema)
    model_filepath = os.path.join("apps",f"{model_name}", f"models.py")
    subprocess.call(["pydanticgen","-i",json_filepath, "-o",model_filepath ], stderr=subprocess.STDOUT)
    return 

if __name__ == "__main__":
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    if not os.path.exists(apps_dir):
        os.makedirs(apps_dir)
    for model in os.listdir(schema_dir):
        if model.endswith(".json"):
            model_name = model.replace(".json", "").lower()
            print(model_name)
            if not os.path.exists(os.path.join(apps_dir, model_name)):
                app_dir = os.makedirs(os.path.join(apps_dir, model_name))
            try:
                gen_pydantic_file_from_autogen_json(model_name)
            except:
                gen_pydantic_file_from_example_db(model_name)
        

        