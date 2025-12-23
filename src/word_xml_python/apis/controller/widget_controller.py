from fastapi import APIRouter, Depends

from ..database.database import Database, get_database
from ..dto import (
    WidgetCreateRequest,
    WidgetResponse,
    WigetListRequest,
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


@router.post("/list", response_model=list[WidgetResponse], summary="获取 Widget 列表")
async def get_widget_list(
    request: WigetListRequest, service: WidgetService = Depends(get_widget_service)
) -> list[WidgetResponse]:
    print(request)
    return service.get_widget_list(request)
