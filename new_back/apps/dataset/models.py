from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, conint, HttpUrl, EmailStr, AnyUrl
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from apps.comment.models import Comment
from apps.organization.models import Organization
from pydantic import create_model

from apps.organization.models import (Organization, OrganizationEn)
from apps.reference.models import Broadcast_ModeEnumFr
from apps.reference.models import Data_DomainEnumFr
from apps.reference.models import SubthematicEnumEn
from apps.reference.models import NatureEnumFr
from apps.reference.models import License_TypeEnumFr
from apps.reference.models import Broadcast_ModeEnumEn
from apps.reference.models import Data_DomainEnumEn
from apps.reference.models import EnvironmentEnumFr
from apps.reference.models import License_NameEnumEn
from apps.reference.models import License_NameEnumFr
from apps.reference.models import License_TypeEnumEn
from apps.reference.models import EnvironmentEnumEn
from apps.reference.models import Theme_CategoryEnumFr
from apps.reference.models import Theme_CategoryEnumEn
from apps.reference.models import SubthematicEnumFr
from apps.reference.models import NatureEnumEn
from apps.reference.models import Exposure_Factor_CategoryEnumEn
from apps.reference.models import Dataset_TypeEnumEn
from apps.reference.models import Dataset_TypeEnumFr
from apps.reference.models import Exposure_Factor_CategoryEnumFr
from apps.reference.models import Contact_TypeEnumFr
from apps.reference.models import Data_FormatEnumFr
from apps.reference.models import Geographical_Geospatial_Information_LevelEnumFr
from apps.reference.models import Projection_SystemEnumFr

class FilterDatasetFr(BaseModel):
    organizations: Optional[List[Organization]] = []
    dataset_type: Optional[List[Dataset_TypeEnumFr]] = []
    environment: Optional[List[EnvironmentEnumFr]] = []
    nature: Optional[List[NatureEnumFr]] = []
    subthematic: Optional[List[SubthematicEnumFr]] = []
    exposure_factor: Optional[List[str]] = []
    exposure_factor_category: Optional[List[Exposure_Factor_CategoryEnumFr]] = []
    theme_category: Optional[List[Theme_CategoryEnumFr]] = []
    is_opendata: Optional[bool] = None
    license_name: Optional[List[License_NameEnumFr]] = []
    license_type: Optional[List[License_TypeEnumFr]] = []
    has_restrictions: Optional[bool] = None
    has_pricing: Optional[bool] = None
    has_compliance: Optional[bool] = None
    data_domain: Optional[List[Data_DomainEnumFr]] = []
    broadcast_mode: Optional[List[Broadcast_ModeEnumFr]] = []
    last_updated: Optional[datetime] = None
    downloadable: Optional[bool] = None
    has_documentation: Optional[bool] = None
    has_filter: Optional[bool] = None
    has_missing_data: Optional[bool] = None
    has_search_engine: Optional[bool] = None
    temporal_scale: Optional[List[str]] = []
    update_frequency: Optional[str] = None
    year: Optional[List[str]] = []
    is_geospatial_data: Optional[bool] = None
    

class Dataset(BaseModel):
    id: Optional[str] = None
    integration_status: Optional[bool] = None
    state: Optional[bool] = None
    last_inserted: Optional[datetime] = None
    last_modification: Optional[datetime] = None
    name: str
    acronym: Optional[str] = None
    organizations: Optional[List[Organization]] = []
    description: str
    url: HttpUrl
    contact_type: List[Contact_TypeEnumFr] = []
    contact: List[str] = []
    contact_type_comments: List[Comment] = []
    dataset_type: str
    environment: List[EnvironmentEnumFr] = []
    nature: Optional[NatureEnumFr] = None
    subthematic: List[SubthematicEnumFr] = []
    exposure_factor: List[str] = []
    exposure_factor_category: List[Exposure_Factor_CategoryEnumFr]
    theme_category: Optional[Theme_CategoryEnumFr] = None
    is_opendata: bool
    license_name: Optional[License_NameEnumFr] = None
    license_type: List[License_TypeEnumFr] = []
    has_restrictions: Optional[bool] = None
    restrictions_comments: List[Comment] = []
    has_pricing: Optional[bool] = None
    has_compliance: Optional[bool] = None
    pricing_comments: List[Comment] = []
    compliance_comments: List[Comment] = []
    data_format: List[Data_FormatEnumFr] = []
    other_access_points: List[str] = []
    data_domain: str
    related_referential: List[str] = []
    related_datasets: List[Dataset] = []
    automatic_update: Optional[bool] = None
    broadcast_mode: List[Broadcast_ModeEnumFr] = []
    documentation_comments: List[Comment] = []
    last_updated: Optional[datetime] = None
    downloadable: Optional[bool] = None
    has_documentation: Optional[bool] = None
    has_filter: Optional[bool] = None
    has_missing_data: Optional[bool] = None
    has_search_engine: Optional[bool] = None
    missing_data_comments: List[Comment] = []
    technical_comments: List[Comment] = []
    temporal_scale: List[str] = []
    update_frequency: Optional[str] = None
    volume: Optional[str] = None
    year: List[str] = []
    is_geospatial_data: Optional[bool] = None
    administrative_territory_coverage: List[str] = []
    geographical_information_level: List[Geographical_Geospatial_Information_LevelEnumFr] = []
    projection_system: List[Projection_SystemEnumFr] = []
    related_geographical_information: Optional[bool] = None
    geographical_geospatial_coverage: List[str] = []
    geospatial_comments: List[Comment] = []
    comments: List[Comment] = []
    qualification_comments: List[Comment] = []
    context_comments: List[Comment] = []
    

Dataset.update_forward_refs()







