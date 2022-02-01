
def import_organizations():
    '''import_organizations
    insert organization defined by rules into DB.organizations from data/organizations/organizations_fr.csv
    '''
    DB.organizations.drop()
    org_doc = os.path.abspath(os.path.join(data_dir, "organizations", "organizations_fr.csv"))
    print(f"Create Organizations by inserting {org_doc}")
    with open(org_doc, "r") as f:
        reader = DictReader(f, delimiter=",")
        for row in reader:
            org = {"fr": {},"en": {}}
            org["fr"] = row
            org["en"] = {k: v for k,v in row.items() if get_not_translated_fields("organization")} 
            for translated_field in  get_translated_fields("organization"):
                rule = get_rule("organization", translated_field)
                try:
                    value = row[translated_field] 
                    if rule["is_controled"]:
                        accepted_ref = DB[rule["reference_table"]].find_one({"label_fr": value}, {"label_en":1})
                        try:
                            value = accepted_ref["label_en"]
                        except: 
                            value = accepted_ref
                except KeyError:
                    value = None
                org["en"][translated_field] = value
            db_org = DB.organizations.insert_one(org)
            create_logs("admin","create", "organization", True, "OK", scope=None, ref_id=db_org.inserted_id)
    print(DB.organizations.count_documents({}), "organization inserted")



