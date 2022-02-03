from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, conint, HttpUrl, EmailStr, AnyUrl
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime












class LicenseFr(BaseModel):
    license_name: Optional[str] = None
    license_type: List[str] = []
    is_opendata: bool
    license_description: Optional[str] = None
    id: Optional[str] = None
    




class LicenseEn(BaseModel):
    license_name: Optional[str] = None
    license_type: List[str] = []
    is_opendata: bool
    license_description: Optional[str] = None
    id: Optional[str] = None
    




