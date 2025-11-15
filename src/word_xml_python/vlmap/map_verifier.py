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

