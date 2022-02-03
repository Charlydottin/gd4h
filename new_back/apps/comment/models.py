from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, conint, HttpUrl, EmailStr, AnyUrl
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime












class Comment(BaseModel):
    id: Optional[str] = None
    text: str
    scope: str
    user: dict
    date: datetime
    




