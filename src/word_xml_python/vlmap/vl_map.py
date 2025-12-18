from lxml import etree
from ..core.constants import WORD_NAMESPACES, WORD_NS_URI

MAP_AI_TIP = """
上面是一个 Word 表格的可视化呈现。

## 你的角色
你是一个专业的 Word 表格结构分析专家。

## 任务
将上面的 Word 表格分割成多个独立的"内容区域"，重点是识别需要填写重复内容的区域。

## 区域类型定义
1. **Form（普通表单）**：字段标签与填写区域一一对应，没有重复的数据行结构
2. **RepeatTable（重复表）**：有明确的表头行 + 下方多行结构相同的空白数据行，需要注意的是识别出的第一行一定为表头行
3. **Left_RepeatTable（左重复表）**：左侧是标题列，右侧是上述第2条的RepeatTable（重复表）结构

## 输出格式
返回 JSON 数组，每个区域包含：
- name: 区域名称（中文描述）
- rows: 行号数组，从 1 开始，必须连续，如 [1, 2, 3]
- type: 只能是 "Form" | "RepeatTable" | "Left_RepeatTable" | "Right_RepeatTable"
- reason: 判断理由
- split_after_column: 仅 Left/Right_RepeatTable 需要，表示在第几列后切割（从 0 开始）

## 约束
- 所有行必须被覆盖，不能遗漏
- 行号不能重复
- rows 必须是连续整数

## 示例输出
[
  {
    "name": "基本信息表单",
    "rows": [1, 2],
    "type": "Form",
    "reason": "姓名、部门等单行字段，无重复结构"
  },
  {
    "name": "工作经历重复表",
    "rows": [3, 4, 5],
    "type": "RepeatTable",
    "reason": "第3行是表头（公司、职位、时间），第4-5行是结构相同的空白数据行"
  },
  {
    "name": "技能评分左重复表",
    "rows": [6, 7, 8],
    "type": "Left_RepeatTable",
    "split_after_column": 0,
    "reason": "第0列是技能名称标题，第1-3列是重复的评分结构"
  }
]只返回 JSON，不要其他解释。
"""

TABLE_ROW_SEPARATOR_LINE = 70


