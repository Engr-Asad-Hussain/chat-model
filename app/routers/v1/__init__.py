from fastapi import APIRouter

from app.routers.v1.task import route_question, route_upload

router = APIRouter(prefix="/v1")

router.include_router(route_upload.router)
router.include_router(route_question.router)
