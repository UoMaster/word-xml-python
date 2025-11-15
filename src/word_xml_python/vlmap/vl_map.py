from lxml import etree

MAP_AI_TIP = """
上面是一个 Word 表格的可视化呈现。
任务：将这个表格分割成多个独立的"内容区域"。其实重点就是将表格中需要填写重复内容的区域分割出来。

判断依据：
1. **重复表(RepeatTable)**：必须有明确的表头行，下方包含多行结构相同的空白行用于填写重复数据。典型特征是有列标题和多行数据行。
2. **左右重复表(Left_RepeatTable/Right_RepeatTable)**：表格被垂直分割，一侧是标题，另一侧是重复表结构。
3. **普通表单(Form)**：其他所有不包含重复数据结构的区域，包括单行字段、跨行字段等。

关键识别特征：
- 重复表：有列标题 + 多行相同结构的空白数据行
- 表单：字段标签与填写区域一一对应，没有重复的数据行结构

请返回 JSON（只返回JSON，无需解释）：
[
  {
    "name": "", // 区域名称
    "rows": [], // int 的数组，表示区域行号 例如 [1, 2, 3]
    "type": "Form", // "Form" 或 "RepeatTable"
    "reason": "" // 原因描述
  },
]
• rows 必须是连续的整数数组
• type 只能是 "Form" 或 "RepeatTable" 或 "Left_RepeatTable" 或 "Right_RepeatTable"
"""

TABLE_ROW_SEPARATOR_LINE =  70

class Vlmap:
  table_xml_string: str 
  tree: etree.Element
  namespaces: dict[str, str]
  row_span_map: dict[tuple[int, int], int]

  def __init__(self, table_xml_string: str):
      self.table_xml_string = table_xml_string
      self.tree = etree.fromstring(self.table_xml_string)
      self.namespaces = self.tree.nsmap
      self.row_span_map = {}
      
  def parse(self) -> str:
    vl = ""
    trs = self.tree.findall(".//w:tr", self.namespaces)
    trLen = len(trs)
    
    self._calculate_row_spans(trs)
    
    vl += self.print_table_info(trLen)
    for row_idx, tr in enumerate(trs):
      vl += self.print_table_row(tr, row_idx)
    return vl  
  def _calculate_row_spans(self, trs: list[etree.Element]):
    col_merge_state = {}
    
    for row_idx, tr in enumerate(trs):
      tcs = tr.findall(".//w:tc", self.namespaces)
      col_idx = 0
      
      for tc in tcs:
        while col_idx in col_merge_state and col_merge_state[col_idx] > row_idx:
          col_idx += 1
        
        tcPr = tc.find(".//w:tcPr", self.namespaces)
        col_span = 1
        
        if tcPr is not None:
          gridSpan = tcPr.find(".//w:gridSpan", self.namespaces)
          if gridSpan is not None:
            col_span = int(gridSpan.get(f"{{{self.namespaces['w']}}}val", "1"))
          
          vMerge = tcPr.find(".//w:vMerge", self.namespaces)
          if vMerge is not None:
            vmerge_val = vMerge.get(f"{{{self.namespaces['w']}}}val", "continue")
            
            if vmerge_val == "restart":
              row_span = self._count_row_span(trs, row_idx, col_idx)
              self.row_span_map[(row_idx, col_idx)] = row_span
              
              for c in range(col_idx, col_idx + col_span):
                col_merge_state[c] = row_idx + row_span - 1
        
        col_idx += col_span
  
  def _count_row_span(self, trs: list[etree.Element], start_row: int, col_idx: int) -> int:
    span = 1
    for row_idx in range(start_row + 1, len(trs)):
      tr = trs[row_idx]
      tcs = tr.findall(".//w:tc", self.namespaces)
      
      current_col = 0
      found = False
      
      for tc in tcs:
        if current_col == col_idx:
          tcPr = tc.find(".//w:tcPr", self.namespaces)
          if tcPr is not None:
            vMerge = tcPr.find(".//w:vMerge", self.namespaces)
            if vMerge is not None:
              vmerge_val = vMerge.get(f"{{{self.namespaces['w']}}}val", "continue")
              if vmerge_val == "continue" or vmerge_val is None:
                span += 1
                found = True
                break
          break
        
        tcPr = tc.find(".//w:tcPr", self.namespaces)
        col_span = 1
        if tcPr is not None:
          gridSpan = tcPr.find(".//w:gridSpan", self.namespaces)
          if gridSpan is not None:
            col_span = int(gridSpan.get(f"{{{self.namespaces['w']}}}val", "1"))
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
    
    for tc in tr.findall(".//w:tc", self.namespaces):
      cells.append(self.print_table_cell(tc, row_idx, col_idx))
      
      tcPr = tc.find(".//w:tcPr", self.namespaces)
      col_span = 1
      if tcPr is not None:
        gridSpan = tcPr.find(".//w:gridSpan", self.namespaces)
        if gridSpan is not None:
          col_span = int(gridSpan.get(f"{{{self.namespaces['w']}}}val", "1"))
      col_idx += col_span
    
    row_info = f"第{row_idx + 1}行 | " + " | ".join(cells) + " |\n"
    row_info += "-" * TABLE_ROW_SEPARATOR_LINE + "\n"
    return row_info
  
  def print_table_cell(self, tc: etree.Element, row_idx: int, col_idx: int) -> str:
    wts = tc.findall(".//w:t", self.namespaces)
    
    tcPr = tc.find(".//w:tcPr", self.namespaces)
    merge_info = ""
    
    if tcPr is not None:
      gridSpan = tcPr.find(".//w:gridSpan", self.namespaces)
      vMerge = tcPr.find(".//w:vMerge", self.namespaces)
      
      col_span = 1
      row_span = 0
      
      if gridSpan is not None:
        col_span = int(gridSpan.get(f"{{{self.namespaces['w']}}}val", "1"))
      
      if vMerge is not None:
        vmerge_val = vMerge.get(f"{{{self.namespaces['w']}}}val", "continue")
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
   