def import_datasets():
    print("Create Datasets")
    created_datasets = []
    datasets_doc = os.path.abspath(os.path.join(data_dir, "datasets", "census_datasets_fr.csv"))
    with open(datasets_doc, "r") as f:
        reader = DictReader(f, delimiter=",")
        for row in reader:
            dataset = {}
            #COMMON
            dataset["name"] = row["dataset_name"]
            dataset["acronym"] = row["acronym"]
            dataset["description"] = {"label_fr":row["description"], "label_en": None}
            dataset["organizations"] = [{"name":n.strip()} for n in row["organization"].split("|")]
            dataset["url"] = row["link"]
            #CONTACT
            dataset["contact"] = [row["contact"]]
            dataset["contact_type"] = [{"label_fr": "email", "label_en": "email"}]
            dataset["contact_comments"] = [create_comment("admin", text=row["contact"])]
            # SANTE-ENVIRONNEMENT
            dataset["data_domain"] = {"label_fr": row["data_domain"], "label_en": None}
            dataset["theme_category"] = {"label_fr":row["theme_category"], "label_en": None}
            dataset["thematic_field"] = {"label_fr":row["thematic_field"], "label_en": None} 
            dataset["nature"] = {"label_fr":row["nature"], "label_en": None}
            dataset["environment"] = [{"label_fr":n.strip(), "label_en": translate(n.strip())} for n in row["environment"].split("/")]
            dataset["subthematic"] = [{"label_fr":n.strip(), "label_en": translate(n.strip())} for n in row["subthematic"].split("/")]
            dataset["exposure_factor_category"] = [{"label_fr":n.strip(), "label_en": translate(n.strip())} for n in row["exposure_factor_category"].split("/")]
            # this a simple copy for NOW
            dataset["exposure_factor"] = dataset["exposure_factor_category"]
            # TECH
            dataset["has_filter"] = bool(row["filter"])
            dataset["has_search_engine"] = bool(row["search_engine"])
            dataset["has_missing_data"] = bool(row['missing_data']!= "" and row['missing_data'] is not None and row["missing_data"] != "None")
            if dataset["has_missing_data"]: 
                dataset["missing_data_comments"] = [create_comment("admin", text=row["missing_data"])]
            dataset["has_documentation"] = bool(row['documentation']!= "" and row['documentation'] is not None and row["documentation"] != "None")
            if dataset["has_documentation"]: 
                dataset["documentation_comments"] = [create_comment("admin", text=row["documentation"])]
            
            dataset["is_downloadable"] = bool(row["downloadable"])
            dataset["broadcast_mode"] = [ {"label_fr":n.strip(), "label_en":None} for n in row["broadcast_mode"].split("/") ]
            dataset["files_format"] = [n.strip().title() for n in row["format"].split("/")]
            dataset["tech_comments"] = []
            # dataset["tech_comments"] = [create_comment("c24b", text="Commentaire sur l'accès technique")]
            #LEGAL
            dataset["license_name"] = {"label_fr":row["license_name"], "label_en": None}
            dataset["license_type"] = [{"label_fr":n, "label_en": n} for n in row["license_type"].split("/")]
            dataset["has_pricing"] = bool(row['pricing']!= "Gratuit")
            if row['pricing']!= "Gratuit":

                dataset["legal_comments"] = [
                    create_comment("c24b", text=row["pricing"])]
            else:
                dataset["legal_comments"] = []
            dataset["has_restriction"] = bool(row['restrictions']!= "")
            if dataset["has_restriction"]: 
                dataset["restrictions_comments"] = [create_comment("admin", text=row["restrictions"])]
            dataset["has_compliance"] = bool(row['compliance']!= "")
            if dataset["has_compliance"]: 
                dataset["compliance_comments"] = [create_comment("admin", text=row["compliance"])]
            #GEO
            dataset["is_geospatial_data"] = bool(row["geospatial_data"])
            if dataset["is_geospatial_data"]:
                dataset["administrative_territory_coverage"] = [n.strip() for n in row["administrative_territory_coverage"].split(",")]
                dataset["geospatial_geographical_coverage"] = row["geographical_geospatial_coverage"].split("+")
                dataset["geographical_information_level"] = [{"label_fr":v.strip(), "label_en":translate(v.strip())} for v in row["geographical_information_level"].split("/")]
                dataset["projection_system"] = [n.strip() for n in row["projection_system"].split("/")]
                dataset["related_geographical_information"] = bool(row["related_geographical_information"] == "")
            if row["related_geographical_information"] != "":
                dataset["geo_comments"] = [create_comment("c24b", text=row["related_geographical_information"])]
            else:
                dataset["geo_comments"] = []
            #TIME
            dataset["year"] = [n.strip() for n in row["year"].split("-")]
            dataset["temporal_scale"] = [v.strip() for v in row["temporal_scale"].split("/")]
            dataset["update_frequency"] = {"label_fr":row["update_frequency"], "label_en": translate(row["update_frequency"])}
            if row["automatic_update"] == "false":
                dataset["automatic_update"] = False
            if row["automatic_update"] == "true":
                dataset["automatic_update"] = False
            if row["automatic_update"] == "":
                dataset["automatic_update"] = None
            # ADMIN
            dataset["last_updated"] = row["last_updated"]
            dataset["last_inserted"]= row["last_inserted"]
            dataset["last_modification"] = row["last_modification"]
            dataset["related_referentials"] = [v.strip() for v in row["related_referentials"].split("|")]
            dataset["other_access_points"] = [v.strip() for v in row["other_access_points"].split("|")]
            # dataset["context_comments"] = [create_comment("admin", text="Commentaire sur le contexte de production du dataset")]
            dataset["context_comments"] = []
            dataset["comments"] = [create_comment("admin", text=row["comment"])]
            ds = DB.datasets.insert_one(dataset)
            created_datasets.append(ds.inserted_id)
    for id in created_datasets:
        DB.logs.insert_one(create_logs("admin", "create", "dataset", True, "OK", scope=None, ref_id=id))

