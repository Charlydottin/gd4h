from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, conint, HttpUrl, EmailStr, AnyUrl
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


from apps.user.models import UserFr
from apps.user.models import UserEn
from apps.reference.models import Agent_TypeEnumEn
from apps.reference.models import Organization_TypeEnumFr
from apps.reference.models import Agent_TypeEnumFr
from apps.reference.models import Organization_TypeEnumEn

class Organization(BaseModel):
    _id: Optional[str] = None
    organization_type: Organization_TypeEnumFr = Organization_TypeEnumFr.option_1
    acronym: Optional[str] = None
    agent_type: Agent_TypeEnumFr = Agent_TypeEnumFr.option_1
    image_url: Optional[HttpUrl] = None
    name: str
    url: Optional[HttpUrl]
    description: Optional[str] = None
    members: Optional[List[UserFr]] = []

class OrganizationEn(BaseModel):
    _id: Optional[str] = None
    organization_type: Organization_TypeEnumEn = Organization_TypeEnumEn.option_1
    acronym: Optional[str] = None
    agent_type: Agent_TypeEnumEn = Agent_TypeEnumEn.option_1
    image_url: Optional[HttpUrl] = None
    name: str
    url: Optional[HttpUrl]
    description: Optional[str] = None
    members: Optional[List[UserEn]] = []
    
class UpdateOrganizationFr(BaseModel):
    organization_type: Optional[Organization_TypeEnumFr] = None
    agent_type: Optional[Agent_TypeEnumFr] = None
    name: Optional[str] = None
    acronym: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    name: Optional[str]
    url: Optional[HttpUrl]
    description: Optional[str] = None

class UpdateOrganizationEn(BaseModel):
    organization_type: Optional[Organization_TypeEnumEn] = None
    agent_type: Optional[Agent_TypeEnumEn] = None
    name: Optional[str] = None
    acronym: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    name: Optional[str]
    url: Optional[HttpUrl]
    description: Optional[str] = None

class FilterOrganizationFr(BaseModel):
    organization_type: Optional[Organization_TypeEnumFr] = None
    agent_type: Optional[Agent_TypeEnumFr] = None
    name: Optional[str] = None
    

class FilterOrganizationEn(BaseModel):
    organization_type: Optional[Organization_TypeEnumEn] = None
    agent_type: Optional[Agent_TypeEnumEn] = None
    name: Optional[str] = None
    



Organization.update_forward_refs()

OrganizationEn.update_forward_refs()






