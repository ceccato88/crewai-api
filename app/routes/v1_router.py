# app/routes/v1_router.py
from fastapi import APIRouter
from app.routes.health import health_router
from app.routes.agents import agents_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(health_router, tags=["Health"])
v1_router.include_router(agents_router, tags=["Crews"])
