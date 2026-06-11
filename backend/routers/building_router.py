from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Building, Permit, Approval, AuditLog, UserRole, PermitStatus, ApprovalType
from auth import get_current_user, require_role
from schemas import BuildingCreate, BuildingOut, PermitCreate, PermitOut, ApprovalCreate, ApprovalOut

router = APIRouter(prefix="/api/buildings", tags=["建筑"])


@router.get("", response_model=list[BuildingOut])
def list_buildings(db: Session = Depends(get_db)):
    return db.query(Building).all()


@router.post("", response_model=BuildingOut)
def create_building(req: BuildingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    b = Building(**req.dict())
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


@router.get("/{building_id}", response_model=BuildingOut)
def get_building(building_id: int, db: Session = Depends(get_db)):
    b = db.query(Building).filter(Building.id == building_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="建筑不存在")
    return b
