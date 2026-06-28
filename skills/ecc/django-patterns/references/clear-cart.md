---
skill_id: 330262ba0dfb
usage_count: 1
last_used: 2026-06-16
---
# Clear cart
        cart.items.all().delete()

        return order

    @staticmethod
    def process_payment(order: Order, payment_data: dict) -> bool:
        """Process payment for order."""