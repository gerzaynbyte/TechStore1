from sqlalchemy.orm import Session
from sqlalchemy import select
from src.repository import OrderRow
from datetime import datetime, timedelta, timezone



def test_pia_order_persistence():
    """Prueba de integración: guardar pedido de TechStore en DB"""
    # Importa tu repositorio (adaptado a TechStore)
    from src.repository import make_engine, SqlOrderRepository
    
    class OrderPIA:
        def __init__(self, total, status):
            self.total = total
            self.status = status
    
    engine = make_engine()
    
    with Session(engine) as session:
        # Arrange
        order = OrderPIA(total=15500.00, status="Pago confirmado")
        repo = SqlOrderRepository(session)
        
        # Act
        repo.save(1001, order)
        session.commit()
        
        # Assert
        row = session.scalar(select(OrderRow).where(OrderRow.id == 1001))
        assert row is not None
        assert row.total == 15500.00
        assert row.status == "Pago confirmado"


def test_pia_order_rollback():
    """Prueba de integración: rollback descarta el pedido"""
    from src.repository import make_engine, SqlOrderRepository
    
    class OrderPIA:
        def __init__(self, total, status):
            self.total = total
            self.status = status
    
    engine = make_engine()
    
    with Session(engine) as session:
        order = OrderPIA(total=15500.00, status="Pago confirmado")
        repo = SqlOrderRepository(session)
        
        repo.save(1002, order)
        session.rollback()
        
        # El pedido nunca se persistió
        row = session.scalar(select(OrderRow).where(OrderRow.id == 1002))
        assert row is None