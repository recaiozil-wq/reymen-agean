---
skill_id: 0b1ba4a8bd84
usage_count: 1
last_used: 2026-06-16
---
# app/schemas/user.py
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, model_validator


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    password_confirm: str

    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreate":
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    total: int
    items: list[UserResponse]
```

---