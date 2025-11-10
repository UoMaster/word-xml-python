from copy import deepcopy
from dataclasses import dataclass
from tkinter import W
from lxml.etree import _Element
from typing import Dict, List
from ..models import CellInfo, TableInfo, XmlMeta
from lxml import etree


@dataclass
class TableSplitResult:
    table: _Element
    table_type: str
    table_cell_csv_str: str = ""
    table_info: TableInfo | None = None
    table_cell_list: List[CellInfo] | None = None


class TableSplitter:
    """表格分割器"""

    tblElement: _Element
    namespaces: Dict[str, str]
    xmlMetaList: List[XmlMeta]
    ns: Dict[str, str]
    currentTblElement: _Element
    tables: List[TableSplitResult]

    def __init__(self, tblElement: _Element, namespaces: Dict[str, str]):
        self.tblElement = tblElement
        self.namespaces = namespaces
        self.xmlMetaList: List[XmlMeta] = []
        self.ns = namespaces
        self.tables = []

    def split(self):
        """分割表格"""
        self.currentTblElement = self.copyTemplateTbl()
        tr_elements = self.tblElement.findall(".//w:tr", self.namespaces)
        all_tr_len = len(tr_elements)
        # 上指针
        top_point = 0
        # 下指针
        bottom_point = top_point + 1

        # 1. 如果 t 指针和 b 指针 的列数相同则 添加 t 指针的行到当前表，并移动 t + 1 指针和 b + 1 指针
        while top_point < all_tr_len:
            # 边界检查：确保 bottom_point 不越界
            if bottom_point >= all_tr_len:
                # 如果 bottom_point 超出范围，将剩余的行添加到当前表
                self.currentTblElement.append(deepcopy(tr_elements[top_point]))
                self.load_new_template_tbl()
                break

            # 元素
            t_el = tr_elements[top_point]
            b_el = tr_elements[bottom_point]

            # 列数
            t_len = len(t_el.findall(".//w:tc", self.namespaces))
            b_len = len(b_el.findall(".//w:tc", self.namespaces))
            h_len: int | None = None

            # 匹配结果
            success_num = 0

            if t_len == 1:
                h_len = b_len
                while 1:
                    bottom_point += 1
                    # 边界检查
                    if bottom_point >= all_tr_len:
                        bottom_point = all_tr_len - 1
                        break
                    b_el = tr_elements[bottom_point]
                    b_len = len(b_el.findall(".//w:tc", self.namespaces))
                    if b_len == h_len and self.is_tr_empty(b_el):
                        success_num += 1
                    else:
                        bottom_point -= 1
                        break
                if success_num >= 2:
                    self.currentTblElement.append(deepcopy(t_el))
                    self.load_new_template_tbl()
                    # 只提取 2 行
                    GET_LEN = 2
                    for _ in range(GET_LEN):
                        top_point += 1
                        # 边界检查
                        if top_point >= all_tr_len:
                            break
                        t_el = tr_elements[top_point]
                        t_len = len(t_el.findall(".//w:tc", self.namespaces))
                        self.currentTblElement.append(deepcopy(t_el))

                    self.load_new_template_tbl("repeat")
                    top_point = bottom_point + 1
                    bottom_point = top_point + 1
            else:
                if t_len == h_len:
                    self.currentTblElement.append(deepcopy(t_el))
                    top_point += 1
                    bottom_point += 1
                else:
                    if t_len != 1:
                        self.currentTblElement.append(deepcopy(t_el))
                        top_point += 1
                        bottom_point += 1

    def load_new_template_tbl(self, type: str = "normal"):
        self.tables.append(TableSplitResult(deepcopy(self.currentTblElement), type))
        self.currentTblElement = self.copyTemplateTbl()

    def is_tr_empty(self, tr_element: _Element) -> bool:
        """
        判断一个 tr 元素下的所有 tc 单元格是否都为空

        Args:
            tr_element: 要检查的 tr 元素

        Returns:
            bool: 如果所有单元格都为空返回 True，否则返回 False
        """
        # 获取所有的 tc 单元格
        tc_elements = tr_element.findall(".//w:tc", self.namespaces)

        # 如果没有单元格，认为是空的
        if not tc_elements:
            return True

        # 检查每个单元格
        for tc in tc_elements:
            # 查找单元格中的所有文本元素 w:t
            text_elements = tc.findall(".//w:t", self.namespaces)

            # 检查是否有非空文本
            for text_elem in text_elements:
                text_content = text_elem.text
                # 如果有非空且非空白的文本内容，则该单元格不为空
                if text_content and text_content.strip():
                    return False

        # 所有单元格都为空
        return True

    def copyTemplateTbl(self) -> _Element:
        newTblElement = etree.Element(f"{{{self.ns['w']}}}tbl", nsmap=self.namespaces)

        tbl_pr = self.tblElement.find("./w:tblPr", self.namespaces)
        if tbl_pr is not None:
            newTblElement.append(deepcopy(tbl_pr))

        tbl_grid = self.tblElement.find("./w:tblGrid", self.namespaces)
        if tbl_grid is not None:
            newTblElement.append(deepcopy(tbl_grid))

        return newTblElement

    def getTables(self) -> List[TableSplitResult]:
        return deepcopy(self.tables)


__all__ = ["TableSplitter"]
