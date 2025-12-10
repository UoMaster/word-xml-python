# Word XML Python

一个用于解析和处理 Word XML 文档的 Python 库，专注于表格数据的提取与处理。

## ✨ 功能特性

- 📄 **DOCX 解压** - 将 `.docx` 文件解压为 XML 元数据
- 📊 **表格解析** - 解析 Word XML 中的表格结构，支持合并单元格
- 🔀 **表格分割** - 智能识别并分割表格中的不同区域（表单、重复表等）
- 📤 **多格式导出** - 将表格数据导出为 CSV 或字符串
- 🤖 **AI 辅助** - VL Map 可视化表格，辅助 AI 进行表格区域分割

## 📦 安装

```bash
# 使用 Poetry 安装
poetry install

# 或使用 pip
pip install -r requirements-api.txt
```

### 依赖要求

- Python >= 3.13
- lxml >= 6.0.2
- pandas >= 2.3.3
- FastAPI >= 0.121.1 (API 服务)
- uvicorn >= 0.38.0 (API 服务)

## 🚀 快速开始

### 1. 解压 DOCX 文件

```bash
# 将 .docx 文件解压为 XML 元数据
make extract DOCX=path/to/your/file.docx
```

或在代码中使用：

```python
from examples.word_to_xml import extract_docx_to_meta

meta_dir = extract_docx_to_meta("path/to/file.docx", "output_dir")
```

### 2. 处理表格数据

```python
from word_xml_python import process_word_table, export_to_csv

# 解析 XML 文档中的表格
tables = process_word_table("word_meta/word/document.xml")

# 遍历每个表格
for idx, table in enumerate(tables):
    print(f"表格 {idx}: {table.table_type}")
    print(f"单元格数量: {len(table.table_cell_list)}")
    
    # 导出为 CSV
    export_to_csv(table.table_cell_list, f"output_{idx}.csv")
```

### 3. 从 XML 字符串处理

```python
from word_xml_python import process_word_table_from_xml

xml_content = "<w:document>...</w:document>"
tables = process_word_table_from_xml(xml_content)
```

## 📖 API 参考

### 便捷函数

| 函数 | 描述 |
|------|------|
| `process_word_table(file_path)` | 从文件路径处理 Word 表格 |
| `process_word_table_from_xml(xml_string)` | 从 XML 字符串处理 Word 表格 |
| `export_to_csv(cell_list, output_path)` | 导出单元格数据到 CSV 文件 |
| `export_to_str(cell_list)` | 将单元格数据转换为 CSV 字符串 |

### 核心类

| 类 | 描述 |
|----|------|
| `WordXMLParser` | Word XML 文档解析器 |
| `TableExtractor` | 表格信息提取器 |
| `CellExtractor` | 单元格信息提取器 |
| `CSVExporter` | CSV 导出器 |
| `TableSplitter` | 表格分割器 |
| `Vlmap` | 表格可视化映射 |
| `MapVerifier` | 映射验证器 |

### 数据模型

| 模型 | 描述 |
|------|------|
| `TableInfo` | 表格元数据（行数、列数） |
| `CellInfo` | 单元格信息（位置、合并信息、内容） |
| `TableSplitResult` | 表格分割结果 |

## 🛠️ 开发命令

```bash
# 运行 API 服务
make api

# 运行快速演示
make demo

# 解压 DOCX 文件
make extract DOCX=word/请假表.docx

# 生成 VL Map（可视化表格）
make vl

# 验证 VL Map
make vl_v
```

## 🏗️ 项目结构

```
word-xml-python/
├── src/word_xml_python/     # 主包
│   ├── models/              # 数据模型层
│   ├── parser/              # XML 解析层
│   ├── extractors/          # 数据提取层
│   ├── exporters/           # 数据导出层
│   ├── split/               # 表格分割
│   ├── vlmap/               # 可视化映射
│   └── core/                # 核心配置
├── examples/                # 示例代码
├── tests/                   # 测试
└── word_meta/               # 解压后的 Word 元数据
```

## 📄 VL Map 功能

VL Map 是一个将 Word 表格可视化为文本格式的工具，主要用于辅助 AI 理解表格结构：

```python
from word_xml_python import Vlmap
from lxml import etree

# 读取表格 XML
xml_bytes = open("word_meta/word/document.xml", "rb").read()
tree = etree.fromstring(xml_bytes)
namespaces = tree.nsmap

# 创建 VL Map
table_xml = etree.tostring(tree.find(".//w:tbl", namespaces))
vlmap = Vlmap(table_xml)

# 生成可视化文本
print(vlmap.parse())

# 生成带 AI 提示的文本
print(vlmap.parse_and_tip())
```

输出示例：
```
======================================================================
这是一个word中的表格，表格行数: 5
======================================================================
第1行 | 姓名 | (空) | 部门 | (空) |
----------------------------------------------------------------------
第2行 | 请假类型[跨2列] | 开始时间 | 结束时间 |
----------------------------------------------------------------------
...
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 License

MIT License
