#!/usr/bin/env python3
from http.client import HTTPException
from operator import itemgetter
#from msilib.schema import Error
import os
from flask import Flask, jsonify, request
import requests
import urllib.parse
import jinja2
import itertools
from flask_cors import CORS, cross_origin

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
    kwargs["lang"] = "fr"
    kwargs["title"]= "Green Data For Health"
    kwargs["page_title"] = template_name.split(".")[0].title()
    kwargs["tagline"] = "Outil de recensement des données vertes utiles en Santé Environnement"
    return template.render(**kwargs)
    
@app.route("/")
def home():
    return render_template('index.tpl', title="Green Data For Health")


# @app.route('/search/datasets/{lang}?', methods=['POST'])
# def search_dataset():
#     print("search dataset")
#     if request.args.get("query") is not None:
#         query = urllib.parse.quote_plus(request.args.get("query"))
#         data = requests.get(API_ROOT_URL+"/search/datasets/fr?q="+query)    
#         count_results = data.json()
#         count = count_results["count"]
#         datasets = count_results["results"] 
#         return render_template('datasets.tpl', result=datasets, count=count)
#     # return HTTPException("No query")

@app.route('/datasets/', methods=['GET', 'POST'])
def dataset_list():
    
    req_datasets = requests.get(API_ROOT_URL+"/datasets")
    datasets = req_datasets.json()
    count = requests.get(API_ROOT_URL+"/datasets/count")
    count = count.json()
        
    #build filter menu
    req_filters = requests.get(API_ROOT_URL+"/references/filters/dataset/")
    filters = req_filters.json()
    values = {}
    _filters = {f["section"]: [] for f in filters}
    for section, filter_group in itertools.groupby(filters, lambda f: f["section"]):
        for f in filter_group:
            if f["slug"] == "organizations":
                req_org = requests.get(API_ROOT_URL+"/organizations/")    
                values[f["slug"]] = [r["name"] for r in req_org.json()]
                f["is_bool"] = False
                _filters[section].append(f)
            else:
                if f["datatype"] == "bool":
                    f["is_bool"] = True
                    values[f["slug"]] = [{"label_en":"Yes", "label_fr":"Oui"},{"label_en":"No", "label_fr":"Non"}]
                    _filters[section].append(f)
                else:
                    if (f["is_controled"]):
                        #print(f["slug"], "references")
                        values_req = requests.get(API_ROOT_URL+"/references/"+f['reference_table'])
                        if not values_req.status_code == 404:
                            f["is_bool"] = False
                            values[f["slug"]] = values_req.json()
                            _filters[section].append(f)    
                    # elif f["slug"] == "geographical_geospatial_information_level":
                    #     #print(f["slug"], "references")
                    #     values_req = requests.get(API_ROOT_URL+"/references/"+f['reference_table'])
                    #     if not values_req.status_code == 404:
                    #         _filters.append(f)
                    #         values[f["slug"]] = values_req.json()
                    #     else:
                    #         print("Error", f["slug"])
                    else:
                        values_req = requests.get(API_ROOT_URL+"/references/filters/dataset/"+f['slug']+"/values")
                        if not values_req.status_code == 404:
                            values[f["slug"]] = values_req.json()
                            f["is_bool"] = False
                            _filters[section].append(f)
                    #else:
                        #print("Error", f["slug"])
    return render_template('datasets.tpl', title="Datasets", page_title="Jeux de données", result=datasets, count=count, filters=_filters, values=values)

@app.route('/datasets/<dataset_id>', methods=['GET'])
def dataset_item(dataset_id):
    req_datasets = requests.get(f"{API_ROOT_URL}/datasets/{dataset_id}")
    dataset = req_datasets.json()
    rules = requests.get(API_ROOT_URL+"/references/meta/dataset")
    print(rules.json())
    ordered = sorted([(rule["section"],rule["slug"], int(rule["order"])) for rule in rules.json()], key=itemgetter(2))
    dataset_section = {}
    for section, filter_group in itertools.groupby(ordered, lambda f: f[0]):
        print(section)
        dataset_section[section] = []
        for section, slug, order in filter_group:
            # if order != -1:
            try:
                dataset_section[section].append({slug: dataset[slug]})
            except KeyError:
                pass 
    return render_template('dataset.html', dataset= dataset, additionnal_info=dataset_section)

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

@app.route("/search?", methods=["GET"])
def get_users():
    req_refs = requests.get(f"{API_ROOT_URL}/search/datasets/fr?q=eau%20CO2")
    references = req_refs.json()
    return(references)

if __name__=="__main__":
#     # os.getenv("FRONT_HOST")
#     # os.getenv("FRONT_PORT")
#     # os.getenv("FRONT_DEBUG")
#     # app.run(host=os.getenv("FRONT_HOST"), port=os.getenv("FRONT_PORT"), debug=os.getenv("FRONT_DEBUG"))
    app.run(host="localhost", port=8000, debug=True, load_dotenv=True)
