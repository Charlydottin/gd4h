from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, conint, HttpUrl, EmailStr, AnyUrl
from enum import Enum
from typing import Optional
from datetime import datetime
from bson import ObjectId

class Comment(BaseModel):
    _id: Optional[str] = None
    text: str
    scope: Optional[str] = None
    perimeter: Optional[str] = None
    user: str = "admin"
    lang: str = "fr"
    date: Optional[datetime] = datetime.now()
    ref_id:  Optional[str] = None





