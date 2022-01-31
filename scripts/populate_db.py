
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