def link_organizations_to_datasets():
    not_found_orgs = []
    for dataset in DB.datasets.find({}, {"_id": 1, "organizations":1}):
        orgs = []
        for org in dataset["organizations"]:
            existing_org = DB.organizations.find_one({"name": org["name"]})
            
            if existing_org is None:
                not_found_orgs.append(org["name"])
                DB.logs.insert_one(create_logs("admin", "edit", "dataset", False, "Organization '{}' not found".format(org["name"]), scope="organizations", ref_id=dataset["_id"]))
            else:
                orgs.append(existing_org)
        log = create_logs("admin", "edit", "dataset", True, "OK", scope="organizations", ref_id=dataset["_id"])
        DB.datasets.update_one({"_id": dataset["_id"]},{"$set": {"organizations":orgs}})
        DB.logs.insert_one(log)
    print("Missing orgs ", set(not_found_orgs))
    
def register_dataset_comments():
    dataset = DB.datasets.find_one()
    comments_fields =  {key:1 for key in dataset if "comment" in key}
    comments_fields["_id"] = 1
    for dataset in DB.datasets.find({}, comments_fields):
        dataset_id = dataset["_id"]
        del dataset["_id"]
        for k,v in dataset.items():
            for c in v:
                register_comment(c, "dataset", k, dataset_id)

def translate_datasets():
    for dataset in DB.datasets.find({}):
        for k,v in dataset.items():
            if isinstance(v, dict):
                if v["label_en"] is None and v["label_fr"] is not None:
                    status, ref = find_reference_by_label_fr("ref_"+k, v["label_fr"])
                    if status:
                        v["label_en"] = ref["label_en"]
                    else:
                        v["label_en"] = translate(v["label_fr"])
                    DB.datasets.update_one({"_id": dataset["_id"]}, {"$set": {k:v}})
                    
                    continue
                elif v["label_fr"] is None and v["label_en"] is not None:
                    status, ref = find_reference_by_label_fr("ref_"+k, v["label_en"])
                    if status:
                        v["label_fr"] = ref["label_fr"]
                    else:
                        v["label_fr"] = translate(l["label_en"])
                    DB.datasets.update_one({"_id": dataset["_id"]}, {"$set": {k:v}})            
                    continue
                
            if isinstance(v, list):
                update = False
                if k not in ["organizations"]:
                    for l in v:    
                        if isinstance(l, dict):    
                            if l["label_en"] is None and l["label_fr"] is not None:
                                status, ref = find_reference_by_label_fr("ref_"+k, l["label_fr"])
                                if status:
                                    l["label_en"] = ref["label_en"]
                                else:
                                    l["label_en"] = translate(l["label_fr"])
                                update = True
                            elif l["label_fr"] is None and l["label_en"] is not None:
                                status, ref = find_reference_by_label_fr("ref_"+k, v["label_en"])
                                if status:
                                    l["label_fr"] = ref["label_fr"]
                                else:
                                    l["label_fr"] = translate(l["label_en"])
                                update = True
                if update:
                    DB.datasets.update_one({"_id": dataset["_id"]}, {"$set": {k:v}})            
                    continue
def translate_fr_references():
    print("Translate references from FR > EN")
    for tablename in DB.references.distinct("tablename"):
        for ref_value in DB[tablename].find({"$or":[{"label_en": ""},{"label_en": None}], "label_fr":{"$nin": ["", None]}}, {"_id":1, "label_fr":1}):
            try: 
                value_en = translate(ref_value["label_fr"], _from="fr")
                DB[tablename].update_one({"_id": ref_value["_id"]}, {"$set": {"label_en": value_en} })
            except KeyError:
                pass
def translate_en_references():
    print("Translate references from EN > FR")
    for tablename in DB.references.distinct("tablename"):
        for ref_value in DB[tablename].find({"$or":[{"label_fr": ""},{"label_fr": None}], "label_en":{"$nin": ["", None]}}, {"_id":1, "label_en":1}):
            try: 
                
                value_fr = translate(ref_value["label_en"], _from="en")
                DB[tablename].update_one({"_id": ref_value["_id"]}, {"$set": {"label_fr": value_fr} })
            except KeyError:
                pass

