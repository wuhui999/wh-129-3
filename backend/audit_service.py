from models import AuditLog


def add_audit_log(db, user_id, action, target_type, target_id, detail=""):
    log = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
    )
    db.add(log)
    return log


def log_audit(db, user_id, action, target_type, target_id, detail=""):
    add_audit_log(db, user_id, action, target_type, target_id, detail)
    db.commit()
