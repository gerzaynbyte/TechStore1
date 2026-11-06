# src/security_pia.py

def can_cancel_pia(status, owner_id, user_id, is_admin, created_at, now=None):
    """RN-11 TechStore: Cancelación dentro de 2 horas desde confirmación.
    
    Estados permitidos: "Pago confirmado", "En preparación".
    Ventana: < 2 horas desde created_at.
    Admin puede cancelar siempre en estos estados (excepto En tránsito).
    """
    if now is None:
        from datetime import UTC, datetime
        now = datetime.now(UTC)
    
    # Estados donde la cancelación está permitida por la regla
    PERMITTED_STATES = {"Pago confirmado", "En preparación"}
    
    # Estados donde NO se permite cancelación (solo devolución posterior)
    if status not in PERMITTED_STATES:
        return False
    
    # Administrador puede cancelar en estos estados
    if is_admin:
        return True
    
    # Propietario: solo dentro de 2 horas (comparación estricta)
    if owner_id == user_id:
        from datetime import timedelta
        return now - created_at < timedelta(hours=2)
    
    # No propietario y no admin → denegado
    return False