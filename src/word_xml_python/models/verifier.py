"""验证器相关数据模型"""

from pydantic import BaseModel


class VerifierMeta(BaseModel):
    """验证器元数据"""

    name: str
    rows: list[int]
    type: str
    reason: str
    split_after_column: int | None = None


class ErrorInfo(BaseModel):
    """错误信息"""

    source_meta: str
    error_msg: str
