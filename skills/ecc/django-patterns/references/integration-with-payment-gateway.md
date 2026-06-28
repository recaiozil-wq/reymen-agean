---
skill_id: 781bb678acdd
usage_count: 1
last_used: 2026-06-16
---
# Integration with payment gateway
        payment = PaymentGateway.charge(
            amount=order.total_price,
            token=payment_data['token']
        )

        if payment.success:
            order.status = Order.Status.PAID
            order.save()