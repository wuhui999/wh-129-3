from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Permit, Demolition, AuditLog, PermitStatus, UserRole
from auth import get_current_user, require_role
from schemas import DemolitionCreate, DemolitionAccept, DemolitionOut

router = APIRouter(prefix="/api/demolitions", tags=["拆除验收"])


def _demolition_to_out(d, db):
    restorer = db.query(User).filter(User.id == d.restorer_id).first() if d.restorer_id else None
    acceptor = db.query(User).filter(User.id == d.acceptor_id).first() if d.acceptor_id else None
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
        accept_result=d.accept_result,
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
    d.acceptor_id = current_user.id
    d.accept_opinion = req.accept_opinion
    d.accept_result = req.accept_result
    db.commit()
    if req.accept_result == "accepted":
        permit = db.query(Permit).filter(Permit.id == d.permit_id).first()
        if permit:
            permit.status = PermitStatus.accepted.value
            db.commit()
    log = AuditLog(user_id=current_user.id, action=f"验收{'通过' if req.accept_result == 'accepted' else '不通过'}", target_type="demolition", target_id=d.id)
    db.add(log)
    db.commit()
    return _demolition_to_out(d, db)
