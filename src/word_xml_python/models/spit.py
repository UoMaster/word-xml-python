from pydantic import BaseModel


class TableSplitResult(BaseModel):
    """表格分割结果"""

    table_xml: str
    table_type: str
