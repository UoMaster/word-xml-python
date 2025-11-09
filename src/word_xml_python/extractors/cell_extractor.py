"""单元格信息提取器"""

from typing import Dict, List
from lxml.etree import _Element

from ..models import CellInfo, CellPBody, CellRBody
from ..core import TCPR_DELETE_TAGS


class CellExtractor:
    """单元格信息提取器"""
    
    def __init__(self, namespaces: Dict[str, str]):
        """
        初始化提取器
        
        Args:
            namespaces: XML命名空间映射
        """
        self.namespaces = namespaces
        self.row_span_map: Dict[int, CellInfo] = {}
    
    def extract_all(self, table_element: _Element) -> List[CellInfo]:
        """
        从表格元素中提取所有单元格信息
        
        Args:
            table_element: 表格XML元素
            
        Returns:
            单元格信息列表
        """
        cell_info_list: List[CellInfo] = []
        self.row_span_map = {}
        
        # 获取所有行
        rows = table_element.findall(".//w:tr", self.namespaces)
        
        for row_index, row in enumerate(rows):
            cells = row.findall(".//w:tc", self.namespaces)
            
            for cell_index, cell in enumerate(cells):
                cell_info = self._extract_cell(cell, row_index, cell_index)
                cell_info_list.append(cell_info)
        
        return cell_info_list
    
    def _extract_cell(
        self, 
        cell_element: _Element, 
        row_index: int, 
        cell_index: int
    ) -> CellInfo:
        """
        提取单个单元格信息
        
        Args:
            cell_element: 单元格XML元素
            row_index: 行索引
            cell_index: 列索引
            
        Returns:
            单元格信息对象
        """
        key = f"{row_index}-{cell_index}"
        
        # 获取单元格属性
        tc_pr = cell_element.find("./w:tcPr", self.namespaces)
        
        # 清理不需要的标签
        if tc_pr is not None:
            self._clean_tc_pr(tc_pr)
        
        # 获取列合并信息
        col_span = self._get_col_span(tc_pr)
        
        # 提取单元格内容
        cell_body = self._extract_p_body(cell_element)
        
        # 创建单元格信息对象
        cell_info = CellInfo(
            key=key,
            col_span=col_span,
            row_span=1,
            body=cell_body,
            is_empty_cell=False
        )
        
        if len(cell_body) ==1 or len(cell_body[0].rList) == 0:
            cell_info.is_empty_cell = True


        left_cell_key, top_cell_key = self._get_adjoining_cell_key(row_index, cell_index)
        cell_info.left_cell_key = left_cell_key
        cell_info.top_cell_key = top_cell_key
        
        # 处理行合并
        self._process_row_merge(tc_pr, cell_index, cell_info)
        
        return cell_info

    def _get_adjoining_cell_key(self, row_index: int, cell_index: int) -> (str | None, str | None):
        """
        获取相邻的单元格的key

        Returns:
            (左边相邻的单元格的key, 上边相邻的单元格的key)
        """

        left_cell_key = None if cell_index == 0 else f"{row_index}-{cell_index - 1}"
        top_cell_key = None if row_index == 0 else f"{row_index - 1}-{cell_index}"
        return (left_cell_key, top_cell_key)
    
    def _clean_tc_pr(self, tc_pr: _Element) -> None:
        """
        清理tcPr元素中不需要的标签
        
        Args:
            tc_pr: tcPr元素
        """
        for tag in TCPR_DELETE_TAGS:
            tag_element = tc_pr.find(tag, self.namespaces)
            if tag_element is not None:
                tc_pr.remove(tag_element)
    
    def _get_col_span(self, tc_pr: _Element | None) -> int:
        """
        获取列合并数
        
        Args:
            tc_pr: tcPr元素
            
        Returns:
            列合并数
        """
        if tc_pr is None:
            return 1
        
        grid_span = tc_pr.find("./w:gridSpan", self.namespaces)
        if grid_span is not None:
            val = grid_span.get(f"{{{self.namespaces['w']}}}val", "1")
            return int(val)
        
        return 1
    
    def _process_row_merge(
        self, 
        tc_pr: _Element | None, 
        cell_index: int,
        cell_info: CellInfo
    ) -> None:
        """
        处理行合并逻辑
        
        Args:
            tc_pr: tcPr元素
            cell_index: 列索引
            cell_info: 单元格信息对象
        """
        if tc_pr is None:
            # 没有tcPr，清除该列的行合并记录
            self.row_span_map.pop(cell_index, None)
            return
        
        v_merge = tc_pr.find("./w:vMerge", self.namespaces)
        
        if v_merge is not None:
            val = v_merge.get(f"{{{self.namespaces['w']}}}val", "continue")
            
            if val == "restart":
                # 开始新的行合并
                self.row_span_map[cell_index] = cell_info
            elif val == "continue":
                # 继续行合并
                if cell_index in self.row_span_map:
                    self.row_span_map[cell_index].row_span += 1
        else:
            # 没有vMerge标签，清除该列的行合并记录
            self.row_span_map.pop(cell_index, None)

    def _extract_p_body(self, cell_element: _Element) -> List[CellPBody]:
        """
        提取单元格内容
        
        Args:
            cell_element: 单元格XML元素
            
        Returns:
            单元格内容列表
        """
        body: List[CellPBody] = []
        p_elements = cell_element.findall("./w:p", self.namespaces)
        for p_element in p_elements:
            pStyle: Dict[str, str] = {}
            pPrElement = p_element.find("./w:pPr", self.namespaces)
            # 提取 p 中的段落样式
            if pPrElement is not None:
                jcElement = pPrElement.find("./w:jc", self.namespaces)
                if jcElement is not None:
                    pStyle["algin"] = jcElement.get(f"{{{self.namespaces['w']}}}val", "left")
            # 提取 p 中的文本样式
            rprElement = p_element.find("./w:rPr", self.namespaces)
            if rprElement is not None:
                style_tags = [
                    ("color", "black"),
                    ("b", "false"),
                    ("i", "false"),
                ]
                for tag, default in style_tags:
                    element = rprElement.find(f"./w:{tag}", self.namespaces)
                    if element is not None:
                        # 映射标签名称
                        style_key = tag
                        if tag == "b":
                            style_key = "bold"
                        elif tag == "i":
                            style_key = "italic"
                        pStyle[style_key] = element.get(f"{{{self.namespaces['w']}}}val", default)
            
            # 创建段落内容
            pBody = CellPBody(
                pStyle=pStyle,
                rList=self._extract_r_body(p_element)
            )
            body.append(pBody)
        return body

    def _extract_r_body(self, p_element: _Element) -> List[CellRBody]:
        """
        提取 w:r元素

        Args:
            p_element: w:p元素
            
        Returns:
            run内容列表
        """
        body: List[CellRBody] = []
        r_elements = p_element.findall("./w:r", self.namespaces)
        for r_element in r_elements:
            rStyle: str = ""
            # 提取 r 中的文本样式
            rPrElement = r_element.find("./w:rPr", self.namespaces)
            if rPrElement is not None:
                colorElement = rPrElement.find("./w:color", self.namespaces)
                if colorElement is not None:
                    rStyle = colorElement.get(f"{{{self.namespaces['w']}}}val", "")

            # 提取 r 中的文本
            textElement = r_element.find("./w:t", self.namespaces)
            rBody = CellRBody(
                rStyle=rStyle,
                body=textElement.text if textElement is not None else ""
            )
            body.append(rBody)
        return body