class Vlmap:
    table_xml_string: str
    tree: etree.Element
    row_span_map: dict[tuple[int, int], int]

    def __init__(self, table_xml_string: str):
        self.table_xml_string = table_xml_string
        self.tree = etree.fromstring(self.table_xml_string)
        self.row_span_map = {}

    def parse(self) -> str:
        vl = ""
        trs = self.tree.findall(".//w:tr", WORD_NAMESPACES)
        trLen = len(trs)

        self._calculate_row_spans(trs)

        vl += self.print_table_info(trLen)
        for row_idx, tr in enumerate(trs):
            vl += self.print_table_row(tr, row_idx)
        return vl

    def parse_and_tip(self) -> str:
        vl = self.parse()
        return vl + "\n" + MAP_AI_TIP

    def _calculate_row_spans(self, trs: list[etree.Element]):
        col_merge_state = {}

        for row_idx, tr in enumerate(trs):
            tcs = tr.findall(".//w:tc", WORD_NAMESPACES)
            col_idx = 0

            for tc in tcs:
                while col_idx in col_merge_state and col_merge_state[col_idx] > row_idx:
                    col_idx += 1

                tcPr = tc.find(".//w:tcPr", WORD_NAMESPACES)
                col_span = 1

                if tcPr is not None:
                    gridSpan = tcPr.find(".//w:gridSpan", WORD_NAMESPACES)
                    if gridSpan is not None:
                        col_span = int(gridSpan.get(f"{{{WORD_NS_URI}}}val", "1"))

                    vMerge = tcPr.find(".//w:vMerge", WORD_NAMESPACES)
                    if vMerge is not None:
                        vmerge_val = vMerge.get(f"{{{WORD_NS_URI}}}val", "continue")

                        if vmerge_val == "restart":
                            row_span = self._count_row_span(trs, row_idx, col_idx)
                            self.row_span_map[(row_idx, col_idx)] = row_span

                            for c in range(col_idx, col_idx + col_span):
                                col_merge_state[c] = row_idx + row_span - 1

                col_idx += col_span

    def _count_row_span(
        self, trs: list[etree.Element], start_row: int, col_idx: int
    ) -> int:
        span = 1
        for row_idx in range(start_row + 1, len(trs)):
            tr = trs[row_idx]
            tcs = tr.findall(".//w:tc", WORD_NAMESPACES)

            current_col = 0
            found = False

            for tc in tcs:
                if current_col == col_idx:
                    tcPr = tc.find(".//w:tcPr", WORD_NAMESPACES)
                    if tcPr is not None:
                        vMerge = tcPr.find(".//w:vMerge", WORD_NAMESPACES)
                        if vMerge is not None:
                            vmerge_val = vMerge.get(f"{{{WORD_NS_URI}}}val", "continue")
                            if vmerge_val == "continue" or vmerge_val is None:
                                span += 1
                                found = True
                                break
                    break

                tcPr = tc.find(".//w:tcPr", WORD_NAMESPACES)
                col_span = 1
                if tcPr is not None:
                    gridSpan = tcPr.find(".//w:gridSpan", WORD_NAMESPACES)
                    if gridSpan is not None:
                        col_span = int(gridSpan.get(f"{{{WORD_NS_URI}}}val", "1"))
                current_col += col_span

            if not found:
                break

        return span

    def print_table_info(self, trLen: int) -> str:
        table_info = ""
        table_info += "=" * TABLE_ROW_SEPARATOR_LINE
        table_info += "\n"
        table_info += f"这是一个word中的表格，表格行数: {trLen}"
        table_info += "\n"
        table_info += "=" * TABLE_ROW_SEPARATOR_LINE
        table_info += "\n"
        return table_info

    def print_table_row(self, tr: etree.Element, row_idx: int) -> str:
        cells = []
        col_idx = 0

        for tc in tr.findall(".//w:tc", WORD_NAMESPACES):
            cells.append(self.print_table_cell(tc, row_idx, col_idx))

            tcPr = tc.find(".//w:tcPr", WORD_NAMESPACES)
            col_span = 1
            if tcPr is not None:
                gridSpan = tcPr.find(".//w:gridSpan", WORD_NAMESPACES)
                if gridSpan is not None:
                    col_span = int(gridSpan.get(f"{{{WORD_NS_URI}}}val", "1"))
            col_idx += col_span

        row_info = f"第{row_idx + 1}行 | " + " | ".join(cells) + " |\n"
        row_info += "-" * TABLE_ROW_SEPARATOR_LINE + "\n"
        return row_info

    def print_table_cell(self, tc: etree.Element, row_idx: int, col_idx: int) -> str:
        wts = tc.findall(".//w:t", WORD_NAMESPACES)

        tcPr = tc.find(".//w:tcPr", WORD_NAMESPACES)
        merge_info = ""

        if tcPr is not None:
            gridSpan = tcPr.find(".//w:gridSpan", WORD_NAMESPACES)
            vMerge = tcPr.find(".//w:vMerge", WORD_NAMESPACES)

            col_span = 1
            row_span = 0

            if gridSpan is not None:
                col_span = int(gridSpan.get(f"{{{WORD_NS_URI}}}val", "1"))

            if vMerge is not None:
                vmerge_val = vMerge.get(f"{{{WORD_NS_URI}}}val", "continue")
                if vmerge_val == "restart":
                    row_span = self.row_span_map.get((row_idx, col_idx), 1)

            if col_span > 1 or row_span > 1:
                merge_parts = []
                if col_span > 1:
                    merge_parts.append(f"跨{col_span}列")
                if row_span > 1:
                    merge_parts.append(f"跨{row_span}行")
                merge_info = f"[{','.join(merge_parts)}]"

        if len(wts) > 0:
            content = "".join(wt.text or "" for wt in wts)
            return f"{content}{merge_info}" if merge_info else content
        else:
            return f"(空){merge_info}" if merge_info else "(空)"
