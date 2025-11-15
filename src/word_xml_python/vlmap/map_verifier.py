from dataclasses import dataclass, asdict
import json
from typing import Dict, List
from lxml import etree
@dataclass
class VerifierMeta:
  name: str
  rows: List[int]
  type: str
  reason: str

@dataclass
class ErrorInfo:
  source_meta: str
  error_msg: str

class MapVerifier:
  metas: List[VerifierMeta] = []
  trs: List[etree._Element] = []
  namespaces: Dict[str, str] = {}

  def __init__(self,verifier_meta:List[VerifierMeta], trs: List[etree._Element], namespaces: Dict[str, str]):
    if verifier_meta and isinstance(verifier_meta[0], dict):
      self.metas = [VerifierMeta(**meta) for meta in verifier_meta]
    else:
      self.metas = verifier_meta
    self.trs = trs
    self.namespaces = namespaces

  def verify(self) -> List[ErrorInfo]:
    error_infos: List[ErrorInfo] = []

    # 首先确认trs的行数是否与叠加的verifier_meta的rows的行数一致
    self._verify_trs_len(error_infos)
    
    # 遍历metas，逐行验证
    for meta in self.metas:
      self._verify_meta_rows(meta, error_infos)
    return error_infos

  
  def _verify_trs_len(self, error_infos: List[ErrorInfo]):
    tr_len = len(self.trs)
    meta_rows_len = sum(len(meta.rows) for meta in self.metas)
    if tr_len != meta_rows_len:
      error_infos.append(
        ErrorInfo(
          source_meta=json.dumps([asdict(meta) for meta in self.metas], ensure_ascii=False),
          error_msg=f"生成的数据行数，与我给你提供的表格行数不一致，请检查 我提供的表格共{tr_len}行，你生成的数据共{meta_rows_len}行"
        )
      )

  def _verify_meta_rows(self, meta: VerifierMeta, error_infos: List[ErrorInfo]):
    if not self._verify_common_rules(meta, error_infos):
      return
    
    type = meta.type
    if type == "Form":
      self._verify_form_type(meta, error_infos)
    elif type == "RepeatTable":
      self._verify_repeat_table_type(meta, error_infos)
    elif type == "Left_RepeatTable":
      self._verify_left_repeat_table_type(meta, error_infos)
    elif type == "Right_RepeatTable":
      self._verify_right_repeat_table_type(meta, error_infos)
  
  def _verify_common_rules(self, meta: VerifierMeta, error_infos: List[ErrorInfo]) -> bool:
    """
    验证所有类型通用的基本规则
    1. 行数不能为0
    2. 行号必须连续（符合提示词要求）
    3. 行号必须在有效范围内
    """
    if len(meta.rows) < 1:
      error_infos.append(
        ErrorInfo(
          source_meta=json.dumps(asdict(meta), ensure_ascii=False),
          error_msg=f"区域'{meta.name}'行数为0"
        )
      )
      return False
    
    for i in range(1, len(meta.rows)):
      if meta.rows[i] != meta.rows[i-1] + 1:
        error_infos.append(
          ErrorInfo(
            source_meta=json.dumps(asdict(meta), ensure_ascii=False),
            error_msg=f"区域'{meta.name}'的行号不连续: {meta.rows}"
          )
        )
        return False
    
    for row_num in meta.rows:
      row_idx = row_num - 1
      if row_idx < 0 or row_idx >= len(self.trs):
        error_infos.append(
          ErrorInfo(
            source_meta=json.dumps(asdict(meta), ensure_ascii=False),
            error_msg=f"区域'{meta.name}'的行号{row_num}超出表格范围(1-{len(self.trs)})"
          )
        )
        return False
    
    return True
  
  def _verify_form_type(self, meta: VerifierMeta, error_infos: List[ErrorInfo]):
    """
    验证普通表单类型
    Form类型只需通过公共规则验证即可，无额外特殊要求
    """
    pass

  def _verify_repeat_table_type(self, meta: VerifierMeta, error_infos: List[ErrorInfo]):
    """
    验证重复表类型
    1. 至少需要2行（表头+至少1行数据）
    2. 第一行必须有内容（作为表头）
    """
    if len(meta.rows) < 2:
      error_infos.append(
        ErrorInfo(
          source_meta=json.dumps(asdict(meta), ensure_ascii=False),
          error_msg=f"区域'{meta.name}'标记为RepeatTable，但行数<2（至少需要表头+1行数据）"
        )
      )
      return
    
    first_row_idx = meta.rows[0] - 1
    first_tr = self.trs[first_row_idx]
    first_row_cells = first_tr.findall(".//w:tc", self.namespaces)
    first_row_has_content = any(
      len(tc.findall(".//w:t", self.namespaces)) > 0 for tc in first_row_cells
    )
    
    if not first_row_has_content:
      error_infos.append(
        ErrorInfo(
          source_meta=json.dumps(asdict(meta), ensure_ascii=False),
          error_msg=f"区域'{meta.name}'标记为RepeatTable，但第一行（第{meta.rows[0]}行）没有内容，无法作为表头"
        )
      )

  def _verify_left_repeat_table_type(self, meta: VerifierMeta, error_infos: List[ErrorInfo]):
    """
    验证左重复表类型
    1. 至少需要2行
    2. 每行至少需要2列才能形成左右结构
    """
    if len(meta.rows) < 2:
      error_infos.append(
        ErrorInfo(
          source_meta=json.dumps(asdict(meta), ensure_ascii=False),
          error_msg=f"区域'{meta.name}'标记为Left_RepeatTable，但行数<2"
        )
      )
      return
    
    for row_num in meta.rows:
      row_idx = row_num - 1
      tr = self.trs[row_idx]
      cells = tr.findall(".//w:tc", self.namespaces)
      if len(cells) < 2:
        error_infos.append(
          ErrorInfo(
            source_meta=json.dumps(asdict(meta), ensure_ascii=False),
            error_msg=f"区域'{meta.name}'标记为Left_RepeatTable，但第{row_num}行只有{len(cells)}列，无法形成左右结构"
          )
        )
        break

  def _verify_right_repeat_table_type(self, meta: VerifierMeta, error_infos: List[ErrorInfo]):
    """
    验证右重复表类型
    1. 至少需要2行
    2. 每行至少需要2列才能形成左右结构
    """
    if len(meta.rows) < 2:
      error_infos.append(
        ErrorInfo(
          source_meta=json.dumps(asdict(meta), ensure_ascii=False),
          error_msg=f"区域'{meta.name}'标记为Right_RepeatTable，但行数<2"
        )
      )
      return
    
    for row_num in meta.rows:
      row_idx = row_num - 1
      tr = self.trs[row_idx]
      cells = tr.findall(".//w:tc", self.namespaces)
      if len(cells) < 2:
        error_infos.append(
          ErrorInfo(
            source_meta=json.dumps(asdict(meta), ensure_ascii=False),
            error_msg=f"区域'{meta.name}'标记为Right_RepeatTable，但第{row_num}行只有{len(cells)}列，无法形成左右结构"
          )
        )
        break