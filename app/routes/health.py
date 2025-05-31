from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/health")
def get_health():
    """Check the health of the Api"""

    return {
        "status": "success",
    }