"""
Service 服务层
负责业务逻辑处理，连接 Controller 和 Repository
"""

from fastapi import HTTPException

from ..database.database import Database
from ..database.repository import WidgetRepository
from ..dto import (
    WidgetCreateRequest,
    WidgetResponse,
)


class WidgetService:
    """Widget 服务 - 处理业务逻辑"""

    def __init__(self, db: Database):
        """
        初始化服务

        Args:
            db: 数据库实例（通过依赖注入传入）
        """
        self.db = db
        self.repository = WidgetRepository(self.db)
        # 确保表存在
        self.repository.create_table_if_not_exists()

    def create_widget(self, request: WidgetCreateRequest) -> WidgetResponse:
        """创建 Widget"""
        # 检查是否已存在相同的 label_key
        existing = self.repository.find_by_label_key(request.label_key)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Widget with label_key '{request.label_key}' already exists",
            )

        # 创建记录
        result = self.repository.create(
            label_key=request.label_key,
            type=request.type,
            options=request.options,
        )

        if not result:
            raise HTTPException(status_code=500, detail="Failed to create widget")

        return WidgetResponse(**result)
