---
skill_id: d9e88030a48f
usage_count: 1
last_used: 2026-06-16
---
## Server / Client Components (RSC)

```tsx
// Server Component - default, async, never ships JS for itself
export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await db.product.findUnique({ where: { id: params.id } });
  if (!product) notFound();
  return <ProductView product={product} />;
}

// Client Component - opt in with "use client"
"use client";
export function AddToCartButton({ productId }: { productId: string }) {
  const [pending, startTransition] = useTransition();
  return (
    <button
      disabled={pending}
      onClick={() => startTransition(() => addToCart(productId))}
    >
      {pending ? "Adding..." : "Add to cart"}
    </button>
  );
}
```

Boundaries:

- Server -> Client: pass serializable props or `children`
- Client -> Server: invoke Server Actions via `<form action={...}>` or imperatively from event handlers
- Never `import` a Server Component from a Client Component file — compose them via `children` instead