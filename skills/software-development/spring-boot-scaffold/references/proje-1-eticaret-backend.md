---
skill_id: a860968a5aa6
usage_count: 1
last_used: 2026-06-16
---
# Proje #1: E-Ticaret Backend (Spring Boot + JPA + JWT)

## Temel Bilgiler

- **Yol:** `C:\Users\marko\Desktop\e-ticaret-backend\`
- **Port:** 8080
- **Java:** JDK 17 (Eclipse Adoptium)
- **Maven:** 3.9.9 portable
- **DB:** H2 in-memory (`jdbc:h2:mem:eticaret`)
- **Test script:** `test_api.py`

## Entity'ler (5)

| Entity | Tablo | Iliskiler |
|--------|-------|-----------|
| Product | products | ManyToOne -> Category |
| Category | categories | OneToMany -> Product |
| User | users | OneToMany -> Order |
| Order | orders | ManyToOne -> User, OneToMany -> OrderItem |
| OrderItem | order_items | ManyToOne -> Order, ManyToOne -> Product |

## DTO'lar (8)

AuthRequest (RegisterRequest inner), AuthResponse, CategoryRequest, CategoryResponse,
ProductRequest, ProductResponse, OrderRequest (OrderItemRequest inner), OrderResponse (OrderItemResponse inner)

## API Endpoints

| Method | Path | Auth | Aciklama |
|--------|------|------|----------|
| POST | /api/auth/register | Public | Kayit |
| POST | /api/auth/login | Public | Giris |
| GET | /api/products | Public | Urun listele |
| GET | /api/products/{id} | Public | Urun detay |
| POST | /api/products | Token | Urun ekle |
| PUT | /api/products/{id} | Token | Urun guncelle |
| DELETE | /api/products/{id} | Token | Urun sil |
| GET | /api/categories | Public | Kategori listele |
| POST | /api/categories | Token | Kategori ekle |
| POST | /api/orders | Token | Siparis olustur |
| GET | /api/orders | Token | Kullanici siparisleri |

## Oturumda Cozulen Hatalar

1. **Login 403:** SecurityConfig'de UserDetailsService bean'i yoktu — eklendi
2. **StackOverflowError (Order):** `@Data` + JSON dongusu — `@Data` -> `@Getter @Setter`, `@JsonIgnore` eklendi
3. **Lombok compile hatasi:** pom.xml'de annotationProcessorPaths eksikti — eklendi
4. **Public endpoint 403:** GET/products/categories permitAll eklenmemisti
5. **Genel 403 hata maskesi:** GlobalExceptionHandler yoktu — eklendi
