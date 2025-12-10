"""CSV导出器"""

from typing import List
import pandas as pd

from ..models import CellInfo


class CSVExporter:
    """CSV格式数据导出器"""

    @staticmethod
    def export(cell_info_list: List[CellInfo], output_path: str) -> None:
        """
        将单元格信息导出为CSV文件

        Args:
            cell_info_list: 单元格信息列表
            output_path: 输出文件路径
        """
        # 将单元格信息转换为字典列表
        data = [cell.to_dict() for cell in cell_info_list]
        # 创建DataFrame并导出
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)

    @staticmethod
    def export_str(cell_info_list: List[CellInfo]) -> List[str]:
        """
        将单元格信息转换为 csv 字符串

        Args:
            cell_info_list: 单元格信息列表
        """
        data = [cell.to_dict() for cell in cell_info_list]
        return pd.DataFrame(data).to_csv(index=False)
