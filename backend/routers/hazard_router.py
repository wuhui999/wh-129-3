from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Hazard, Permit, AuditLog, HazardStatus, HazardLevel, PermitStatus, UserRole
from auth import get_current_user, require_role
from schemas import HazardCreate, HazardAssign, HazardRectify, HazardRecheck, HazardOut

router = APIRouter(prefix="/api/hazards", tags=["隐患"])


def _hazard_to_out(h, db):
    assignee = db.query(User).filter(User.id == h.assigned_to).first() if h.assigned_to else None
    rechecker = db.query(User).filter(User.id == h.recheck_by).first() if h.recheck_by else None
    return HazardOut(
        id=h.id,
        permit_id=h.permit_id,
        inspection_id=h.inspection_id,
        level=h.level,
        description=h.description,
        status=h.status,
        assigned_to=h.assigned_to,
        assignee_name=assignee.real_name if assignee else None,
        rectify_result=h.rectify_result,
        recheck_by=h.recheck_by,
        rechecker_name=rechecker.real_name if rechecker else None,
        recheck_result=h.recheck_result,
        created_at=h.created_at,
        updated_at=h.updated_at,
    )


@router.get("", response_model=list[HazardOut])
def list_hazards(permit_id: int = None, status: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Hazard)
    if permit_id:
        q = q.filter(Hazard.permit_id == permit_id)
    if status:
        q = q.filter(Hazard.status == status)
    hazards = q.order_by(Hazard.created_at.desc()).all()
    return [_hazard_to_out(h, db) for h in hazards]


@router.post("", response_model=HazardOut)
def create_hazard(req: HazardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    permit = db.query(Permit).filter(Permit.id == req.permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail="许可不存在")
    h = Hazard(
        permit_id=req.permit_id,
        inspection_id=req.inspection_id,
        level=req.level,
        description=req.description,
        status=HazardStatus.open.value,
    )
    db.add(h)
    db.commit()
    db.refresh(h)
    log = AuditLog(user_id=current_user.id, action="创建隐患", target_type="hazard", target_id=h.id, detail=f"等级:{req.level}")
    db.add(log)
    db.commit()
    return _hazard_to_out(h, db)


@router.put("/{hazard_id}/assign", response_model=HazardOut)
def assign_hazard(hazard_id: int, req: HazardAssign, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    h = db.query(Hazard).filter(Hazard.id == hazard_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="隐患不存在")
    if h.status != HazardStatus.open.value:
        raise HTTPException(status_code=400, detail="当前状态不可派单")
    h.assigned_to = req.assigned_to
    h.status = HazardStatus.assigned.value
    db.commit()
    log = AuditLog(user_id=current_user.id, action="派单隐患", target_type="hazard", target_id=h.id, detail=f"派给:{req.assigned_to}")
    db.add(log)
    db.commit()
    return _hazard_to_out(h, db)


@router.put("/{hazard_id}/rectify", response_model=HazardOut)
def rectify_hazard(hazard_id: int, req: HazardRectify, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    h = db.query(Hazard).filter(Hazard.id == hazard_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="隐患不存在")
    if h.status not in [HazardStatus.assigned.value, HazardStatus.rectifying.value]:
        raise HTTPException(status_code=400, detail="当前状态不可整改")
    if h.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="只能整改派给自己的隐患")
    h.rectify_result = req.rectify_result
    h.status = HazardStatus.recheck.value
    db.commit()
    log = AuditLog(user_id=current_user.id, action="提交整改", target_type="hazard", target_id=h.id)
    db.add(log)
    db.commit()
    return _hazard_to_out(h, db)


@router.put("/{hazard_id}/recheck", response_model=HazardOut)
def recheck_hazard(hazard_id: int, req: HazardRecheck, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.inspector, UserRole.safety))):
    h = db.query(Hazard).filter(Hazard.id == hazard_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="隐患不存在")
    if h.status != HazardStatus.recheck.value:
        raise HTTPException(status_code=400, detail="当前状态不可复查")
    h.recheck_by = current_user.id
    h.recheck_result = req.recheck_result
    if req.recheck_result == "pass":
        h.status = HazardStatus.closed.value
    else:
        h.status = HazardStatus.assigned.value
    db.commit()
    log = AuditLog(user_id=current_user.id, action=f"复查{'通过' if req.recheck_result == 'pass' else '不通过'}", target_type="hazard", target_id=h.id)
    db.add(log)
    db.commit()
    return _hazard_to_out(h, db)
