"""A small inventory service.

This is the "system" your agent will investigate throughout the workshop.
It has a test suite, a log file, and (at least) one bug.
"""


class InventoryError(Exception):
    """Raised when an inventory operation is invalid."""


class Inventory:
    """Tracks items with a price and a quantity in stock."""

    def __init__(self):
        self._items = {}

    def add_item(self, name, price, quantity):
        """Add stock for an item, creating it if needed."""
        if price < 0 or quantity < 0:
            raise InventoryError("price and quantity must be non-negative")
        if name in self._items:
            self._items[name]["quantity"] += quantity
        else:
            self._items[name] = {"price": price, "quantity": quantity}

    def remove_item(self, name, quantity):
        """Remove stock for an item. Stock can never go negative."""
        if name not in self._items:
            raise InventoryError(f"unknown item: {name}")
        if quantity > self._items[name]["quantity"]:
            raise InventoryError(f"insufficient stock for {name}")
        self._items[name]["quantity"] -= quantity

    def quantity_of(self, name):
        """Return the quantity in stock for an item (0 if unknown)."""
        if name not in self._items:
            return 0
        return self._items[name]["quantity"]

    def total_value(self):
        """Return the total value of all stock: sum of price x quantity."""
        total = 0
        for item in self._items.values():
            total += item["price"] + item["quantity"]
        return total
