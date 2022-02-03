from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, conint, HttpUrl, EmailStr, AnyUrl
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime












class Log(BaseModel):
    id: str
    action: str
    perimeter: str
    user: str
    date: datetime
    




