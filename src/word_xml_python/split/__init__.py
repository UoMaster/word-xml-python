from copy import deepcopy
from lxml.etree import _Element
from typing import Dict, List
from ..models import VerifierMeta
from lxml import etree

from dataclasses import dataclass


@dataclass
class TableSplitResult:
    """表格分割结果"""

    table_xml: str
    table_type: str


class TableSplitter:
    """表格分割器"""

    tblElement: _Element
    namespaces: Dict[str, str]
    verifier_meta: List[VerifierMeta]
    _current_template_xml: _Element
    _all_tr: List[_Element]
    result: List[TableSplitResult]

    def __init__(
        self,
        tblElement: _Element,
        namespaces: Dict[str, str],
        verifier_meta: List[VerifierMeta],
    ):
        self.tblElement = tblElement
        self.namespaces = namespaces
        self.verifier_meta = verifier_meta
        self._all_tr = self.tblElement.findall(".//w:tr", self.namespaces)
        self.result = []

    def create_template_xml(self) -> _Element:
        tbl: _Element = deepcopy(self.tblElement)
        for tr in tbl.findall(".//w:tr", self.namespaces):
            tbl.remove(tr)
        return tbl

    def set_current_template_xml(self):
        self.current_template_xml = self.create_template_xml()

    def template_xml_to_str(self) -> str:
        return etree.tostring(
            self.current_template_xml, pretty_print=True, encoding="UTF-8"
        ).decode("UTF-8")

    def split(self) -> List[TableSplitResult]:
        verifier_meta = self.verifier_meta
        for meta in verifier_meta:
            self.set_current_template_xml()
            if meta.type == "Form":
                self._split_form(meta)
            elif meta.type == "RepeatTable":
                self._split_repeat_table(meta)
            elif meta.type == "Left_RepeatTable":
                self._split_left_repeat_table(meta)
        return self.result

    def _extract_cell_text(self, tc_element: _Element) -> str:
        texts = []
        for t in tc_element.findall(".//w:t", self.namespaces):
            if t.text:
                texts.append(t.text)
        return "".join(texts)

    def _create_single_cell_table(self, text: str) -> _Element:
        tbl = self.create_template_xml()

        w_ns = self.namespaces.get(
            "w", "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        )

        # tr -> tc -> p -> r -> t
        tr = etree.Element(f"{{{w_ns}}}tr")
        tc = etree.SubElement(tr, f"{{{w_ns}}}tc")
        p = etree.SubElement(tc, f"{{{w_ns}}}p")
        r = etree.SubElement(p, f"{{{w_ns}}}r")
        t = etree.SubElement(r, f"{{{w_ns}}}t")
        t.text = text

        tbl.append(tr)
        return tbl

    def _split_form(self, meta: VerifierMeta):
        current_template_xml = self.current_template_xml

        for row_num in meta.rows:
            tr = self._all_tr[row_num - 1]
            current_template_xml.append(tr)

        self.result.append(
            TableSplitResult(table_xml=self.template_xml_to_str(), table_type=meta.type)
        )

    def _split_repeat_table(self, meta: VerifierMeta):
        meta.rows = [meta.rows[0], meta.rows[1]]
        self._split_form(meta)

    def _split_left_repeat_table(self, meta: VerifierMeta):
        split_after_column = (
            meta.split_after_column if meta.split_after_column is not None else 0
        )
        namespaces = self.namespaces

        rows_to_process = [self._all_tr[row_num - 1] for row_num in meta.rows]

        for col_idx in range(split_after_column + 1):
            col_texts = []
            for tr in rows_to_process:
                tcs = tr.findall(".//w:tc", namespaces)
                if col_idx < len(tcs):
                    cell_text = self._extract_cell_text(tcs[col_idx])
                    if cell_text:
                        col_texts.append(cell_text)

            merged_text = " ".join(col_texts)

            single_cell_table = self._create_single_cell_table(merged_text)
            self.result.append(
                TableSplitResult(
                    table_xml=etree.tostring(
                        single_cell_table, pretty_print=True, encoding="UTF-8"
                    ).decode("UTF-8"),
                    table_type=meta.type,
                )
            )

        right_table = self.create_template_xml()

        rows_for_repeat = (
            rows_to_process[:2] if len(rows_to_process) >= 2 else rows_to_process
        )

        for tr in rows_for_repeat:
            new_tr = deepcopy(tr)
            tcs = new_tr.findall(".//w:tc", namespaces)

            for col_idx in range(split_after_column, -1, -1):
                if col_idx < len(tcs):
                    new_tr.remove(tcs[col_idx])

            right_table.append(new_tr)

        self.result.append(
            TableSplitResult(
                table_xml=etree.tostring(
                    right_table, pretty_print=True, encoding="UTF-8"
                ).decode("UTF-8"),
                table_type=meta.type,
            )
        )


__all__ = ["TableSplitter"]
