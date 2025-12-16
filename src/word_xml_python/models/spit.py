from dataclasses import dataclass


@dataclass
class TableSplitResult:
    """表格分割结果"""

    table_xml: str
    table_type: str
