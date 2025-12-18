from pydantic import BaseModel, Field


class TableInfo(BaseModel):
    """表格信息"""

    col: int = 0  # 列数
    row: int = 0  # 行数

    def __repr__(self) -> str:
        return f"TableInfo(rows={self.row}, cols={self.col})"


class CellRBody(BaseModel):
    """单元格run内容（文本片段）"""

    rStyle: str = ""
    body: str = ""


class CellPBody(BaseModel):
    """单元格段落内容"""

    pStyle: dict[str, str] = Field(default_factory=dict)
    rList: list[CellRBody] = Field(default_factory=list)


class CellInfo(BaseModel):
    """单元格信息"""

    key: str  # 单元格位置标识，格式: "行索引-列索引"
    col_span: int = 1  # 列合并数
    row_span: int = 1  # 行合并数
    body: list[CellPBody] = Field(default_factory=list)
    is_empty_cell: bool = False
    left_cell_key: str | None = None
    top_cell_key: str | None = None
    left_text_body: str | None = None  # 左边单元格的文本内容
    top_text_body: str | None = None  # 上边单元格的文本内容
    is_merge_continue_cell: bool = False  # 是否是行合并的单元格

    def __repr__(self) -> str:
        return (
            f"CellInfo(key={self.key}, "
            f"col_span={self.col_span}, "
            f"row_span={self.row_span}, "
            f"body={self.body}"
            f"is_empty_cell={self.is_empty_cell}"
            f"left_cell_key={self.left_cell_key}"
            f"top_cell_key={self.top_cell_key}"
            f"left_text_body={self.left_text_body}"
            f"top_text_body={self.top_text_body}"
            f"is_merge_continue_cell={self.is_merge_continue_cell}"
        )


class ExtractorResult(BaseModel):
    """提取结果"""

    table_type: str
    table_info: TableInfo = Field(default_factory=TableInfo)
    cell_info_list: list[CellInfo] = Field(default_factory=list)

    def __repr__(self) -> str:
        return f"ExtractorResult(table_info={self.table_info}, cell_info_list={self.cell_info_list})"
