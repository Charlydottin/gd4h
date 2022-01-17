
from pydantic import BaseModel, Field, HttpUrl, AnyHttpUrl, ValidationError, root_validator
from typing import Any, Optional
from pydantic.main import BaseModel
from typing import List



class CommentList(BaseModel):
    # id = str
    table_name:str
    scope:str
    field:str
    valid:bool

class UpdateCommentList(BaseModel):
    table_name:str
    scope:str
    field:str
    valid:bool

class CommentModel(BaseModel):
    table_name_id:str
    label_fr:str
    label_en:str
    uri:Optional[str]
    root_uri:Optional[str]

class UpdateCommentModel(BaseModel):
    label_fr:str
    label_en:str
    uri:Optional[str]
    root_uri:Optional[str]