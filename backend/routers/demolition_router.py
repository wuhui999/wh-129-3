from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import User, Permit, Demolition, AuditLog, PermitStatus, UserRole
from auth import get_current_user, require_role
from schemas import DemolitionCreate, DemolitionAccept, DemolitionOut

router = APIRouter(prefix="/api/demolitions", tags=["拆除验收"])


def _demolition_to_out(d, db):
    restorer = db.query(User).filter(User.id == d.restorer_id).first() if d.restorer_id else None
    acceptor = db.query(User).filter(User.id == d.acceptor_id).first() if d.acceptor_id else None
    heritage_acceptor = db.query(User).filter(User.id == d.heritage_acceptor_id).first() if d.heritage_acceptor_id else None
    safety_acceptor = db.query(User).filter(User.id == d.safety_acceptor_id).first() if d.safety_acceptor_id else None
    heritage_result = d.heritage_result or "pending"
    safety_result = d.safety_result or "pending"
    if heritage_result == "pending" and safety_result == "pending" and d.accept_result != "pending":
        if d.acceptor_id:
            acceptor_user = db.query(User).filter(User.id == d.acceptor_id).first()
            if acceptor_user and acceptor_user.role == UserRole.heritage.value:
                heritage_result = d.accept_result
            if acceptor_user and acceptor_user.role == UserRole.safety.value:
                safety_result = d.accept_result
    overall_result = "pending"
    if heritage_result == "rejected" or safety_result == "rejected":
        overall_result = "rejected"
    elif heritage_result == "accepted" and safety_result == "accepted":
        overall_result = "accepted"
    return DemolitionOut(
        id=d.id,
        permit_id=d.permit_id,
        demolish_date=d.demolish_date,
        site_restored=d.site_restored,
        restorer_id=d.restorer_id,
        restorer_name=restorer.real_name if restorer else None,
        acceptor_id=d.acceptor_id,
        acceptor_name=acceptor.real_name if acceptor else None,
        accept_opinion=d.accept_opinion,
        accept_result=overall_result,
        heritage_acceptor_id=d.heritage_acceptor_id,
        heritage_acceptor_name=heritage_acceptor.real_name if heritage_acceptor else None,
        heritage_result=heritage_result,
        heritage_opinion=d.heritage_opinion or "",
        heritage_accepted_at=d.heritage_accepted_at,
        safety_acceptor_id=d.safety_acceptor_id,
        safety_acceptor_name=safety_acceptor.real_name if safety_acceptor else None,
        safety_result=safety_result,
        safety_opinion=d.safety_opinion or "",
        safety_accepted_at=d.safety_accepted_at,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )


@router.get("", response_model=list[DemolitionOut])
def list_demolitions(permit_id: int = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Demolition)
    if permit_id:
        q = q.filter(Demolition.permit_id == permit_id)
    demolitions = q.all()
    return [_demolition_to_out(d, db) for d in demolitions]


@router.post("", response_model=DemolitionOut)
def create_demolition(req: DemolitionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    permit = db.query(Permit).filter(Permit.id == req.permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail="许可不存在")
    if permit.status != PermitStatus.pending_demolish.value:
        raise HTTPException(status_code=400, detail="许可不在待拆除状态")
    existing = db.query(Demolition).filter(Demolition.permit_id == req.permit_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="已存在拆除记录")
    d = Demolition(
        permit_id=req.permit_id,
        demolish_date=req.demolish_date,
        site_restored=req.site_restored,
        restorer_id=current_user.id,
        heritage_result="pending",
        safety_result="pending",
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    log = AuditLog(user_id=current_user.id, action="提交拆除验收", target_type="demolition", target_id=d.id)
    db.add(log)
    db.commit()
    return _demolition_to_out(d, db)


@router.put("/{demolition_id}/confirm-restore")
def confirm_restore(demolition_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    d = db.query(Demolition).filter(Demolition.id == demolition_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="拆除记录不存在")
    d.site_restored = 1
    db.commit()
    log = AuditLog(user_id=current_user.id, action="确认现场恢复", target_type="demolition", target_id=d.id)
    db.add(log)
    db.commit()
    return {"message": "现场恢复已确认"}


@router.put("/{demolition_id}/accept", response_model=DemolitionOut)
def accept_demolition(demolition_id: int, req: DemolitionAccept, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.heritage, UserRole.safety))):
    d = db.query(Demolition).filter(Demolition.id == demolition_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="拆除记录不存在")
    if d.site_restored != 1:
        raise HTTPException(status_code=400, detail="现场尚未恢复确认")

    now = datetime.now()
    role_type = None
    if current_user.role == UserRole.heritage.value:
        role_type = "heritage"
        if d.heritage_result and d.heritage_result != "pending":
            raise HTTPException(status_code=400, detail="文保员已验收，不可重复提交")
        d.heritage_acceptor_id = current_user.id
        d.heritage_result = req.accept_result
        d.heritage_opinion = req.accept_opinion
        d.heritage_accepted_at = now
    elif current_user.role == UserRole.safety.value:
        role_type = "safety"
        if d.safety_result and d.safety_result != "pending":
            raise HTTPException(status_code=400, detail="安监员已验收，不可重复提交")
        d.safety_acceptor_id = current_user.id
        d.safety_result = req.accept_result
        d.safety_opinion = req.accept_opinion
        d.safety_accepted_at = now

    if not role_type:
        raise HTTPException(status_code=403, detail="仅文保员和安监员可进行验收")

    db.commit()

    heritage_ok = (d.heritage_result == "accepted")
    safety_ok = (d.safety_result == "accepted")
    heritage_rejected = (d.heritage_result == "rejected")
    safety_rejected = (d.safety_result == "rejected")

    permit = db.query(Permit).filter(Permit.id == d.permit_id).first()
    if permit:
        if heritage_rejected or safety_rejected:
            d.accept_result = "rejected"
            permit.status = PermitStatus.pending_demolish.value
        elif heritage_ok and safety_ok:
            d.accept_result = "accepted"
            permit.status = PermitStatus.accepted.value
        else:
            d.accept_result = "pending"
            permit.status = PermitStatus.pending_demolish.value
        db.commit()

    log = AuditLog(
        user_id=current_user.id,
        action=f"{'文保员' if role_type == 'heritage' else '安监员'}验收{'通过' if req.accept_result == 'accepted' else '不通过'}",
        target_type="demolition",
        target_id=d.id,
        detail=req.accept_opinion,
    )
    db.add(log)
    db.commit()

    return _demolition_to_out(d, db)
