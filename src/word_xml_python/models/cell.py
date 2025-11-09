"""单元格信息数据模型"""

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List


@dataclass
class CellRBody:
    """单元格run内容（文本片段）"""
    rStyle: str = ""
    body: str = ""


@dataclass
class CellPBody:
    """单元格段落内容"""
    pStyle: Dict[str, str] = field(default_factory=dict)
    rList: List[CellRBody] = field(default_factory=list)


@dataclass
class CellInfo:
    """单元格信息"""

    key: str  # 单元格位置标识，格式: "行索引-列索引"
    col_span: int = 1  # 列合并数
    row_span: int = 1  # 行合并数
    body: List[CellPBody] = field(default_factory=list)
    is_empty_cell: bool = False
    left_cell_key: str | None = None
    top_cell_key: str | None = None

    def __repr__(self) -> str:
        return (
            f"CellInfo(key={self.key}, "
            f"col_span={self.col_span}, "
            f"row_span={self.row_span}, "
            f"body={self.body}"
            f"is_empty_cell={self.is_empty_cell}"
            f"left_cell_key={self.left_cell_key}"
            f"top_cell_key={self.top_cell_key}"
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)
