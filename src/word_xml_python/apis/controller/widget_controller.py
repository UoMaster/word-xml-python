from fastapi import APIRouter, Depends

from ..database.database import Database, get_database
from ..dto import (
    GetTypeRequest,
    SetLogRequest,
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
    return service.get_widget_list(request)


@router.post("/set-log", response_model=bool, summary="设置")
async def set_log(
    request: SetLogRequest, service: WidgetService = Depends(get_widget_service)
) -> bool:
    return service.set_log(request)


@router.post("/get-type", response_model=str, summary="获取类型")
async def get_type(
    request: GetTypeRequest, service: WidgetService = Depends(get_widget_service)
) -> str:
    return service.get_type(request)
