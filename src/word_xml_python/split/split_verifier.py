from ..models import TableSplitResult


class SplitVerifier:
    """表格分割验证器"""

    table_split_result: TableSplitResult

    def __init__(self, table_split_result: TableSplitResult):
        self.table_split_result = table_split_result
