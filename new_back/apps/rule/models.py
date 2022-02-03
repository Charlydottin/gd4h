from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, conint, HttpUrl, EmailStr, AnyUrl
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class Rule(BaseModel):
    _id: ObjectId = None
    slug: str = None
    model: str = None
    field_id: str = None
    name_fr: str = None
    name_en: str = None
    section: str = None
    external_model: str = None
    external_model_display_keys: str = None
    is_controled: bool = None
    reference_table: str = None
    vocab: str = None
    translation: bool = None
    multiple: bool = None
    constraint: str = None
    datatype: str = None
    is_indexed: bool = None
    is_facet: bool = None
    ADMIN_scope_order: int = None
    LIST_order: int = None
    ITEM_order: int = None
    FILTER_order: int = None
    mandatory: bool = None
    editable: bool = None
    commentable: bool = None
    description_fr: str = None
    description_en: str = None
    example_fr: str = None
    example_en: str = None
    




