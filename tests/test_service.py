from unittest.mock import Mock, call

import pytest

from src.application import OrderService
from src.domain import Order


def test_gateway_approved():
    gateway = Mock()
    gateway.charge.return_value = True
    assert OrderService(gateway).checkout(Order(100)) == 100
    gateway.charge.assert_called_once_with(100)

def test_gateway_rejected():
    gateway = Mock()
    gateway.charge.return_value = False
    with pytest.raises(RuntimeError):
        OrderService(gateway).checkout(Order(100))

def test_vip_rejected_charges_discounted_amount():
    gateway = Mock()
    gateway.charge.return_value = False
    order = Order(200, vip=True)

    with pytest.raises(RuntimeError, match="payment rejected"):
        OrderService(gateway).checkout(order)

    gateway.charge.assert_called_once_with(170)
    # Riesgo documentado: el pedido quedó CONFIRMED aunque el pago fue rechazado
    assert order.status == "CONFIRMED"

def test_mock_registra_la_llamada():
    gateway = Mock()
    gateway.charge.return_value = True
    OrderService(gateway).checkout(Order(200, vip=True))

    print("\n--- REGISTRO DEL MOCK ---")
    print("call_args_list :", gateway.charge.call_args_list)
    print("call_count     :", gateway.charge.call_count)
    print("mock_calls     :", gateway.mock_calls)

    assert gateway.charge.call_args_list == [call(170)]