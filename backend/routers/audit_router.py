from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import AuditLog, User
from auth import get_current_user
from schemas import AuditLogOut

router = APIRouter(prefix="/api/audit-logs", tags=["审计"])


@router.get("", response_model=list[AuditLogOut])
def list_audit_logs(target_type: str = None, target_id: int = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(AuditLog)
    if target_type:
        q = q.filter(AuditLog.target_type == target_type)
    if target_id:
        q = q.filter(AuditLog.target_id == target_id)
    logs = q.order_by(AuditLog.created_at.desc()).limit(200).all()
    result = []
    for log in logs:
        user = db.query(User).filter(User.id == log.user_id).first()
        result.append(AuditLogOut(
            id=log.id,
            user_id=log.user_id,
            user_name=user.real_name if user else "",
            action=log.action,
            target_type=log.target_type,
            target_id=log.target_id,
            detail=log.detail,
            created_at=log.created_at,
        ))
    return result
