---
skill_id: ea012590a50b
usage_count: 1
last_used: 2026-06-16
---
# tests/test_views.py
from unittest.mock import patch, Mock
import pytest

class TestPaymentView:
    """Test payment view with mocked payment gateway."""

    @patch('apps.payments.services.stripe')
    def test_successful_payment(self, mock_stripe, client, user, product):
        """Test successful payment with mocked Stripe."""