#!/usr/bin/env python3
import os
from flask import Flask, jsonify, request
import requests
import jinja2
from copy import deepcopy
from flask_cors import CORS, cross_origin
from os import environ

template_dir = os.path.join(os.path.dirname(__file__),'templates')
static_dir = os.path.join(os.path.dirname(__file__),'static')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

app = Flask(__name__, static_url_path='/static', template_folder="/templates")
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


#API_ROOT_URL =  "{}:{}".format(os.getenv("BACK_HOST"), os.getenv('BACK_PORT'))
API_ROOT_URL="http://127.0.0.1:3000"

def render_template(template_name, **kwargs):
    template = jinja_env.get_template(template_name)
    
    if kwargs:
        return template.render(**kwargs)
    else:
        return template.render()

@app.route("/")
def home():
    return render_template('index.html')



@app.route('/datasets', methods=['GET'])
def dataset_list():
    req_datasets = requests.get(API_ROOT_URL+"/datasets")
    datasets = req_datasets.json()
    # print(datasets)
    count = requests.get(API_ROOT_URL+"/datasets/count")
    #build filter menu
    req_filters = requests.get(API_ROOT_URL+"/references/filters/dataset/")
    filters = req_filters.json()
    values = {}
    _filters = []
    for f in filters:
        if f["slug"] == "organizations":
            req_org = requests.get(API_ROOT_URL+"/organizations/")    
            values[f["slug"]] = [r["name"] for r in req_org.json()]
            f["is_bool"] = False
            _filters.append(f)
        else:
            if f["datatype"] == "bool":
                f["is_bool"] = True
                values[f["slug"]] = [{"label_en":"Yes", "label_fr":"Oui"},{"label_en":"No", "label_fr":"Non"}]
                _filters.append(f)
            else:
                if (f["is_controled"]):
                    print(f["slug"], "references")
                    values_req = requests.get(API_ROOT_URL+"/references/"+f['reference_table'])
                    if not values_req.status_code == 404:
                        f["is_bool"] = False
                        _filters.append(f)
                        values[f["slug"]] = values_req.json()
                    else:
                        print("Error", f["slug"])    
                elif f["slug"] == "geographical_geospatial_information_level":
                    print(f["slug"], "references")
                    values_req = requests.get(API_ROOT_URL+"/references/"+f['reference_table'])
                    if not values_req.status_code == 404:
                        _filters.append(f)
                        values[f["slug"]] = values_req.json()
                    else:
                        print("Error", f["slug"])
                else:
                    values_req = requests.get(API_ROOT_URL+"/references/filters/dataset/"+f['slug']+"/values")
                    print(f["slug"], "distinct values")
                    if not values_req.status_code == 404:
                        values[f["slug"]] = values_req.json()
                        f["is_bool"] = False
                        _filters.append(f)
                    else:
                        print("Error", f["slug"])
        
    return render_template('datasets.tpl', result=datasets, count=count.json(), filters=_filters, values=values)

@app.route('/datasets/<dataset_id>', methods=['GET'])
def dataset_item(dataset_id):
    print(dataset_id)
    req_datasets = requests.get(f"{API_ROOT_URL}/datasets/{dataset_id}")
    dataset = req_datasets.json()
    # dataset["_id"] = str(dataset["_id"])
    print(dataset)
    return render_template('dataset.html', dataset=dataset)

@app.route("/organizations/", methods=["GET"])
def organization_list():
    req_orgs = requests.get(API_ROOT_URL+"/organizations")
    orgs = req_orgs.json()
    return render_template('organizations.tpl', result=orgs, count=len(orgs) )
    
@app.route("/organizations/<org_id>/", methods=["GET"])
def organization_detail(org_id):
    print(org_id)
    req_orgs = requests.get(f"{API_ROOT_URL}/organizations/{org_id}")
    orgs = req_orgs.json()

    req_count = requests.get(f"{API_ROOT_URL}/organizations/{org_id}/datasets/")
    print(req_count)
    count = req_count.json()    
    return render_template('organization.tpl', org=orgs, datasets = count, count=len(count))


@app.route("/references/", methods=["GET"])
def reference_list():
    print(API_ROOT_URL, )
    req_refs = requests.get(f"{API_ROOT_URL}/references/")
    references = req_refs.json()
    print(references)
    return render_template('references.tpl', references=references, count=len(references))

@app.route("/comments/", methods=["GET"])
def comment_list():
    req_refs = requests.get(f"{API_ROOT_URL}/comments")
    references = req_refs.json()
    return render_template('references.tpl', references=references, count=len(references))


if __name__=="__main__":
#     # os.getenv("FRONT_HOST")
#     # os.getenv("FRONT_PORT")
#     # os.getenv("FRONT_DEBUG")
#     # app.run(host=os.getenv("FRONT_HOST"), port=os.getenv("FRONT_PORT"), debug=os.getenv("FRONT_DEBUG"))
    app.run(host="localhost", port=8000, debug=True, load_dotenv=True)
