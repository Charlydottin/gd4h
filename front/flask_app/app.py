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
import urllib.parse

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
    if "page_title" not in kwargs:
        kwargs["page_title"] = template_name.split(".")[0].title()
    kwargs["tagline"] = "Outil de recensement des données vertes utiles en Santé Environnement"
    return template.render(**kwargs)
    
@app.route("/")
def home():
    return render_template('index.tpl', title="Green Data For Health")
def build_filter_menu():
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
                    else:
                        values_req = requests.get(API_ROOT_URL+"/references/filters/dataset/"+f['slug']+"/values")
                        if not values_req.status_code == 404:
                            values[f["slug"]] = values_req.json()
                            f["is_bool"] = False
                            _filters[section].append(f)
    return _filters, values

@cross_origin()
@app.route("/search")
def results():
    q = request.args.get('query')
    query = urllib.parse.quote_plus(q)
    results= requests.get(f"{API_ROOT_URL}/search/datasets/fr?q={query}")
    references = results.json()
    _filters, values = build_filter_menu()
    return jsonify({'data': render_template('search_results.tpl', lang="fr", page_title="Jeux de données", count=references["count"],results=references["results"], query=q, filters=_filters, values=values)})
    

@app.route('/datasets/', methods=['GET', 'POST'])
def dataset_list():
    print(request.method)
    req_datasets = requests.get(API_ROOT_URL+"/datasets")
    datasets = req_datasets.json()
    count = requests.get(API_ROOT_URL+"/datasets/count")
    count = count.json()
        
    #build filter menu
    
    _filters, values = build_filter_menu()                
    return render_template('datasets.tpl', title="Datasets", lang="fr", page_title="Jeux de données", results=datasets, count=count, filters=_filters, values=values)

@app.route('/datasets/<dataset_id>', methods=['GET'])
def dataset_item(dataset_id):
    req_datasets = requests.get(f"{API_ROOT_URL}/datasets/{dataset_id}")
    dataset = req_datasets.json()
    rules = requests.get(API_ROOT_URL+"/references/meta/dataset")
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


if __name__=="__main__":
#     # os.getenv("FRONT_HOST")
#     # os.getenv("FRONT_PORT")
#     # os.getenv("FRONT_DEBUG")
#     # app.run(host=os.getenv("FRONT_HOST"), port=os.getenv("FRONT_PORT"), debug=os.getenv("FRONT_DEBUG"))
    app.run(host="localhost", port=8000, debug=True, load_dotenv=True)
