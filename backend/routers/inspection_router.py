from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from models import User, Permit, Inspection, AuditLog, PermitStatus, UserRole
from auth import get_current_user, require_role
from schemas import InspectionCreate, InspectionOut

router = APIRouter(prefix="/api/inspections", tags=["巡检"])


def _inspection_to_out(insp, db):
    inspector = db.query(User).filter(User.id == insp.inspector_id).first()
    return InspectionOut(
        id=insp.id,
        permit_id=insp.permit_id,
        inspector_id=insp.inspector_id,
        inspector_name=inspector.real_name if inspector else "",
        check_items=insp.check_items,
        result=insp.result,
        photos=insp.photos,
        hazard_level=insp.hazard_level,
        remark=insp.remark,
        inspected_at=insp.inspected_at,
    )


@router.get("", response_model=list[InspectionOut])
def list_inspections(permit_id: int = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Inspection)
    if permit_id:
        q = q.filter(Inspection.permit_id == permit_id)
    inspections = q.order_by(Inspection.inspected_at.desc()).all()
    return [_inspection_to_out(i, db) for i in inspections]


@router.post("", response_model=InspectionOut)
def create_inspection(req: InspectionCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.inspector))):
    permit = db.query(Permit).filter(Permit.id == req.permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail="许可不存在")
    if permit.status not in [PermitStatus.can_scaffold.value, PermitStatus.in_use.value]:
        raise HTTPException(status_code=400, detail="当前许可状态不可巡检")
    insp = Inspection(
        permit_id=req.permit_id,
        inspector_id=current_user.id,
        check_items=req.check_items,
        result=req.result,
        photos=req.photos,
        hazard_level=req.hazard_level,
        remark=req.remark,
    )
    db.add(insp)
    db.commit()
    db.refresh(insp)
    log = AuditLog(user_id=current_user.id, action="提交巡检记录", target_type="inspection", target_id=insp.id)
    db.add(log)
    db.commit()
    return _inspection_to_out(insp, db)


@router.get("/overdue-alert")
def overdue_alert(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    in_use_permits = db.query(Permit).filter(Permit.status == PermitStatus.in_use.value).all()
    alerts = []
    for p in in_use_permits:
        last_insp = db.query(Inspection).filter(Inspection.permit_id == p.id).order_by(Inspection.inspected_at.desc()).first()
        if not last_insp or (datetime.now() - last_insp.inspected_at) > timedelta(days=1):
            alerts.append({
                "permit_id": p.id,
                "building_name": p.building.name if p.building else "",
                "last_inspected": last_insp.inspected_at.isoformat() if last_insp else None,
                "overdue_hours": int((datetime.now() - last_insp.inspected_at).total_seconds() / 3600) if last_insp else None,
            })
    return {"alerts": alerts}
