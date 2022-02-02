from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, conint, HttpUrl, EmailStr, AnyUrl
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
{% for model_name,value_list in models %}
{% if model_name=="import_model" %}
{%for model,value in value_list %}from apps.{{model}}.models import {{value}}
{%endfor%}
{% elif model_name=="import_reference" %}
{%for model,value in value_list %}from apps.{{model}}.models import {{value}}
{%endfor%}
{%else%}

class {{model_name}}(BaseModel):
    {%for value in value_list %}{{value}}
    {%endfor%}
{%endif%}
{%endfor%}