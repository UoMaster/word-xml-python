"""表格信息数据模型"""

from dataclasses import dataclass


@dataclass
class TableInfo:
    """表格信息"""
    
    col: int = 0  # 列数
    row: int = 0  # 行数
    
    def __repr__(self) -> str:
        return f"TableInfo(rows={self.row}, cols={self.col})"

