from dataclasses import asdict
import json
from typing import List
from lxml import etree

from word_xml_python.models import VerifierMeta, ErrorInfo
from word_xml_python.core.constants import WORD_NAMESPACES


"""
当 AI 生成完成标准的 verifier_meta 后，需要通过这个类来验证生成的 verifier_meta 是否符合要求，这里验证的都是一些简单的结构问题，如果 AI 分析的正确，一定是
可以通过这个类验证的。所以需要用反复调用这个类来验证生成的 verifier_meta 是否符合要求。

MapVerifier 校验规则汇总：

一、全局校验
  1. 总行数一致：所有区域的 rows 行数之和必须等于表格实际行数
  2. 行号全覆盖：1~N 的每个行号都必须被某个区域覆盖，不能有遗漏
  3. 行号无重复：同一行号不能被多个区域重复使用

二、通用规则（适用于所有类型的区域）
  1. 行数非空：每个区域至少包含 1 行
  2. 行号连续：区域内的行号必须是连续的整数，如 [1,2,3]
  3. 行号有效：行号必须在 1~表格总行数 范围内

三、类型特定规则
  - Form：无额外要求
  - RepeatTable：至少 2 行（表头+数据），且第一行必须有内容
  - Left_RepeatTable：至少 2 行，且每行至少 2 列
  - Right_RepeatTable：至少 2 行，且每行至少 2 列
"""


