from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root():
    return {
        "name": "Embodied AI Training Platform",
        "status": "ok",
        "docs": "/docs",
    }
