#references_model
from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, HttpUrl, EmailStr, AnyUrl
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class Lang(str, Enum):
    {%for lang in available_lang %}{{lang}} = "{{lang}}"
    {% endfor %}

{% for ref_name, ref_list in references.items() %}{% for lang in available_lang %}
class {{ref_name}}Enum{{lang.title()}}(str, Enum):
    {%for value in ref_list %}option_{{loop.index}}="{{value[lang]}}"
    {%endfor%}{%endfor%}
{%endfor%}    

class Reference(BaseModel):
    name_en: str
    name_fr: str
    uri: Optional[HttpUrl]
    slug: Optional[str]
    table_name: str
    