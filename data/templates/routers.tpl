#!/usr/bin/.env/python3.9
# file: routers.py

from fastapi_crudrouter import MemoryCRUDRouter as CRUDRouter{% for route,model in route_models %}
from .models import {{model}}

router = CRUDRouter(schema={{model}})
{%endfor%}