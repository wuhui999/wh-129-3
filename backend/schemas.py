from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserCreate(BaseModel):
    username: str
    password: str
    real_name: str
    role: str
    org_name: str = ""
    phone: str = ""


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    real_name: str
    role: str
    org_name: str
    phone: str


class BuildingCreate(BaseModel):
    name: str
    address: str
    heritage_level: str = "市级"
    description: str = ""


class BuildingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    address: str
    heritage_level: str
    description: str
    created_at: Optional[datetime] = None


class PermitCreate(BaseModel):
    building_id: int
    scaffold_scope: str
    start_date: str
    end_date: str
    plan_attachment: str = ""


class PermitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    building_id: int
    building_name: Optional[str] = None
    scaffold_scope: str
    start_date: str
    end_date: str
    constructor_id: int
    constructor_name: Optional[str] = None
    plan_attachment: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    heritage_approved: Optional[bool] = None
    safety_approved: Optional[bool] = None


class ApprovalCreate(BaseModel):
    approval_type: str
    result: str
    opinion: str = ""
    conditions: str = ""


class ApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    permit_id: int
    approver_id: int
    approver_name: Optional[str] = None
    approval_type: str
    result: str
    opinion: str
    conditions: str
    created_at: Optional[datetime] = None


class InspectionCreate(BaseModel):
    permit_id: int
    check_items: str
    result: str = "normal"
    photos: str = ""
    hazard_level: str = "none"
    remark: str = ""


class InspectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    permit_id: int
    inspector_id: int
    inspector_name: Optional[str] = None
    check_items: str
    result: str
    photos: str
    hazard_level: str
    remark: str
    inspected_at: Optional[datetime] = None


class HazardCreate(BaseModel):
    permit_id: int
    inspection_id: Optional[int] = None
    level: str
    description: str


class HazardAssign(BaseModel):
    assigned_to: int


class HazardRectify(BaseModel):
    rectify_result: str


class HazardRecheck(BaseModel):
    recheck_result: str


class HazardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    permit_id: int
    inspection_id: Optional[int] = None
    level: str
    description: str
    status: str
    assigned_to: Optional[int] = None
    assignee_name: Optional[str] = None
    rectify_result: str
    recheck_by: Optional[int] = None
    rechecker_name: Optional[str] = None
    recheck_result: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DemolitionCreate(BaseModel):
    permit_id: int
    demolish_date: str
    site_restored: int = 0


class DemolitionAccept(BaseModel):
    accept_opinion: str = ""
    accept_result: str = "accepted"


class DemolitionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    permit_id: int
    demolish_date: str
    site_restored: int
    restorer_id: Optional[int] = None
    restorer_name: Optional[str] = None
    acceptor_id: Optional[int] = None
    acceptor_name: Optional[str] = None
    accept_opinion: str
    accept_result: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    user_name: Optional[str] = None
    action: str
    target_type: str
    target_id: int
    detail: str
    created_at: Optional[datetime] = None
