# 架构文档

## 项目结构

```
word-xml-python/
├── src/
│   └── word_xml_python/          # 主包
│       ├── __init__.py            # 公共API和便捷函数
│       ├── models/                # 数据模型层
│       │   ├── __init__.py
│       │   ├── table.py           # 表格信息模型
│       │   └── cell.py            # 单元格信息模型
│       ├── parser/                # 解析层
│       │   ├── __init__.py
│       │   └── xml_parser.py      # Word XML解析器
│       ├── extractors/            # 提取层
│       │   ├── __init__.py
│       │   ├── table_extractor.py # 表格信息提取器
│       │   └── cell_extractor.py  # 单元格信息提取器
│       ├── exporters/             # 导出层
│       │   ├── __init__.py
│       │   └── csv_exporter.py    # CSV导出器
│       └── core/                  # 核心配置层
│           ├── __init__.py
│           └── constants.py       # 常量定义
├── examples/                      # 示例代码
│   ├── __init__.py
│   └── basic_usage.py             # 基础使用示例
├── tests/                         # 测试
│   └── __init__.py
├── quick_demo.py                  # 快速演示
├── pyproject.toml                 # 项目配置
└── README.md                      # 项目文档
```

## 架构设计

### 设计原则

1. **单一职责原则** - 每个模块只负责一个功能领域
2. **开放封闭原则** - 易于扩展新功能，无需修改现有代码
3. **依赖倒置原则** - 高层模块不依赖底层模块，都依赖于抽象
4. **模块化设计** - 清晰的层次结构，便于维护和测试

### 分层架构

#### 1. 数据模型层 (models/)

**职责**: 定义核心数据结构

- `TableInfo`: 表格元数据（行数、列数）
- `CellInfo`: 单元格信息（位置、合并信息、内容）

**特点**:
- 使用 `dataclass` 实现，代码简洁
- 提供 `to_dict()` 方法方便数据转换
- 不包含业务逻辑，纯数据对象

#### 2. 解析层 (parser/)

**职责**: 处理XML文档的解析和命名空间管理

- `WordXMLParser`: 解析Word XML文档，管理命名空间

**特点**:
- 封装 lxml 的复杂性
- 统一处理命名空间
- 提供友好的查询接口

#### 3. 提取层 (extractors/)

**职责**: 从XML元素中提取结构化数据

- `TableExtractor`: 提取表格整体信息
- `CellExtractor`: 提取单元格详细信息，处理合并逻辑

**特点**:
- 关注点分离：表格和单元格分别处理
- 封装复杂的合并单元格逻辑
- 维护行合并状态

#### 4. 导出层 (exporters/)

**职责**: 将数据导出为不同格式

- `CSVExporter`: 导出为CSV格式

**特点**:
- 易于扩展（可添加 JSONExporter、ExcelExporter 等）
- 统一的导出接口
- 利用 pandas 进行数据处理

#### 5. 核心配置层 (core/)

**职责**: 存放常量和配置

- `constants.py`: 定义全局常量

**特点**:
- 集中管理配置
- 避免魔法数字和字符串
- 便于修改和维护

### 数据流

```
Word XML文件
    ↓
WordXMLParser (解析)
    ↓
XML Element Tree
    ↓
TableExtractor → TableInfo (表格信息)
    ↓
CellExtractor → List[CellInfo] (单元格列表)
    ↓
CSVExporter → CSV文件
```

### API设计

#### 两种使用方式

**方式一：便捷函数（推荐新手）**

```python
from word_xml_python import process_word_table, export_to_csv

table_info, cell_list = process_word_table("document.xml")
export_to_csv(cell_list, "output.csv")
```

**方式二：完整API（高级用户）**

```python
from word_xml_python import (
    WordXMLParser, TableExtractor, CellExtractor, CSVExporter
)

parser = WordXMLParser("document.xml")
parser.parse()
table_element = parser.find_table()

table_extractor = TableExtractor(parser.get_namespaces())
table_info = table_extractor.extract(table_element)

cell_extractor = CellExtractor(parser.get_namespaces())
cell_list = cell_extractor.extract_all(table_element)

CSVExporter.export(cell_list, "output.csv")
```

## 扩展性

### 添加新的提取器

```python
# src/word_xml_python/extractors/image_extractor.py
class ImageExtractor:
    def extract_all(self, element):
        # 实现图片提取逻辑
        pass
```

### 添加新的导出器

```python
# src/word_xml_python/exporters/json_exporter.py
class JSONExporter:
    @staticmethod
    def export(data, output_path):
        # 实现JSON导出逻辑
        pass
```

### 添加新的模型

```python
# src/word_xml_python/models/paragraph.py
@dataclass
class ParagraphInfo:
    text: str
    style: str
```

## 测试策略

- **单元测试**: 每个模块独立测试
- **集成测试**: 测试完整的数据流
- **fixtures**: 使用测试XML文件

## 最佳实践

1. **类型注解**: 所有函数都有完整的类型注解
2. **文档字符串**: 遵循 Google 风格的 docstring
3. **错误处理**: 提供清晰的错误信息
4. **代码风格**: 遵循 PEP 8 规范
5. **命名规范**: 使用描述性的变量和函数名

## 性能考虑

- 使用 lxml 的 C 扩展，保证解析性能
- 单次遍历处理单元格，避免重复解析
- 使用 pandas 批量处理数据导出

## 未来规划

- [ ] 添加更多导出格式（JSON, Excel, HTML）
- [ ] 支持多表格处理
- [ ] 提取单元格实际内容（当前为占位符）
- [ ] 添加单元格样式信息提取
- [ ] 支持图片和其他媒体元素
- [ ] 添加完整的单元测试覆盖
- [ ] 性能优化和基准测试
- [ ] CLI 命令行工具

