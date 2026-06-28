---
skill_id: d038b629570f
usage_count: 1
last_used: 2026-06-16
---
# Enforce explicit deterministic ordering to ensure reliable pagination
        result = await self.db.execute(
            select(User).order_by(User.id).offset(skip).limit(limit)
        )
        return list(result.scalars()), total

    async def update(self, user_id: int, payload: UserUpdate) -> User | None:
        user = await self.db.get(User, user_id)
        if user is None:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise DuplicateUserError from exc
        await self.db.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> str | None:
        user = await self.get_by_email(email)
        if user is None or not pwd_context.verify(password, user.hashed_password):
            return None
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        return jwt.encode(
            {"sub": str(user.id), "exp": expire},
            settings.secret_key,
            algorithm=settings.algorithm,
        )
```

> **Note on Database Design:** Application-level unique handling requires an underlying unique database index (e.g., `unique=True` on your SQLAlchemy mapping attributes). Without underlying constraints, application layer error-catching cannot safely prevent concurrent race conditions.

---