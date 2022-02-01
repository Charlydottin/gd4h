from pydantic import create_model 
from pymongo import MongoClient
from bson import ObjectId
DATABASE_NAME = "GD4H_V2"
import os
mongodb_client = MongoClient("mongodb://localhost:27017")
DB = mongodb_client[DATABASE_NAME]
AVAILABLE_LANG = ["fr","en"]
SWITCH_LANGS = dict(zip(AVAILABLE_LANG,AVAILABLE_LANG[::-1]))
curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curr_dir)
data_dir = os.path.join(parent_dir, "data")
meta_dir = os.path.join(data_dir, "meta")
schema_dir = os.path.join(data_dir, "schemas")
data_dir = os.path.join(parent_dir, "data")

def create_rules_json_schema():
    one_record = DB.rules.find_one({},{"_id":0})
    print(one_record)
    # one_record["_id"] =str(one_record["_id"])
    rule_model = create_model("Rules", **one_record)
    print(rule_model)
    rule_json_schema = rule_model.schema_json()
    with open(os.path.join(data_dir, "schemas", "Rules.json"), "w") as f:
        f.write(rule_json_schema)

def create_reference_json_schema():
    class Config:
        arbitrary_types_allowed = True
    one_record = DB.references.find_one({},{"_id":0})
    
    
    rule_model = create_model("Reference", **one_record, __config__=Config)
    rule_json_schema = rule_model.schema_json()
    with open(os.path.join(schema_dir, "References.json"), "w") as f:
        f.write(rule_json_schema)

def create_org_json_schema():
    # class Config:
    #     arbitrary_types_allowed = True
    one_record = DB.organizations.find_one({},{"_id":0})
    validators = {
    'reference_validator':
        validator('agent_type')(check_value(agent_type))
    }
    
    rule_model = create_model("Organization", **one_record["fr"], __config__=Config)
    rule_json_schema = rule_model.schema_json()
    with open(os.path.join(schema_dir, "organizationFR.json"), "w") as f:
        f.write(rule_json_schema)
if __name__=="__main__":
    # create_rules_json_schema()
    # create_reference_json_schema()
    create_org_json_schema()