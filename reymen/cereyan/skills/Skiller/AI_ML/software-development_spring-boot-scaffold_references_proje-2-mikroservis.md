---
name: software-development_spring-boot-scaffold_references_proje-2-mikroservis
description: E-Ticaret Mikroservis (Proje #2)
title: "Software Development Spring Boot Scaffold References Proje 2 Mikroservis"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | E-Ticaret Mikroservis (Proje |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# E-Ticaret Mikroservis (Proje #2)

**Yol:** `C:\Users\marko\Desktop\e-ticaret-mikroservis\`
**Durum:** Derlendi (mvn compile -q exit 0).
**Teknoloji:** Spring Boot 3.4.4 + Spring Cloud 2024.0.1

## Servisler

| Servis | Port | Açıklama |
|--------|------|----------|
| Service Registry (Eureka) | 8761 | Register-with-eureka: false |
| API Gateway | 8080 | Spring Cloud Gateway + JWT Filter |
| Product Service | random | JPA + H2 + REST |
| Order Service | random | JPA + H2 + Feign -> Product |
| User Service | random | JPA + H2 + JWT Auth |

## Başlatma Sırası

1. service-registry -> mvn spring-boot:run -q (port 8761, ~8sn)
2. user-service, product-service, order-service (paralel, random port, ~6sn her biri)
3. api-gateway -> port 8080 (~10sn)

## Gateway Route'ları

- `/api/auth/**` -> user-service (JWT bypass)
- `/api/products/**, /api/categories/**` -> product-service
- `/api/orders/**` -> order-service

## Gateway JWT Filter

- `/api/auth/**` dışındaki tüm isteklerde Authorization header'dan JWT okur
- Token doğrulaması gateway'de yapılır, geçerliyse X-User-Email header'ı eklenir
- Geçersiz/seb 401 Unauthorized

## Feign İletişimi

- Order Service -> Product Service: @FeignClient(name = "product-service")
- Sipariş oluştururken ürün bilgisi Feign ile çekilir ve doğrulanır

## Dosya Dağılımı

Toplam 35+ Java dosyasi:
- service-registry: 2 Java
- api-gateway: 2 Java (application + JwtAuthGatewayFilter)
- product-service: 8 Java (entity 2, dto 4, repository 2, service 1, controller 1, exception 2)
- order-service: 7 Java (entity 2, dto 3, feign client 1, repository 1, service 1, controller 1)
- user-service: 7 Java (entity 1, dto 3, repository 1, service 1, controller 1, util 1)

## Derleme

```bash
export JAVA_HOME="/c/Program Files/Eclipse Adoptium/jdk-17.0.19.10-hotspot"
export PATH="$JAVA_HOME/bin:/c/Users/marko/Desktop/e-ticaret-backend/apache-maven-3.9.9/bin:$PATH"
cd /c/Users/marko/Desktop/e-ticaret-mikroservis
mvn compile -q
```

## Önemli Dersler

- Gateway JWT filter'da `@Order(-1)` + `GlobalFilter` kullanılır
- Feign client'lar `@EnableFeignClients` ile aktifleştirilir
- Product-Order servis iletişiminde API uyumu kritik — ProductDto alanları ProductService.Response ile eşleşmeli
- Random port kullanımı: `server.port: 0` — Eureka port'u otomatik keşfeder
- Gateway route'larında `lb://servis-adi` Eureka üzerinden load balancing yapar
