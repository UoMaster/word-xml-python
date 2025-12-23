from pydantic import BaseModel, Field
from datetime import datetime


# ==================== 请求 DTO ====================


class WidgetCreateRequest(BaseModel):
    """创建 Widget 的请求体"""

    label_key: str = Field(..., description="标签键", examples=["name_field"])
    type: str = Field(..., description="类型", examples=["text"])
    options: list[str] = Field(
        default=[], description="选项列表", examples=[["option1", "option2"]]
    )


class WigetListRequest(BaseModel):
    """获取 Widget 列表的请求体"""

    label_key: str = Field(..., description="标签键", examples=["name_field"])


class SetLogRequest(BaseModel):
    log_type: str = Field(
        ...,
        description="日志类型",
        examples=[
            "hit",
            "consistency",
        ],
    )
    label_key: str = Field(..., description="标签键", examples=["name_field"])
    options: list[str] = Field(
        ..., description="选项列表", examples=[["option1", "option2"]]
    )
    type: str = Field(..., description="类型", examples=["Radio", "Checkbox"])


class GetTypeRequest(BaseModel):
    left_text: str | None = Field(..., description="左文本", examples=["左文本"])
    top_text: str | None = Field(..., description="上文本", examples=["上文本"])
    text: str | None = Field(..., description="文本", examples=["文本"])


# ==================== 响应 DTO ====================


class WidgetResponse(BaseModel):
    """Widget 响应体"""

    id: int
    label_key: str
    type: str
    options: list[str]
    hit_count: int
    consistency_count: int
    un_consistency_count: int
    confidence: float
    create_time: datetime
    update_time: datetime
