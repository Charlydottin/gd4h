
def create_json_model():
    '''generate JSON empty file from rules table'''
    rules = [rule for rule in DB["rules"].find({},{})]

    final_models = {}
    for  model_name, field_rules in itertools.groupby(rules, key=lambda x:x["model"]):
        print(model_name)
        field_rules = list(field_rules)
        is_multilang_model = any([r["translation"] for r in field_rules])
        if is_multilang_model:
            for lang in AVAILABLE_LANG:
                root_schema = {
                "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
                "name": f"{model_name}_{lang}",
                "title": "{} - {}".format(model_name.title(), lang),
                "description": f"Spécification du modèle de données {model_name} relatif au catalogue des jeux de données Santé Environnement du GD4H",
                "contributors": [
                    {
                    "title": "GD4H",
                    "role": "author"
                    },
                    {
                    "title": "Constance de Quatrebarbes",
                    "role": "contributor"
                    }
                ],
                "version": "0.0.1",
                "created": "2022-01-28",
                "lastModified": "2022-01-28",
                "homepage": "https://github.com/c24b/gd4h/",
                "$id": f"{model_name}_{lang}-schema.json",
                "path": f"https://github.com/c24b/gd4h/catalogue/raw/v0.0.1/{model_name}_{lang}-schema.json",
                "type":object,
                "properties":[

                ]
                }
                for rule in field_rules:
                    root_schema["properties"].append(gen_json_item(rule, lang))
                yield root_schema
                root_schema["properties"] = []
        else:
            root_schema = {
                "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
                "name": f"{model_name}",
                "title": f"{model_name.title()} Simplifié",
                "description": f"Spécification du modèle de données {model_name.title()} relatif au catalogue des jeux de données Santé Environnement du GD4H",
                "contributors": [
                    {
                    "title": "GD4H",
                    "role": "author"
                    },
                    {
                    "title": "Constance de Quatrebarbes",
                    "role": "contributor"
                    }
                ],
                "$id": f"{model_name}-schema.json",
                "version": "0.0.1",
                "created": "2022-01-28",
                "lastModified": "2022-01-28",
                "homepage": "https://github.com/c24b/gd4h/",
                "path": f"https://github.com/c24b/gd4h/catalogue/raw/v0.0.1/{model_name}-schema.json".format(model_name),
                "properties":[

                ]
            }
            for rule in field_rules:
                root_schema["properties"].append(gen_json_item(rule, "en"))
            yield root_schema
    
def write_json_model():
    for json_schema in create_json_model():
        with open(os.path.join(data_dir, "schemas", json_schema["$id"]), "w") as f:
            f.write(json.dumps(json_schema, indent=4))
            print(json_schema["$id"], "ready!")
