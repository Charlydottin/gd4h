# Pipeline 


## init_db: from csv to mongodb table

- create rules DB
- 
Option: see Beanie as ODM

- create a document model using rules


## create_model: from mongodb table to pydantic

create_model building a dict from with rules and example

json schema example see Pydantic Doc Code Generation:


  - [x] add example value in rules.csv => init_db
  - [ ] add validator using rules => enum not working
  - [x] declare external ref as ref

```
validators = {
    'username_validator':
    validator('username')(username_alphanumeric)
}

UserModel = create_model(
    'UserModel',
    username=(str, ...),
    __validators__=validators
)
```

alternative in CLI datamodel code generator takes a jsonschema and create model.py
> https://github.com/koxudaxi/datamodel-code-generator
>

## populate initial data using rules table to control insertion


## Create API CRUD endpoint from Models


https://fastapi-crudrouter.awtkns.com/


## Create index

-
- See esengine is an ODM (Object Document Mapper) it maps Python classes in to Elasticsearch index/doc_type and object instances() in to Elasticsearch documents.


