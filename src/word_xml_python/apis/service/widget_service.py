"""
Service 服务层
负责业务逻辑处理，连接 Controller 和 Repository
"""

from datetime import datetime

from fastapi import HTTPException

from ..database.database import Database
from ..database.repository import WidgetRepository
from ..dto import (
    GetTypeRequest,
    SetLogRequest,
    WidgetCreateRequest,
    WidgetResponse,
    WigetListRequest,
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

    def get_widget_list(self, request: WigetListRequest) -> list[WidgetResponse]:
        print("get_widget_list", request.label_key)
        return [
            WidgetResponse(**row) for row in self.repository.find_all(request.label_key)
        ]

    def set_log(self, request: SetLogRequest) -> bool:
        label_key = request.label_key
        log_type = request.log_type
        options = request.options
        type = request.type

        if log_type == "hit_count":
            record = self.repository.find_by_label_key_and_type(label_key, type)
            if record:
                self.repository.update_hit_count_by_label_key_and_type(
                    label_key, type, record["hit_count"] + 1
                )
            else:
                self.create_widget_record(label_key, type, options, log_type)
        elif log_type == "consistency_count":
            records = self.repository.find_by_label_key(label_key)
            if len(records) == 0:
                self.create_widget_record(label_key, type, options, log_type)
            else:
                for record in records:
                    if record["type"] == type:
                        self.repository.update_consistency_count_by_label_key_and_type(
                            label_key, type, record["consistency_count"] + 1
                        )
                    else:
                        self.repository.update_un_consistency_count_by_label_key_and_type(
                            label_key, type, record["un_consistency_count"] + 1
                        )

    def create_widget_record(
        self, label_key: str, type: str, options: list[str], log_type: str
    ) -> bool:
        self.repository.create(label_key, type, options, log_type)

    def get_type(self, request: GetTypeRequest) -> str:
        def clean_keyword(text: str | None) -> str:
            if text is None:
                return ""
            return (
                text.replace(" ", "")
                .replace("\n", "")
                .replace("\r", "")
                .replace("\t", "")
            )

        def get_frequency_confidence(hit_count: int) -> float:
            if hit_count >= 50:
                return 1.0
            elif hit_count >= 10:
                return 0.9
            elif hit_count >= 3:
                return 0.6
            elif hit_count >= 1:
                return 0.2
            return 0.0

        def get_consistency_confidence(
            consistency_count: int, un_consistency_count: int
        ) -> float:
            total = consistency_count + un_consistency_count
            if total == 0:
                return 0.0
            return consistency_count / total

        def get_time_decay(update_time: datetime) -> float:
            now = datetime.now(update_time.tzinfo)
            days_diff = (now - update_time).days
            if days_diff > 20:
                return 0.7
            return 1.0

        keywords = [
            clean_keyword(request.left_text),
            clean_keyword(request.top_text),
            clean_keyword(request.text),
        ]
        keywords = [k for k in keywords if k]

        if not keywords:
            return ""

        records_map: dict[int, dict] = {}
        for keyword in keywords:
            records = self.repository.find_by_label_key(keyword)
            for record in records:
                records_map[record["id"]] = record

        if not records_map:
            return ""

        best_type = ""
        best_confidence = -1.0

        for record in records_map.values():
            freq_conf = get_frequency_confidence(record["hit_count"])
            cons_conf = get_consistency_confidence(
                record["consistency_count"], record["un_consistency_count"]
            )
            time_decay = get_time_decay(record["update_time"])

            confidence = freq_conf * cons_conf * time_decay

            if confidence > best_confidence:
                best_confidence = confidence
                best_type = record["type"]

        if best_confidence <= 0.5:
            return ""

        return best_type
