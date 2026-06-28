---
name: ecc_quarkus-security_references_password-hashing
description: Password Hashing
title: "Ecc Quarkus Security References Password Hashing"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Password Hashing |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Password Hashing

```java
@ApplicationScoped
public class PasswordService {

  public String hash(String plainPassword) {
    return BcryptUtil.bcryptHash(plainPassword);
  }

  public boolean verify(String plainPassword, String hashedPassword) {
    return BcryptUtil.matches(plainPassword, hashedPassword);
  }
}

// In service
@ApplicationScoped
public class UserService {
  @Inject
  PasswordService passwordService;

  @Transactional
  public User register(CreateUserDto dto) {
    String hashedPassword = passwordService.hash(dto.password());
    User user = new User();
    user.email = dto.email();
    user.password = hashedPassword;
    user.persist();
    return user;
  }

  public boolean authenticate(String email, String password) {
    return User.find("email", email)
        .firstResultOptional()
        .map(u -> passwordService.verify(password, u.password))
        .orElse(false);
  }
}
```
