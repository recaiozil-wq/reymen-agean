---
skill_id: 2333fac6fbce
usage_count: 1
last_used: 2026-06-16
---
## Test Data Builders

```csharp
public sealed class OrderBuilder
{
    private string _customerId = "cust-default";
    private readonly List<OrderItem> _items = [new("SKU-001", 1, 10m)];

    public OrderBuilder WithCustomer(string customerId)
    {
        _customerId = customerId;
        return this;
    }

    public OrderBuilder WithItem(string sku, int quantity, decimal price)
    {
        _items.Add(new OrderItem(sku, quantity, price));
        return this;
    }

    public Order Build() => Order.Create(_customerId, _items);
}

// Usage in tests
var order = new OrderBuilder()
    .WithCustomer("cust-vip")
    .WithItem("SKU-PREMIUM", 3, 99.99m)
    .Build();
```