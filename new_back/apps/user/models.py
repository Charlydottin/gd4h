from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, conint, HttpUrl, EmailStr, AnyUrl
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


from apps.role.models import RoleFr
from apps.role.models import RoleEn










class UserFr(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    role: List[RoleFr]
    




class UserEn(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    role: List[RoleEn]
    





UserFr.update_forward_refs()

UserEn.update_forward_refs()






