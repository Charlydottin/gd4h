from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, conint, HttpUrl, EmailStr, AnyUrl
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime












class RoleFr(BaseModel):
    id: Optional[str] = None
    type: str
    action: List[str]
    perimeter: str
    




class RoleEn(BaseModel):
    id: Optional[str] = None
    type: str
    action: List[str]
    perimeter: str
    




