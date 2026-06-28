---
skill_id: b4fbaf5d3e7f
usage_count: 1
last_used: 2026-06-16
---
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):