def translate_missing_references():
    for tablename in DB.references.distinct("tablename"):
        for ref_value in DB[tablename].find({"$or":[{"label_en": ""},{"label_en": None}], "label_fr":{"$nin": ["", None]}}, {"_id":1, "label_fr":1}):
            try: 
                value_en = translate(ref_value["label_fr"], _from="fr")
                DB[tablename].update_one({"_id": ref_value["_id"]}, {"$set": {"label_en": value_en} })
            except KeyError:
                pass
    for tablename in DB.references.distinct("tablename"):
        for ref_value in DB[tablename].find({"$or":[{"label_fr": ""},{"label_fr": None}], "label_en":{"$nin": ["", None]}}, {"_id":1, "label_en":1}):
            try: 
                
                value_fr = translate(ref_value["label_en"], _from="en")
                DB[tablename].update_one({"_id": ref_value["_id"]}, {"$set": {"label_fr": value_fr} })
            except KeyError:
                pass
def create_default_users():
    default_users = [{
        "email": "constance.de-quatrebarbes@developpement-durable.gouv.fr", 
        "first_name": "Constance", 
        "last_name": "de Quatrebarbes", 
        "username": "c24b",
        "organization": "GD4H",
        "roles": ["admin", "expert"],
        "is_active": True, 
        "is_superuser": True,
        "lang": "fr"
    },{
        "email": "gd4h-catalogue@developpement-durable.gouv.fr", 
        "first_name": "GD4H", 
        "last_name": "Catalogue", 
        "username": "admin",
        "organization": "GD4H",
        "roles": ["admin", "expert"],
        "is_active": True, 
        "is_superuser": True,
        "lang": "fr"
    }]
    _id = DB.users.insert_many(default_users)
    create_logs("admin", action="create", perimeter="user",status=True, message="OK", scope=None, ref_id=_id.inserted_ids )
    pipeline = [ {'$project': {"id": {'$toString': "$_id"}, "_id": 0,"value": 1}}]
    DB.users.aggregate(pipeline)
    # print(_id.inserted_ids)
    return _id.inserted_ids 

def create_comment(username, text="Ceci est un commentaire test"):
    default_user = DB.users.find_one({"username": username}, {"username": 1, "lang": 1})
    if default_user is None:
        raise Exception(username, "not found")
    default_lang = default_user["lang"]
    clean_text = bleach.linkify(bleach.clean(text))
    alternate_lang = SWITCH_LANGS[default_lang]
    alternate_text = translate(clean_text, _from=default_lang)
    comment = {"label_"+default_lang: clean_text, "label_"+alternate_lang: alternate_text, "date":datetime.datetime.now(), "user": default_user["username"]}
    return comment

def register_comment(comment, perimeter, scope, ref_id):
    comment["perimeter"] = perimeter
    comment["scope"] = scope #field
    comment["ref_id"] = ref_id
    DB.comments.insert_one(comment)
    


def create_logs(username, action, perimeter, status=True,  message="OK", scope=None, ref_id=None):
    default_user = DB.users.find_one({"username": username}, {"username":1})
    default_lang = "en"
    default_label = "label_en"
    ref_perimeter = DB["ref_perimeter"].find_one({default_label: perimeter}, {"_id":0} )
    ref_action = DB["ref_action"].find_one({default_label: perimeter}, {"_id":0})
    try:
        assert ref_perimeter is not None
    except AssertionError:
        raise ValueError(f"Log has no perimeter :'{perimeter}'")
        assert ref_action is not None
    except AssertionError:
        raise ValueError(f"Log has no action {perimeter}")
    return {
                "user": username,
                "action": action,
                "perimeter": perimeter,
                "scope": scope,
                "ref_id": ref_id, 
                "date": datetime.datetime.now(),
                "status": status,
                "message": message
            }

def init_data():
    DB.organizations.drop()
    import_organizations()
    DB.datasets.drop()
    import_dataset()
    link_dataset2organizations()
    register_comments()

