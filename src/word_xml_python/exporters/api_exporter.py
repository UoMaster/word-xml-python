"""API导出器 - 提供HTTP接口处理Word XML"""

from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from ..split import TableSplitResult
from .. import process_word_table_from_xml


# 创建FastAPI应用
app = FastAPI(
    title="Word XML Parser API",
    description="用于解析Word XML文档并提取表格数据的API",
    version="1.0.0",
)


class CellInfoResponse(BaseModel):
    """单元格信息响应模型"""

    key: str
    row_span: int
    col_span: int
    body: List[Dict[str, Any]]
    is_empty_cell: bool
    left_cell_key: str | None
    top_cell_key: str | None


class TableInfoResponse(BaseModel):
    """表格信息响应模型"""

    table_type: str
    cells: List[CellInfoResponse]
    csv_string: str


class ProcessResponse(BaseModel):
    """处理响应模型"""

    success: bool
    message: str
    tables: List[TableInfoResponse]


def convert_cell_to_dict(cell) -> Dict[str, Any]:
    """将CellInfo对象转换为字典"""
    return {
        "key": cell.key,
        "row_span": cell.row_span,
        "col_span": cell.col_span,
        "body": [
            {
                "pStyle": p.pStyle,
                "rList": [{"rStyle": r.rStyle, "body": r.body} for r in p.rList],
            }
            for p in cell.body
        ],
        "is_empty_cell": cell.is_empty_cell,
        "left_cell_key": cell.left_cell_key,
        "top_cell_key": cell.top_cell_key,
    }


def convert_table_to_dict(table: TableSplitResult) -> Dict[str, Any]:
    """将TableSplitResult对象转换为字典"""
    return {
        "table_type": table.table_type,
        "cells": [convert_cell_to_dict(cell) for cell in (table.table_cell_list or [])],
        "csv_string": table.table_cell_csv_str or "",
    }


@app.post("/api/parse-xml", response_model=ProcessResponse)
async def parse_xml(request: Request):
    """
    解析Word XML字符串并返回表格数据

    Args:
        request: 原始请求对象，body包含XML字符串

    Returns:
        处理结果，包含所有表格的信息和单元格数据

    Example:
        POST /api/parse-xml
        Content-Type: text/plain
        Body: <w:document>...</w:document>
    """
    try:
        # 读取原始XML字符串
        xml_content = await request.body()
        xml_string = xml_content.decode("utf-8")
        print(xml_string)

        # 处理XML字符串
        tables = process_word_table_from_xml(xml_string)

        # 转换为响应格式
        table_responses = [convert_table_to_dict(table) for table in tables]

        return ProcessResponse(
            success=True,
            message=f"成功解析 {len(tables)} 个表格",
            tables=table_responses,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"XML解析错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "name": "Word XML Parser API",
        "version": "1.0.0",
        "endpoints": {"parse_xml": "/api/parse-xml (POST)"},
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