class MapVerifier:
    metas: List[VerifierMeta] = []
    trs: List[etree._Element] = []

    def __init__(
        self,
        verifier_meta: List[VerifierMeta],
        trs: List[etree._Element],
    ):
        if verifier_meta and isinstance(verifier_meta[0], dict):
            self.metas = [VerifierMeta(**meta) for meta in verifier_meta]
        else:
            self.metas = verifier_meta
        self.trs = trs

    def verify(self) -> List[ErrorInfo]:
        error_infos: List[ErrorInfo] = []

        self._verify_trs_len(error_infos)
        self._verify_rows_coverage(error_infos)

        for meta in self.metas:
            self._verify_meta_rows(meta, error_infos)
        return error_infos

    def _verify_trs_len(self, error_infos: List[ErrorInfo]):
        tr_len = len(self.trs)
        meta_rows_len = sum(len(meta.rows) for meta in self.metas)
        if tr_len != meta_rows_len:
            error_infos.append(
                ErrorInfo(
                    source_meta=json.dumps(
                        [asdict(meta) for meta in self.metas], ensure_ascii=False
                    ),
                    error_msg=f"生成的数据行数，与我给你提供的表格行数不一致，请检查 我提供的表格共{tr_len}行，你生成的数据共{meta_rows_len}行",
                )
            )

    def _verify_rows_coverage(self, error_infos: List[ErrorInfo]):
        all_rows = []
        for meta in self.metas:
            all_rows.extend(meta.rows)

        expected = set(range(1, len(self.trs) + 1))
        actual = set(all_rows)

        missing = expected - actual
        if missing:
            error_infos.append(
                ErrorInfo(
                    source_meta=json.dumps(
                        [asdict(meta) for meta in self.metas], ensure_ascii=False
                    ),
                    error_msg=f"以下行号未被任何区域覆盖: {sorted(missing)}",
                )
            )

        duplicates = [r for r in all_rows if all_rows.count(r) > 1]
        if duplicates:
            error_infos.append(
                ErrorInfo(
                    source_meta=json.dumps(
                        [asdict(meta) for meta in self.metas], ensure_ascii=False
                    ),
                    error_msg=f"以下行号被多个区域重复使用: {sorted(set(duplicates))}",
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

    def _verify_common_rules(
        self, meta: VerifierMeta, error_infos: List[ErrorInfo]
    ) -> bool:
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
                    error_msg=f"区域'{meta.name}'行数为0",
                )
            )
            return False

        for i in range(1, len(meta.rows)):
            if meta.rows[i] != meta.rows[i - 1] + 1:
                error_infos.append(
                    ErrorInfo(
                        source_meta=json.dumps(asdict(meta), ensure_ascii=False),
                        error_msg=f"区域'{meta.name}'的行号不连续: {meta.rows}",
                    )
                )
                return False

        for row_num in meta.rows:
            row_idx = row_num - 1
            if row_idx < 0 or row_idx >= len(self.trs):
                error_infos.append(
                    ErrorInfo(
                        source_meta=json.dumps(asdict(meta), ensure_ascii=False),
                        error_msg=f"区域'{meta.name}'的行号{row_num}超出表格范围(1-{len(self.trs)})",
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

    def _verify_repeat_table_type(
        self, meta: VerifierMeta, error_infos: List[ErrorInfo]
    ):
        """
        验证重复表类型
        1. 至少需要2行（表头+至少1行数据）
        2. 第一行必须有内容（作为表头）
        """
        if len(meta.rows) < 2:
            error_infos.append(
                ErrorInfo(
                    source_meta=json.dumps(asdict(meta), ensure_ascii=False),
                    error_msg=f"区域'{meta.name}'标记为RepeatTable，但行数<2（至少需要表头+1行数据）",
                )
            )
            return

        first_row_idx = meta.rows[0] - 1
        first_tr = self.trs[first_row_idx]
        first_row_cells = first_tr.findall(".//w:tc", WORD_NAMESPACES)
        first_row_has_content = any(
            len(tc.findall(".//w:t", WORD_NAMESPACES)) > 0 for tc in first_row_cells
        )

        if not first_row_has_content:
            error_infos.append(
                ErrorInfo(
                    source_meta=json.dumps(asdict(meta), ensure_ascii=False),
                    error_msg=f"区域'{meta.name}'标记为RepeatTable，但第一行（第{meta.rows[0]}行）没有内容，无法作为表头",
                )
            )

    def _verify_left_repeat_table_type(
        self, meta: VerifierMeta, error_infos: List[ErrorInfo]
    ):
        """
        验证左重复表类型
        1. 至少需要2行
        2. 每行至少需要2列才能形成左右结构
        """
        if len(meta.rows) < 2:
            error_infos.append(
                ErrorInfo(
                    source_meta=json.dumps(asdict(meta), ensure_ascii=False),
                    error_msg=f"区域'{meta.name}'标记为Left_RepeatTable，但行数<2",
                )
            )
            return

        for row_num in meta.rows:
            row_idx = row_num - 1
            tr = self.trs[row_idx]
            cells = tr.findall(".//w:tc", WORD_NAMESPACES)
            if len(cells) < 2:
                error_infos.append(
                    ErrorInfo(
                        source_meta=json.dumps(asdict(meta), ensure_ascii=False),
                        error_msg=f"区域'{meta.name}'标记为Left_RepeatTable，但第{row_num}行只有{len(cells)}列，无法形成左右结构",
                    )
                )
                break

    def _verify_right_repeat_table_type(
        self, meta: VerifierMeta, error_infos: List[ErrorInfo]
    ):
        """
        验证右重复表类型
        1. 至少需要2行
        2. 每行至少需要2列才能形成左右结构
        """
        if len(meta.rows) < 2:
            error_infos.append(
                ErrorInfo(
                    source_meta=json.dumps(asdict(meta), ensure_ascii=False),
                    error_msg=f"区域'{meta.name}'标记为Right_RepeatTable，但行数<2",
                )
            )
            return

        for row_num in meta.rows:
            row_idx = row_num - 1
            tr = self.trs[row_idx]
            cells = tr.findall(".//w:tc", WORD_NAMESPACES)
            if len(cells) < 2:
                error_infos.append(
                    ErrorInfo(
                        source_meta=json.dumps(asdict(meta), ensure_ascii=False),
                        error_msg=f"区域'{meta.name}'标记为Right_RepeatTable，但第{row_num}行只有{len(cells)}列，无法形成左右结构",
                    )
                )
                break
