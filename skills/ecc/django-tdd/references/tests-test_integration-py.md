---
skill_id: c954f2bbdf90
usage_count: 1
last_used: 2026-06-16
---
# tests/test_integration.py
import pytest
from django.urls import reverse
from tests.factories import UserFactory, ProductFactory

class TestCheckoutFlow:
    """Test complete checkout flow."""

    def test_guest_to_purchase_flow(self, client, db):
        """Test complete flow from guest to purchase."""