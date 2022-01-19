#!/usr/bin/env/python3

__doc__== "Script pour exporter les datasets et les organisations"

import datetime
import os
import csv
from pymongo import MongoClient

DATABASE_NAME = "GD4H_V1"
mongodb_client = MongoClient("mongodb://localhost:27017")
DB = mongodb_client[DATABASE_NAME]
# parent = os.path.dirname(os.getcwd())
data_dir = os.path.join(os.getcwd(), "data")

def export_datasets(lang="fr"):

    datasets_list = []
    for dataset in DB.datasets.find({}, {"_id":0}):
        dataset_row = {}
        for k,v in dataset.items():
            
            rules = DB.meta_fields.find_one({"model":"Dataset", "slug":k}, {"_id":0})
            if rules is not None and "comment" not in k:
                if rules["datatype"] == "bool":
                    dataset_row[k] = v
                    continue    
                elif rules["datatype"] == "dict" and rules["external_model"] == "Organization":
                    dataset_row[k] = "|".join([n["name"] for n in v])
                    continue
                elif rules["multiple"]:
                    if rules["translation"]:
                        try:
                            dataset_row[k] = "|".join([n["label_"+lang] for n in v])
                        except TypeError:
                            dataset_row[k] = "|".join([n["label_"+lang] for n in v if n["label_"+lang] is not None and n["label_"+lang]!= ""])
                            
                        continue
                    else:
                        dataset_row[k] = "|".join(v)
                        continue
                else:
                    if rules["translation"]:
                        dataset_row[k] = v["label_"+lang]
                        continue
                    else:
                        dataset_row[k] = v
                        continue            
        datasets_list.append(dataset_row)

    filename = f"datasets_{lang}.csv"
    filepath = os.path.join(data_dir, "export", filename)
    headers = list(sorted(dataset_row.keys()))
    print(headers)
    with open(filepath, "w") as fd:
        csv_writer = csv.DictWriter(fd, headers)
        csv_writer.writeheader()
        for row in datasets_list:
            csv_writer.writerow(row)

def export_organisations(lang="fr"):
    for org in DB.organizations.find({}, {"_id":0}):
        print(org)
def index_datasets(lang="fr"):
    for rules in DB.meta_fields.find({"model":"Dataset", "is_indexed": True, "is_facet":True}, {"_id":0}):
        print(rules["slug"])
    
if __name__ == "__main__":
    # export_datasets()
    # export_datasets("en")
    index_datasets()