---
skill_id: 0af5ea0a2b4d
usage_count: 1
last_used: 2026-06-16
---
# E-Ticaret Mikroservis - Tüm Dosyalar

## service-registry/

- `pom.xml` — spring-cloud-starter-netflix-eureka-server
- `ServiceRegistryApplication.java` — @EnableEurekaServer
- `application.yml` — port 8761, register-with-eureka: false

## api-gateway/

- `pom.xml` — gateway, eureka-client, jjwt
- `ApiGatewayApplication.java` — @EnableDiscoveryClient
- `JwtAuthGatewayFilter.java` — GlobalFilter, JWT doğrulama, /api/auth/** bypass
- `application.yml` — port 8080, 3 route (user/product/order), globalcors

## product-service/

### entity/
- `Product.java` — @Getter @Setter, @ManyToOne(fetch=LAZY) Category
- `Category.java` — @Getter @Setter, @OneToMany(mappedBy="category") Set<Product>

### dto/
- `ProductRequest.java` — @NotBlank name, @Positive price, @PositiveOrZero stockQuantity
- `ProductResponse.java` — id, name, price, stockQuantity, categoryName, createdAt
- `CategoryRequest.java` — @NotBlank name, description
- `CategoryResponse.java` — id, name, description, productCount, createdAt

### repository/
- `ProductRepository.java` — findByCategoryId
- `CategoryRepository.java` — findBy

### service/
- `ProductService.java` — 155 satır: createCategory, getAllCategories, getCategory, createProduct, getAllProducts, getProduct, updateProduct, deleteProduct

### controller/
- `ProductController.java` — 75 satır: CRUD endpoints, /api/products, /api/categories

### exception/
- `ResourceNotFoundException.java` — RuntimeException subclass
- `GlobalExceptionHandler.java` — @RestControllerAdvice, 404/400/500 handlers

### resources/
- `application.yml` — port 0, eureka-client, H2 mem productdb

## order-service/

### entity/
- `Order.java` — @Getter @Setter, @OneToMany(mappedBy="order") Set<OrderItem>, orderNumber generator
- `OrderItem.java` — @Getter @Setter, @ManyToOne(fetch=LAZY) Order, @JsonIgnore

### dto/
- `OrderRequest.java` — @NotEmpty List<OrderItemRequest> items
- `OrderResponse.java` — id, orderNumber, items, totalAmount, status, createdAt
- `ProductDto.java` — id, name, price, stockQuantity (Feign tarafından doldurulur)

### client/
- `ProductServiceClient.java` — @FeignClient(name="product-service"), GET /api/products/{id}

### repository/
- `OrderRepository.java` — findByUserEmailOrderByCreatedAtDesc

### service/
- `OrderService.java` — 104 satır: createOrder (Feign ile ürün doğrulama + fiyat hesaplama), getUserOrders, getOrderById

### controller/
- `OrderController.java` — 40 satır: POST create, GET all (X-User-Email header'dan), GET /{id}

### resources/
- `application.yml` — port 0, eureka-client, Feign, H2 mem orderdb

## user-service/

### entity/
- `User.java` — @Getter @Setter, email/password/fullName/role/createdAt, Role enum

### dto/
- `AuthRequest.java` — @NotBlank @Email email, @NotBlank @Size(min=6) password, fullName
- `AuthResponse.java` — token, email, fullName, role
- `UserResponse.java` — id, email, fullName, role, createdAt

### repository/
- `UserRepository.java` — findByEmail, existsByEmail

### service/
- `AuthService.java` — 90 satır: register (exists check), login (password match), getUserByEmail

### controller/
- `AuthController.java` — 40 satır: POST /api/auth/register, POST /api/auth/login, GET /api/auth/me (X-User-Email)

### util/
- `JwtTokenUtil.java` — hmacShaKeyFor, generateToken (app.jwt.secret), validateToken

### resources/
- `application.yml` — port 0, eureka-client, app.jwt.secret + app.jwt.expiration-ms
