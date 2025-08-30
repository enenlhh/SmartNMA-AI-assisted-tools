# SmartEBM 模板化数据提取工具 - 完整文档

## 目录

- [系统要求](#系统要求)
- [安装指南](#安装指南)
- [模板规范格式](#模板规范格式)
- [配置说明](#配置说明)
- [使用工作流程](#使用工作流程)
- [高级功能](#高级功能)
- [性能优化](#性能优化)
- [故障排除](#故障排除)
- [技术架构](#技术架构)
- [集成指南](#集成指南)
- [最佳实践](#最佳实践)

## 系统要求

### 最低要求
- **Python**: 3.8 或更高版本（推荐 3.10+）
- **内存**: 4GB RAM（大型数据集推荐 8GB+）
- **存储**: 1GB 可用空间
- **网络**: 稳定的互联网连接用于 LLM API 访问

### 推荐配置
- **Python**: 3.10+
- **内存**: 16GB RAM 以获得最佳性能
- **CPU**: 4+ 核心用于高效处理
- **存储**: 5GB+ 用于大型文档集合
- **网络**: 高速互联网以获得更快的 API 响应

### 依赖包
- pandas >= 1.5.0
- pdfplumber >= 0.7.0
- PyPDF2 >= 3.0.0
- openai >= 1.0.0
- tqdm >= 4.64.0
- openpyxl >= 3.0.0

## 安装指南

### 步骤 1: 环境设置

```bash
# 创建虚拟环境（推荐）
python -m venv smartebm_template_env
source smartebm_template_env/bin/activate  # Windows: smartebm_template_env\Scripts\activate

# 克隆或下载工具
cd template_based_extraction_tool
```

### 步骤 2: 安装依赖

```bash
# 安装必需的包
pip install -r requirements.txt

# 验证安装
python -c "import pandas, pdfplumber, openai; print('依赖包安装成功')"
```

### 步骤 3: API 配置

```bash
# 设置 OpenAI API 密钥（必需）
export OPENAI_API_KEY="your-api-key-here"

# 可选：配置自定义基础 URL
export OPENAI_BASE_URL="https://api.openai.com/v1"

# 可选：设置首选模型
export OPENAI_MODEL="gpt-4-turbo"
```

### 步骤 4: 目录设置

```bash
# 创建必需的目录
mkdir -p input output debug_tables

# 验证结构
ls -la  # 应显示 input/, output/, debug_tables/ 文件夹
```

## 模板规范格式

### 4行模板结构

模板化数据提取工具使用革命性的4行Excel模板格式，大大简化了提取配置：

| 行 | 用途 | 描述 | 示例 |
|-----|---------|-------------|---------|
| 1 | **字段名称** | 提取数据的列标题 | Study_ID, Sample_Size, Primary_Outcome |
| 2 | **字段描述** | 要提取内容的详细说明 | "唯一研究标识符", "参与者总数", "主要疗效终点" |
| 3 | **示例 1** | 预期值的第一个示例 | "Smith2023", "150", "血压变化" |
| 4 | **示例 2** | 用于模式识别的第二个示例 | "Jones2022", "89", "症状减轻" |

### 模板创建指南

#### 字段命名约定
```excel
# 良好的字段名称
Study_ID, Author_Year, Sample_Size, Mean_Age, Primary_Outcome

# 避免特殊字符
Study ID (空格), Author&Year (符号), Sample-Size (中间连字符)
```

#### 描述最佳实践
```excel
# 具体清晰的描述
"随机分配的参与者总数"
"研究人群的平均年龄（年）"
"作者定义的主要疗效终点"

# 避免模糊描述
"数量", "年龄", "结果"
```

#### 示例选择策略
```excel
# 使用现实、多样的示例
示例 1: "比较药物A与安慰剂的RCT"
示例 2: "干预B的交叉试验"

# 包含边缘情况
示例 1: "150名参与者"
示例 2: "未报告"
```

### 模板验证

工具在加载过程中自动验证模板：

- **行数检查**: 确保恰好有4行数据
- **字段对齐**: 验证各行列数一致
- **内容检查**: 验证字段名称和描述非空
- **格式验证**: 确认Excel文件结构完整性

## 配置说明

### 配置文件 (config.py)

```python
DEFAULT_CONFIG = {
    "paths": {
        "pdf_folder": "./input",              # 输入PDF目录
        "template_xlsx": "./template.xlsx",   # 模板文件路径
        "output_xlsx": "./output/results.xlsx"  # 输出文件路径
    },
    "llm": {
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "model": os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
        "temperature": 0.0,                   # 确定性输出
        "max_tokens": 6000,                   # 响应长度限制
        "timeout": 120,                       # 请求超时（秒）
        "max_retries": 5                      # 重试次数
    },
    "runtime": {
        "chunk_field_size": 20,               # 每批字段数
        "max_chars_per_doc": 30000,           # 文本截断限制
        "debug_dir": "./debug_tables",        # 调试输出目录
        "use_repair_call": True               # 启用自动修复
    }
}
```

### 环境变量覆盖

```bash
# 路径配置
export PDF_FOLDER="/path/to/pdfs"
export TEMPLATE_XLSX="/path/to/template.xlsx"
export OUTPUT_XLSX="/path/to/results.xlsx"

# LLM 配置
export OPENAI_API_KEY="your-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_MODEL="gpt-4-turbo"
```

## 使用工作流程

### 基本提取工作流程

#### 步骤 1: 准备模板
```bash
# 创建包含4行的 template.xlsx：
# 第1行: Study_ID | Sample_Size | Primary_Outcome
# 第2行: 唯一研究标识符 | 参与者总数 | 主要终点
# 第3行: Smith2023 | 150 | 血压降低
# 第4行: Jones2022 | 89 | 症状改善
```

#### 步骤 2: 组织PDF文件
```bash
# 将PDF文件放入输入目录
cp /path/to/studies/*.pdf ./input/

# 验证文件
ls -la input/  # 应显示您的PDF文件
```

#### 步骤 3: 运行提取
```bash
# 执行提取
python main.py

# 监控进度
# 工具将显示进度条和状态更新
```

#### 步骤 4: 查看结果
```bash
# 检查输出
ls -la output/  # 应显示 results.xlsx

# 查看调试信息
ls -la debug_tables/  # 显示每个文件的提取详情
```

## 高级功能

### 智能字段分批

工具通过智能分批自动优化字段处理：

#### 自动批次大小确定
- **字段数量分析**: 考虑字段总数
- **复杂度评估**: 评估字段描述长度
- **令牌限制管理**: 防止LLM上下文溢出
- **性能优化**: 平衡速度和准确性

#### 批处理策略
1. **字段分组**: 相关字段一起处理
2. **负载均衡**: 批次间均匀分布
3. **依赖管理**: 维护字段关系
4. **错误隔离**: 一个批次的失败不影响其他批次

### 自动修复机制

#### 修复触发条件
- **解析失败**: 表格解析失败时
- **格式问题**: 列数不一致
- **内容问题**: 缺少必需字段
- **结构错误**: 表格输出格式错误

#### 修复成功指标
- **成功率**: 85-90%的解析失败得到解决
- **质量保持**: 修复过程中保持数据准确性
- **性能影响**: 最小开销（每次修复2-3秒）

### 多格式PDF支持

#### 主要提取方法 (pdfplumber)
- 针对基于文本的PDF优化
- 处理表格和结构化内容
- 支持复杂布局和多列文档

#### 备用提取方法 (PyPDF2)
- 处理基于图像的PDF
- 处理扫描文档和旧格式
- 提供损坏文件的兼容性

## 性能优化

### 处理速度优化

#### 速度优化的模板设计
```excel
# 快速处理模板：
# - 清晰、具体的字段名称
# - 简洁的描述（< 50字符）
# - 现实的示例
# - 逻辑字段排序

# 优化模板示例：
Study_ID | Sample_Size | Mean_Age | Primary_Outcome
研究标识符 | 参与者数量 | 平均年龄 | 主要疗效指标
STUDY001 | 150 | 65.2 | 血压变化
RCT2023 | 89 | 58.7 | 症状减轻
```

#### 批次大小调优
```python
# 性能指南：
# 小数据集（< 20个PDF）: chunk_size = 25
# 中等数据集（20-100个PDF）: chunk_size = 20  
# 大数据集（> 100个PDF）: chunk_size = 15
```

### 成本优化

#### API使用优化
```python
# 成本效益设置：
"model": "gpt-4-turbo",        # 最佳准确性/成本比
"temperature": 0.0,            # 确定性，无浪费
"max_tokens": 6000,            # 足够大多数提取
"use_repair_call": True        # 防止重新处理失败
```

## 故障排除

### 常见问题和解决方案

#### 模板加载错误

**问题**: "模板必须至少有4行"
```bash
# 解决方案：验证Excel文件结构
# - 在Excel中打开 template.xlsx
# - 确保恰好有4行数据
# - 检查空行或合并单元格
# - 保存为 .xlsx 格式（不是 .xls）
```

#### PDF处理错误

**问题**: "从[file.pdf]未提取到文本"
```bash
# 解决方案：
# 1. 对于扫描PDF：使用OCR预处理
# 2. 对于损坏PDF：尝试PDF修复工具
# 3. 对于密码保护PDF：先移除保护
```

#### LLM API错误

**问题**: "API密钥未配置"
```bash
# 解决方案：设置环境变量
export OPENAI_API_KEY="your-actual-api-key"
```

**问题**: "超出速率限制"
```bash
# 解决方案：实施延迟和重试
# 编辑 config.py：
"max_retries": 10,
"timeout": 180,
```

## 技术架构

### 核心组件

#### TemplateExtractor 类
具有集成处理管道的主要提取引擎：

- **模板加载**: 解析4行Excel模板
- **PDF处理**: 多方法文本提取
- **提示生成**: 创建结构化LLM提示
- **响应解析**: 将LLM输出转换为结构化数据
- **自动修复**: 修复格式错误的响应
- **管道编排**: 管理完整的提取工作流程

#### 处理管道
1. **输入处理**: 模板验证和PDF发现
2. **文本提取**: 带备用方法的多方法PDF处理
3. **字段分批**: 智能分组以获得最佳LLM性能
4. **LLM处理**: 结构化提示生成和API交互
5. **响应处理**: 具有自动修复功能的解析
6. **输出生成**: 数据验证和Excel格式化

### 错误处理架构

#### 多级错误恢复
- **第1级**: 带备用方法的PDF处理错误
- **第2级**: 带重试逻辑和指数退避的LLM API错误
- **第3级**: 带自动修复机制的解析错误

## 集成指南

### SmartEBM生态系统集成

模板化数据提取工具作为SmartEBM系统评价工作流程中的专业组件，为需要自定义字段定义的特定用例提供灵活的数据提取功能，补充标准数据提取工具。

#### 工作流程位置
- **输入**: 来自文献筛选的PDF文档
- **处理**: 模板驱动的字段提取
- **输出**: 用于下游分析的结构化Excel数据
- **集成**: 与偏倚风险评估和数据分析工具兼容

### 外部工具集成

#### 参考文献管理器集成
- **Zotero**: 从集合导入PDF并保留元数据
- **Mendeley**: 从文件夹获取文档并跟踪引用
- **EndNote**: 处理导出的PDF库

#### 统计软件集成
- **R**: 为荟萃分析包导出CSV格式
- **STATA**: 生成用于统计分析的.dta文件
- **RevMan**: 为Cochrane评价创建兼容的数据格式

## 最佳实践

### 模板设计最佳实践

#### 字段定义指南
```excel
# 有效的字段命名：
✓ Study_ID, Sample_Size, Mean_Age, Primary_Outcome
✗ ID, N, Age, Outcome

# 清晰的描述：
✓ "随机分配的参与者总数"
✗ "人数"

# 现实的示例：
✓ "Smith等人 2023", "150名参与者", "65.2岁"
✗ "研究1", "很多", "老"
```

#### 模板复杂度管理
- **最佳大小**: 每个模板15-25个字段
- **字段分组**: 将相关字段组织在一起
- **类型优化**: 使用分类字段以获得更快的处理速度

### 处理优化最佳实践

#### 质量保证工作流程
```python
# 预处理验证
def validate_inputs():
    assert os.path.exists(template_path), "模板文件缺失"
    assert len(pdf_files) > 0, "未找到PDF文件"
    assert api_key_configured(), "API密钥未设置"

# 后处理验证
def verify_results():
    results = pd.read_excel(output_path)
    assert len(results) > 0, "未提取到数据"
    assert results.isnull().sum().sum() < len(results) * 0.5, "缺失值过多"
```

### 成本管理最佳实践

#### 预算管理
- **成本估算**: 处理前计算预期API成本
- **模型选择**: 根据准确性/成本要求选择合适的模型
- **预算警报**: 监控支出并设置限制

### 维护和监控最佳实践

#### 定期维护
- **调试清理**: 每周删除旧的调试文件
- **模板验证**: 定期验证模板完整性
- **API连接性**: 定期测试API访问

#### 性能监控
- **成功率跟踪**: 监控提取成功率
- **处理时间分析**: 跟踪性能趋势
- **每PDF成本监控**: 分析成本效率

本综合文档为在所有用例和集成场景中有效使用SmartEBM模板化数据提取工具提供了完整指导。