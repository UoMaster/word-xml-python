from fastapi import APIRouter, Depends

from ..database.database import Database, get_database
from ..dto import (
    WidgetCreateRequest,
    WidgetResponse,
)
from ..service import WidgetService

router = APIRouter(
    prefix="/widgets",
    tags=["Widgets"],
    responses={404: {"description": "Not found"}},
)


def get_widget_service(db: Database = Depends(get_database)) -> WidgetService:
    return WidgetService(db)


@router.post("/", response_model=WidgetResponse, summary="创建 Widget")
async def create_widget(
    request: WidgetCreateRequest,
    service: WidgetService = Depends(get_widget_service),
):
    return service.create_widget(request)
