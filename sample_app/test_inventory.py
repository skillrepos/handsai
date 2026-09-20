"""Tests for the inventory service. One of these currently fails."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from inventory import Inventory, InventoryError


def test_add_and_quantity():
    inv = Inventory()
    inv.add_item("widget", 19.99, 5)
    inv.add_item("widget", 19.99, 2)
    assert inv.quantity_of("widget") == 7


def test_remove_item():
    inv = Inventory()
    inv.add_item("gadget", 5.00, 10)
    inv.remove_item("gadget", 4)
    assert inv.quantity_of("gadget") == 6


def test_remove_too_many_raises():
    inv = Inventory()
    inv.add_item("gizmo", 2.50, 1)
    with pytest.raises(InventoryError):
        inv.remove_item("gizmo", 5)


def test_unknown_item_raises():
    inv = Inventory()
    with pytest.raises(InventoryError):
        inv.remove_item("nothere", 1)


def test_total_value():
    inv = Inventory()
    inv.add_item("widget", 19.99, 5)   # 99.95
    inv.add_item("gadget", 5.00, 10)   # 50.00
    assert inv.total_value() == pytest.approx(149.95)
