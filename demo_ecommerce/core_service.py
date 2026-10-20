"""E-Commerce Cart, Inventory, and Order Processing Service.
Generated for task: Zamonaviy Online Do'kon va Savat Tizimi
Handles product catalog, cart mutations, discount coupons, currency formatting, and checkout orders.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time
import uuid


@dataclass
class Product:
    id: str
    name: str
    price: float
    inventory: int
    category: str = "general"

    def is_available(self, quantity: int = 1) -> bool:
        return self.inventory >= quantity


class ECommerceService:
    def __init__(self, currency_symbol: str = "UZS"):
        self.currency_symbol = currency_symbol
        self.catalog: Dict[str, Product] = {}
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.coupons: Dict[str, float] = {"CHEMPION10": 10.0, "SUPER20": 20.0}

    def add_product(self, product_id: str, name: str, price: float, inventory: int, category: str = "general") -> Product:
        if price < 0 or inventory < 0:
            raise ValueError("Price and inventory must be non-negative")
        prod = Product(id=product_id, name=name, price=float(price), inventory=int(inventory), category=category)
        self.catalog[product_id] = prod
        return prod

    def calculate_cart_totals(self, items: List[Dict[str, Any]], coupon_code: Optional[str] = None) -> Dict[str, Any]:
        discount_pct = 0.0
        if coupon_code:
            clean_code = coupon_code.strip().upper()
            if clean_code in self.coupons:
                discount_pct = self.coupons[clean_code]
            else:
                raise ValueError(f"Invalid coupon code: {coupon_code}")

        subtotal = 0.0
        verified_items = []
        for item in items:
            pid = item.get("product_id")
            qty = int(item.get("quantity", 1))
            prod = self.catalog.get(pid)
            if not prod:
                raise KeyError(f"Product '{pid}' not found in catalog")
            if not prod.is_available(qty):
                raise ValueError(f"Insufficient stock for product '{pid}' (available: {prod.inventory})")
            line_total = prod.price * qty
            subtotal += line_total
            verified_items.append({
                "product_id": pid,
                "name": prod.name,
                "unit_price": prod.price,
                "quantity": qty,
                "line_total": round(line_total, 2)
            })

        discount_amount = round(subtotal * (discount_pct / 100.0), 2)
        tax = round((subtotal - discount_amount) * 0.12, 2)
        total = round(subtotal - discount_amount + tax, 2)

        return {
            "items": verified_items,
            "subtotal": round(subtotal, 2),
            "discount_amount": discount_amount,
            "tax": tax,
            "total": total,
            "currency": self.currency_symbol
        }

    def checkout(self, customer_id: str, items: List[Dict[str, Any]], coupon_code: Optional[str] = None) -> Dict[str, Any]:
        if not items:
            raise ValueError("Cannot checkout with an empty cart")
        totals = self.calculate_cart_totals(items, coupon_code)

        for item in items:
            prod = self.catalog[item["product_id"]]
            prod.inventory -= int(item.get("quantity", 1))

        order_id = f"ord_{uuid.uuid4().hex[:12]}"
        order = {
            "order_id": order_id,
            "customer_id": customer_id,
            "items": totals["items"],
            "totals": totals,
            "status": "CONFIRMED",
            "created_at": time.time()
        }
        self.orders[order_id] = order
        return order
