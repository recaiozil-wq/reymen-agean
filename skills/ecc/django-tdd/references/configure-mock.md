---
skill_id: 714488088aab
usage_count: 1
last_used: 2026-06-16
---
# Configure mock
        mock_stripe.Charge.create.return_value = {
            'id': 'ch_123',
            'status': 'succeeded',
            'amount': 9999,
        }

        client.force_login(user)
        response = client.post(reverse('payments:process'), {
            'product_id': product.id,
            'token': 'tok_visa',
        })

        assert response.status_code == 302
        mock_stripe.Charge.create.assert_called_once()

    @patch('apps.payments.services.stripe')
    def test_failed_payment(self, mock_stripe, client, user, product):
        """Test failed payment."""
        mock_stripe.Charge.create.side_effect = Exception('Card declined')

        client.force_login(user)
        response = client.post(reverse('payments:process'), {
            'product_id': product.id,
            'token': 'tok_visa',
        })

        assert response.status_code == 302
        assert 'error' in response.url
```

### Mocking Email Sending

```python