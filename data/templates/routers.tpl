#!/usr/bin/.env/python3.9
# file: routers.py

from fastapi_crudrouter import MemoryCRUDRouter as CRUDRouter
{% for route,lang,model in route_models %}
from .models import {{model}}
{%if lang in ["en", "fr"] %}
{{lang}}_router = CRUDRouter(schema={{model}})
{%else%}
router = CRUDRouter(schema={{model}})
{%endif%}
{%endfor%}