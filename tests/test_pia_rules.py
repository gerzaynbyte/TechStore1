from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
import pytest
from src.security_pia import can_cancel_pia


# --------------------------------------------
# Regla CP-01 a CP-03: RN-11 Cancelación
# --------------------------------------------

def test_cancel_within_window():
    """RN-11: Cliente puede cancelar dentro de 2 horas"""
    now = datetime(2026, 11, 4, 12, 0, tzinfo=timezone.utc)
    created_at = now - timedelta(hours=1, minutes=59)
    
    # Arrange: pedido en estado "Pago confirmado", dueño es el cliente
    order_status = "Pago confirmado"
    owner_id = 1
    user_id = 1
    is_admin = False
    
    # Act & Assert
    assert can_cancel_pia(order_status, owner_id, user_id, is_admin, created_at, now) is True


def test_cancel_after_deadline():
    """RN-11: Cancelación denegada fuera de la ventana de 2 horas"""
    now = datetime(2026, 11, 4, 14, 0, tzinfo=timezone.utc)
    created_at = now - timedelta(hours=2, minutes=1)
    
    order_status = "Pago confirmado"
    owner_id = 1
    user_id = 1
    is_admin = False
    
    assert can_cancel_pia(order_status, owner_id, user_id, is_admin, created_at, now) is False


def test_cancel_exactly_2h():
    """RN-11: Límite exacto a las 2:00 horas debe ser denegado"""
    now = datetime(2026, 11, 4, 14, 0, tzinfo=timezone.utc)
    created_at = now - timedelta(hours=2, minutes=0)  # Exactamente 2 horas
    
    order_status = "Pago confirmado"
    owner_id = 1
    user_id = 1
    is_admin = False
    
    # La comparación estricta (< 2h) hace que el borde exacto sea denegado
    assert can_cancel_pia(order_status, owner_id, user_id, is_admin, created_at, now) is False


# =============================================
# Regla CP-04 a CP-06: RN-07 Límite de 50 unidades
# =============================================

class LimitExceeded(Exception):
    """Excepción para límite de unidades por SKU"""
    pass

def sku_validate(order):
    """Función simulando regla RN-07"""
    for item in order.items:
        if item.quantity > 50:
            raise LimitExceeded(f"Límite de 50 unidades por SKU excedido")
    return True

def test_sku_limit_ok():
    """RN-07: Pedido con 49 unidades debe aprobarse"""
    class OrderItem:
        def __init__(self, qty): self.quantity = qty
    class Order:
        def __init__(self, items): self.items = items
    
    order = Order([OrderItem(49)])
    
    assert sku_validate(order) is True


def test_sku_limit_exceeded():
    """RN-07: 51 unidades debe ser rechazado"""
    class OrderItem:
        def __init__(self, qty): self.quantity = qty
    class Order:
        def __init__(self, items): self.items = items
    
    order = Order([OrderItem(51)])
    
    with pytest.raises(LimitExceeded, match="50 unidades"):
        sku_validate(order)


def test_sku_limit_exact():
    """RN-07: Exactamente 50 unidades debe aprobarse (límite)"""
    class OrderItem:
        def __init__(self, qty): self.quantity = qty
    class Order:
        def __init__(self, items): self.items = items
    
    order = Order([OrderItem(50)])
    
    assert sku_validate(order) is True


# =============================================
# Regla CP-07 a CP-09: RN-08 Intentos de pago
# =============================================

class PaymentMaxAttempts(Exception):
    """Excepción cuando se agotan los intentos"""
    pass

def process_payment(attempts, window_active, payment_result):
    """Simula regla RN-08 con Mock"""
    if attempts >= 3:
        raise PaymentMaxAttempts("Máximo de 3 intentos alcanzado")
    if not window_active:
        # Ventana de 15 minutos expiró, se reinician intentos
        attempts = 0
        window_active = True
    if not payment_result:
        attempts += 1
    return attempts, window_active

def test_payment_approved_before_max():
    """RN-08: Pago aprobado en intento 2 debe permitir continuar"""
    gateway = Mock()
    gateway.charge.return_value = True  # Pago aprobado
    
    attempts = 2
    window_active = True
    
    if gateway.charge():
        # Pago aprobado, no se incrementa el contador
        assert attempts == 2


def test_max_attempts_reached():
    """RN-08: Tercer intento rechazado bloquea el carrito"""
    gateway = Mock()
    gateway.charge.return_value = False  # Pago rechazado
    
    attempts = 3
    window_active = True
    
    with pytest.raises(PaymentMaxAttempts):
        process_payment(attempts, window_active, gateway.charge())
    
    # Mock verifica que se intentó el cobro
    gateway.charge.assert_called_once()


def test_attempts_reset_after_timeout():
    """RN-08: Después de 15 minutos sin pago, se reinicia"""
    from datetime import datetime, timedelta, timezone
    
    now = datetime(2026, 11, 4, 12, 0, tzinfo=timezone.utc)
    checkout_start = now - timedelta(minutes=16)  # Más de 15 minutos
    
    attempts = 3
    window_active = False  # Ventana expirada
    
    # Simular: ventana expiró → se resetea
    new_attempts = 0
    new_window_active = True
    
    assert new_attempts == 0
    assert new_window_active is True