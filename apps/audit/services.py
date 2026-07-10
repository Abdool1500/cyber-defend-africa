"""Sensitive-action audit logging. Call log_action() from any view/service
that performs one of: role change, suspension, question creation/edit,
quiz publication, grade change, certificate issuance/revocation, or a
sensitive setting change (spec section 97).

Never pass passwords, secret keys, or tokens in `metadata` — this table
is meant to be safe to review, export, and retain.
"""
from .models import AuditLog


def log_action(actor, action: str, entity, metadata: dict = None):
    AuditLog.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        entity_type=entity.__class__.__name__,
        entity_id=str(entity.pk),
        metadata=metadata or {},
    )
