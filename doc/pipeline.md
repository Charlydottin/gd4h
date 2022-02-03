# Pipeline 

## INIT

- import_rules
- import_reference

## CREATE BACK

- generate_models.py
- [x] solve FR EN routers
- [x] solve crud error 

- connect db to back

## POPULATE DB


## CREATE INDEX

## init_db: from csv to mongodb table

- create rules DB
- 
Option: see Beanie as ODM

- create a document model using rules


## create_model: from mongodb table to pydantic

1. Create json-schema from example

Option 1: json schema example see Pydantic Doc Code Generation:


  - [x] add example value in rules.csv => init_db
  - [x] add validator using rules => enum OK
  - [x] declare external ref as ref
  - [x] add external_validor and send them to create_model
```
validators = {
    'username_validator':
    validator('username')(username_alphanumeric)
}

UserModel = create_model(
    'UserModel',
    username=(str, ...),
    __validators__=validators
    __config__ = Config
)
```

BUT: no way to generate from model only import

Option 2: create json-schema with code using rules


2. Create pymodel.py

Option 1. use datamodel-code-generator
alternative in CLI datamodel code generator takes a jsonschema and create model.py
> https://github.com/koxudaxi/datamodel-code-generator

import models into back.apps
Not working 
Option2. convert jsonschemas to openapi

## populate initial data using rules table to control insertion


## Create API CRUD endpoint from Models


https://fastapi-crudrouter.awtkns.com/


## Create index

-
- See esengine is an ODM (Object Document Mapper) it maps Python classes in to Elasticsearch index/doc_type and object instances() in to Elasticsearch documents.


