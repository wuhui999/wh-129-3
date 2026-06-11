from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class UserRole(str, enum.Enum):
    constructor = "constructor"
    inspector = "inspector"
    heritage = "heritage"
    safety = "safety"


class PermitStatus(str, enum.Enum):
    applied = "applied"
    approving = "approving"
    can_scaffold = "can_scaffold"
    in_use = "in_use"
    pending_demolish = "pending_demolish"
    accepted = "accepted"
    rejected = "rejected"


class HazardLevel(str, enum.Enum):
    minor = "minor"
    major = "major"
    critical = "critical"


class HazardStatus(str, enum.Enum):
    open = "open"
    assigned = "assigned"
    rectifying = "rectifying"
    recheck = "recheck"
    closed = "closed"


class ApprovalType(str, enum.Enum):
    heritage = "heritage"
    safety = "safety"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    real_name = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False)
    org_name = Column(String(100), default="")
    phone = Column(String(20), default="")
    created_at = Column(DateTime, default=datetime.now)


class Building(Base):
    __tablename__ = "buildings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    heritage_level = Column(String(20), default="市级")
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)


class Permit(Base):
    __tablename__ = "permits"
    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    scaffold_scope = Column(Text, nullable=False)
    start_date = Column(String(20), nullable=False)
    end_date = Column(String(20), nullable=False)
    constructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_attachment = Column(String(500), default="")
    status = Column(String(20), default=PermitStatus.applied.value)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    building = relationship("Building")
    constructor = relationship("User")


class Approval(Base):
    __tablename__ = "approvals"
    id = Column(Integer, primary_key=True, index=True)
    permit_id = Column(Integer, ForeignKey("permits.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approval_type = Column(String(20), nullable=False)
    result = Column(String(20), nullable=False)
    opinion = Column(Text, default="")
    conditions = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)
    approver = relationship("User")


class Inspection(Base):
    __tablename__ = "inspections"
    id = Column(Integer, primary_key=True, index=True)
    permit_id = Column(Integer, ForeignKey("permits.id"), nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    check_items = Column(Text, nullable=False)
    result = Column(String(20), default="normal")
    photos = Column(Text, default="")
    hazard_level = Column(String(20), default="none")
    remark = Column(Text, default="")
    inspected_at = Column(DateTime, default=datetime.now)
    inspector = relationship("User")


class Hazard(Base):
    __tablename__ = "hazards"
    id = Column(Integer, primary_key=True, index=True)
    permit_id = Column(Integer, ForeignKey("permits.id"), nullable=False)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=True)
    level = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default=HazardStatus.open.value)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    rectify_result = Column(Text, default="")
    recheck_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    recheck_result = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    assignee = relationship("User", foreign_keys=[assigned_to])
    rechecker = relationship("User", foreign_keys=[recheck_by])


class Demolition(Base):
    __tablename__ = "demolitions"
    id = Column(Integer, primary_key=True, index=True)
    permit_id = Column(Integer, ForeignKey("permits.id"), nullable=False)
    demolish_date = Column(String(20), nullable=False)
    site_restored = Column(Integer, default=0)
    restorer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    acceptor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    accept_opinion = Column(Text, default="")
    accept_result = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    restorer = relationship("User", foreign_keys=[restorer_id])
    acceptor = relationship("User", foreign_keys=[acceptor_id])


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False)
    detail = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)
    user = relationship("User")
