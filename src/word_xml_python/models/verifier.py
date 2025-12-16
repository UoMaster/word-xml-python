"""验证器相关数据模型"""

from dataclasses import dataclass
from typing import List


@dataclass
class VerifierMeta:
    """验证器元数据"""

    name: str
    rows: List[int]
    type: str
    reason: str
    split_after_column: int | None = None


@dataclass
class ErrorInfo:
    """错误信息"""

    source_meta: str
    error_msg: str
