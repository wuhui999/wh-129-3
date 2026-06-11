from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import User, Permit, Approval, Hazard, AuditLog, UserRole, PermitStatus, HazardStatus, HazardLevel
from auth import get_current_user, require_role
from schemas import PermitCreate, PermitOut, ApprovalCreate, ApprovalOut

router = APIRouter(prefix="/api/permits", tags=["许可"])


def _permit_to_out(p, db):
    heritage_app = db.query(Approval).filter(Approval.permit_id == p.id, Approval.approval_type == "heritage").first()
    safety_app = db.query(Approval).filter(Approval.permit_id == p.id, Approval.approval_type == "safety").first()
    return PermitOut(
        id=p.id,
        building_id=p.building_id,
        building_name=p.building.name if p.building else None,
        scaffold_scope=p.scaffold_scope,
        start_date=p.start_date,
        end_date=p.end_date,
        constructor_id=p.constructor_id,
        constructor_name=p.constructor.real_name if p.constructor else None,
        plan_attachment=p.plan_attachment,
        status=p.status,
        created_at=p.created_at,
        updated_at=p.updated_at,
        heritage_approved=heritage_app.result == "approved" if heritage_app else False,
        safety_approved=safety_app.result == "approved" if safety_app else False,
    )


def _log_audit(db, user_id, action, target_type, target_id, detail=""):
    log = AuditLog(user_id=user_id, action=action, target_type=target_type, target_id=target_id, detail=detail)
    db.add(log)


@router.get("", response_model=list[PermitOut])
def list_permits(status: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Permit)
    if status:
        q = q.filter(Permit.status == status)
    if current_user.role == UserRole.constructor.value:
        q = q.filter(Permit.constructor_id == current_user.id)
    permits = q.all()
    return [_permit_to_out(p, db) for p in permits]


@router.post("", response_model=PermitOut)
def create_permit(req: PermitCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.constructor))):
    p = Permit(
        building_id=req.building_id,
        scaffold_scope=req.scaffold_scope,
        start_date=req.start_date,
        end_date=req.end_date,
        constructor_id=current_user.id,
        plan_attachment=req.plan_attachment,
        status=PermitStatus.applied.value,
    )
    db.add(p)
    db.flush()
    _log_audit(db, current_user.id, "提交许可申请", "permit", p.id, f"建筑ID:{req.building_id}")
    db.commit()
    db.refresh(p)
    return _permit_to_out(p, db)


@router.get("/{permit_id}", response_model=PermitOut)
def get_permit(permit_id: int, db: Session = Depends(get_db)):
    p = db.query(Permit).filter(Permit.id == permit_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="许可不存在")
    return _permit_to_out(p, db)


@router.put("/{permit_id}/submit", response_model=PermitOut)
def submit_for_approval(permit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Permit).filter(Permit.id == permit_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="许可不存在")
    if p.constructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能提交自己的许可")
    if p.status != PermitStatus.applied.value:
        raise HTTPException(status_code=400, detail="当前状态不可提交审批")
    p.status = PermitStatus.approving.value
    _log_audit(db, current_user.id, "提交审批", "permit", p.id)
    db.commit()
    return _permit_to_out(p, db)


@router.post("/{permit_id}/approve", response_model=ApprovalOut)
def approve_permit(permit_id: int, req: ApprovalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Permit).filter(Permit.id == permit_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="许可不存在")
    if p.status != PermitStatus.approving.value:
        raise HTTPException(status_code=400, detail="许可不在审批中")
    if req.approval_type == "heritage" and current_user.role != UserRole.heritage.value:
        raise HTTPException(status_code=403, detail="仅文保员可进行文保审批")
    if req.approval_type == "safety" and current_user.role != UserRole.safety.value:
        raise HTTPException(status_code=403, detail="仅安监员可进行安监审批")
    existing = db.query(Approval).filter(Approval.permit_id == permit_id, Approval.approval_type == req.approval_type).first()
    if existing:
        raise HTTPException(status_code=400, detail="已存在该类型的审批记录")
    approval = Approval(
        permit_id=permit_id,
        approver_id=current_user.id,
        approval_type=req.approval_type,
        result=req.result,
        opinion=req.opinion,
        conditions=req.conditions,
    )
    db.add(approval)
    db.flush()
    if req.result == "rejected":
        p.status = PermitStatus.rejected.value
    else:
        heritage_app = db.query(Approval).filter(Approval.permit_id == permit_id, Approval.approval_type == "heritage", Approval.result == "approved").first()
        safety_app = db.query(Approval).filter(Approval.permit_id == permit_id, Approval.approval_type == "safety", Approval.result == "approved").first()
        if heritage_app and safety_app:
            p.status = PermitStatus.can_scaffold.value
    db.commit()
    db.refresh(approval)
    _log_audit(db, current_user.id, f"{'通过' if req.result == 'approved' else '驳回'}审批", "permit", permit_id, f"类型:{req.approval_type}")
    db.commit()
    return ApprovalOut(
        id=approval.id,
        permit_id=approval.permit_id,
        approver_id=approval.approver_id,
        approver_name=current_user.real_name,
        approval_type=approval.approval_type,
        result=approval.result,
        opinion=approval.opinion,
        conditions=approval.conditions,
        created_at=approval.created_at,
    )


@router.get("/{permit_id}/approvals", response_model=list[ApprovalOut])
def get_approvals(permit_id: int, db: Session = Depends(get_db)):
    approvals = db.query(Approval).filter(Approval.permit_id == permit_id).all()
    result = []
    for a in approvals:
        approver = db.query(User).filter(User.id == a.approver_id).first()
        result.append(ApprovalOut(
            id=a.id, permit_id=a.permit_id, approver_id=a.approver_id,
            approver_name=approver.real_name if approver else "",
            approval_type=a.approval_type, result=a.result,
            opinion=a.opinion, conditions=a.conditions, created_at=a.created_at,
        ))
    return result


@router.put("/{permit_id}/start-use", response_model=PermitOut)
def start_use(permit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Permit).filter(Permit.id == permit_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="许可不存在")
    if p.status != PermitStatus.can_scaffold.value:
        raise HTTPException(status_code=400, detail="当前状态不可开始使用")
    p.status = PermitStatus.in_use.value
    _log_audit(db, current_user.id, "开始使用", "permit", permit_id)
    db.commit()
    return _permit_to_out(p, db)


@router.put("/{permit_id}/request-demolish", response_model=PermitOut)
def request_demolish(permit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Permit).filter(Permit.id == permit_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="许可不存在")
    if p.status != PermitStatus.in_use.value:
        raise HTTPException(status_code=400, detail="当前状态不可申请拆除")
    critical_open = db.query(Hazard).filter(
        Hazard.permit_id == permit_id,
        Hazard.level == HazardLevel.critical.value,
        Hazard.status != HazardStatus.closed.value,
    ).first()
    if critical_open:
        raise HTTPException(status_code=400, detail="存在未关闭的重大隐患，禁止申请拆除")
    p.status = PermitStatus.pending_demolish.value
    _log_audit(db, current_user.id, "申请拆除", "permit", permit_id)
    db.commit()
    return _permit_to_out(p, db)


@router.put("/{permit_id}/accept", response_model=PermitOut)
def accept_permit(permit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Permit).filter(Permit.id == permit_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="许可不存在")
    if p.status != PermitStatus.pending_demolish.value:
        raise HTTPException(status_code=400, detail="当前状态不可验收")
    p.status = PermitStatus.accepted.value
    _log_audit(db, current_user.id, "验收通过", "permit", permit_id)
    db.commit()
    return _permit_to_out(p, db)
