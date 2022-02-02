from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
class Lang(str, Enum):
    {%for lang in available_lang %}{{lang}} = "{{lang}}"
    {% endfor %}

{% for ref_name, ref_list in references.items() %}{% for lang in available_lang %}
class {{ref_name}}Enum{{lang.title()}}(str, Enum):
    {%for value in ref_list %}option_{{loop.index}}="{{value[lang]}}"
    {%endfor%}
{%endfor%}{%endfor%}    

{% for model_name, value_list in models.items() %}
{% if model_name=="import" %}
{%for value in value_list %}import {{value}}
{%endfor%}
{%else%}
class {{model_name}}(BaseModel):
    {%for value in value_list %}{{value}}
    {%endfor%}
{%endif%}
{%endfor%}    
