from typing import Optional
import uuid
from pydantic import BaseModel, Field, HttpUrl, AnyHttpUrl, ValidationError, root_validator
from slugify import slugify


class PublisherModel(BaseModel):
    slug: str = Field(...)
    label_fr: str = Field(...)
    label_en: str = Field(...)
    adms_uri: AnyHttpUrl
    root_uri = AnyHttpUrl

