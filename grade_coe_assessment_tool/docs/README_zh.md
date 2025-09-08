# GRADE 证据质量评估工具 - 完整文档

## 目录

- [系统要求](#系统要求)
- [安装指南](#安装指南)
- [配置说明](#配置说明)
- [使用流程](#使用流程)
- [GRADE框架集成](#grade框架集成)
- [评估工作流程](#评估工作流程)
- [交互式报告生成](#交互式报告生成)
- [高级功能](#高级功能)
- [性能优化](#性能优化)
- [故障排除](#故障排除)
- [技术架构](#技术架构)
- [集成指南](#集成指南)
- [最佳实践](#最佳实践)

## 系统要求

### 硬件要求
- **内存**: 最低4GB，推荐8GB用于大型数据集
- **存储空间**: 至少1GB可用空间用于分析结果和报告
- **处理器**: 推荐多核处理器用于批量处理

### 软件依赖
- **Python**: 版本3.8或更高
- **必需包**: 列在`requirements.txt`中
- **网页浏览器**: 现代浏览器用于交互式报告（Chrome、Firefox、Safari、Edge）

### 输入数据要求
- R netmeta包的网络荟萃分析结果
- 标准化文件结构与结局目录
- 纳入研究的偏倚风险评估
- 分析设置和配置文件

## 安装指南

### 步骤1：克隆或下载
```bash
# 如果使用git
git clone [repository-url]
cd grade_coe_assessment_tool

# 或下载并解压工具包
```

### 步骤2：安装依赖
```bash
# 安装必需的Python包
pip install -r requirements.txt

# 用于开发环境
pip install -r requirements.txt --upgrade
```

### 步骤3：验证安装
```bash
# 测试安装
python -c "from src.grade_evaluator import GradeEvaluator; print('安装成功')"
```

## 配置说明

### 基本配置

工具使用`config.json`文件进行配置。在根目录创建此文件：

```json
{
    "data_settings": {
        "base_dir": "/path/to/your/nma/results",
        "output_dir": "/path/to/output/directory"
    },
    "mid_params": {
        "harmful_mid": null,
        "benefit_mid": null
    },
    "rob_params": {
        "high_risk_count_threshold": 0.5,
        "high_risk_weight_threshold": 50,
        "very_serious_weight_threshold": 80
    },
    "inconsistency_params": {
        "i2_threshold": 60,
        "i2_very_serious_threshold": 90,
        "ci_overlap_threshold": 0.5
    }
}
```

### 配置参数

#### 数据设置
- **base_dir**: 包含NMA分析结果的根目录
- **output_dir**: 保存GRADE评估结果的目录

#### MID参数（最小重要差异）
- **harmful_mid**: 有害效应阈值（例如，OR为1.25）
- **benefit_mid**: 有益效应阈值（例如，OR为0.75）
- 设置为`null`使用默认值

#### 偏倚风险参数
- **high_risk_count_threshold**: 高风险研究比例阈值（默认：0.5）
- **high_risk_weight_threshold**: 严重关注的权重百分比阈值（默认：50%）
- **very_serious_weight_threshold**: 非常严重关注的权重百分比阈值（默认：80%）

#### 不一致性参数
- **i2_threshold**: 严重不一致性的I²阈值（默认：60%）
- **i2_very_serious_threshold**: 非常严重不一致性的I²阈值（默认：90%）
- **ci_overlap_threshold**: 置信区间重叠阈值（默认：0.5）

### 可定制的判断阈值

工具允许研究者定制GRADE评估标准：

#### 偏倚风险阈值
```json
"rob_params": {
    "high_risk_count_threshold": 0.3,  // 30%的研究
    "high_risk_weight_threshold": 40,   // 40%权重阈值
    "very_serious_weight_threshold": 70 // 70%用于非常严重
}
```

#### 不一致性阈值
```json
"inconsistency_params": {
    "i2_threshold": 50,           // 保守评估的较低阈值
    "i2_very_serious_threshold": 85,
    "ci_overlap_threshold": 0.3   // 更严格的重叠要求
}
```

## 使用流程

### 交互式网页界面

1. **启动应用程序**
   ```bash
   streamlit run app.py
   ```

2. **选择分析参数**
   - 从可用选项中选择结局
   - 选择模型类型（随机或固定效应）
   - 查看配置设置

3. **运行评估**
   - 点击"开始GRADE评估"
   - 实时监控进度
   - 在交互式表格中查看结果

4. **导出结果**
   - 下载包含完整评估的Excel文件
   - 生成交互式HTML报告

### 命令行界面

1. **基本使用**
   ```bash
   python run.py
   ```

2. **程序化使用**
   ```python
   from src.grade_evaluator import GradeEvaluator
   
   evaluator = GradeEvaluator(
       base_dir="/path/to/nma/results",
       outcome_name="primary_outcome",
       model_type="random"
   )
   
   results = evaluator.evaluate_grade()
   ```

### 批量处理

对于多个结局：

```python
import os
from src.grade_evaluator import GradeEvaluator, list_available_outcomes

base_dir = "/path/to/nma/results"
outcomes = list_available_outcomes(base_dir)

for outcome_info in outcomes:
    for model in outcome_info['models']:
        evaluator = GradeEvaluator(
            base_dir=base_dir,
            outcome_name=outcome_info['outcome'],
            model_type=model
        )
        results = evaluator.evaluate_grade()
        # 保存结果
```

## GRADE框架集成

### 五个领域评估

工具实现了全面的GRADE方法学：

#### 1. 偏倚风险评估
- **方法学**: 使用研究水平ROB评估的基于权重的评价
- **阈值**: 可配置的比例和权重阈值
- **输出**: 严重/非常严重/不严重评级及详细推理

#### 2. 不一致性评价
- **统计指标**: I²统计量、置信区间重叠
- **网络特异性**: 考虑直接和间接证据
- **自适应阈值**: 基于研究背景的可定制化

#### 3. 间接性评估
- **人群**: 评估人群代表性
- **干预**: 评估干预相关性
- **结局**: 审查结局测量适当性

#### 4. 不精确性分析
- **样本量**: 计算网络证据的有效样本量
- **最优信息量**: 基于最小重要差异计算OIS
- **置信区间**: 评估效应估计的精确性

#### 5. 发表偏倚检测
- **网络几何**: 评估网络完整性
- **研究分布**: 评估证据分布模式
- **报告质量**: 审查选择性报告指标

### GRADE评级逻辑

工具实现标准化GRADE评级进程：

1. **起始点**: RCT的高质量证据
2. **降级**: 对每个领域关注应用降级
3. **最终评级**: 极低、低、中等或高质量证据

```
高 → 中等 → 低 → 极低
 ↓     ↓    ↓
-1   -1   -1    (每个领域关注)
```

## 评估工作流程

### 数据处理管道

1. **输入验证**
   - 验证文件结构和完整性
   - 检查数据格式一致性
   - 验证分析设置

2. **证据提取**
   - 解析网络荟萃分析结果
   - 提取研究水平特征
   - 编译比较特异性数据

3. **领域特异性评估**
   - 系统性应用GRADE标准
   - 生成基于证据的评级
   - 记录评估推理

4. **结果汇编**
   - 汇总领域评估
   - 计算最终确定性评级
   - 准备结构化输出

### 质量保证步骤

- **自动验证**: 内置一致性检查
- **透明推理**: 每个判断的详细解释
- **可重现结果**: 标准化评估标准
- **审计轨迹**: 评估过程的完整文档

## 交互式报告生成

### HTML报告功能

工具生成全面的交互式报告：

#### 实时重新计算
- **动态阈值**: 调整参数并查看即时结果
- **交互式表格**: 排序、筛选和探索评估数据
- **视觉指标**: 颜色编码的确定性评级和领域关注

#### 自包含设计
- **零依赖**: 无需外部资源的完整功能
- **便携格式**: 单个HTML文件便于共享
- **跨平台**: 与所有现代浏览器兼容

#### 报告组件

1. **执行摘要**
   - 整体评估概述
   - 关键发现和建议
   - 方法学摘要

2. **详细结果表**
   - 比较特异性评估
   - 逐领域评级
   - 支持证据和推理

3. **交互式控制**
   - 阈值调整滑块
   - 筛选和搜索功能
   - 导出功能

4. **方法学文档**
   - 评估标准解释
   - 参数设置记录
   - 质量保证信息

### 报告定制

```python
# 生成定制报告
evaluator.generate_interactive_report(
    output_path="custom_report.html",
    include_methodology=True,
    show_calculations=True,
    theme="professional"
)
```

## 高级功能

### 自定义评估规则

实现领域特异性评估逻辑：

```python
# 自定义ROB评估
def custom_rob_assessment(studies_data, weights_data):
    # 实现自定义逻辑
    return rating, reasoning

evaluator.set_custom_rob_function(custom_rob_assessment)
```

### 与外部工具集成

- **R netmeta**: 与netmeta包输出直接集成
- **RevMan**: 与Cochrane Review Manager数据兼容
- **STATA**: 支持STATA网络荟萃分析结果

### 验证和测试

- **参考标准**: 针对专家评估进行验证
- **可重现性**: 跨运行的一致结果
- **性能指标**: 速度和准确性基准

## 性能优化

### 大数据集处理

- **内存管理**: 大型网络的高效数据处理
- **并行处理**: 批量评估的多核利用
- **缓存**: 中间结果的智能缓存

### 速度优化技巧

1. **预处理数据**: 事先清理和验证输入数据
2. **批量操作**: 一起处理多个结局
3. **配置调优**: 为您的用例优化参数

## 故障排除

### 常见问题

#### 文件未找到错误
```
Error: Directory does not exist: /path/to/results
```
**解决方案**: 验证配置中的`base_dir`路径，确保所有必需文件都存在。

#### 缺少依赖
```
ModuleNotFoundError: No module named 'pandas'
```
**解决方案**: 使用`pip install -r requirements.txt`安装必需包

#### 配置错误
```
KeyError: 'high_risk_count_threshold'
```
**解决方案**: 检查`config.json`格式，确保包含所有必需参数。

### 数据格式问题

#### 不一致的文件结构
- 确保结局目录遵循预期的命名约定
- 验证所有必需的CSV文件都存在且格式正确
- 检查分析设置文件包含必要参数

#### ROB评估格式
- 偏倚风险评估应使用标准化类别："Low"、"High"、"Unclear"
- 确保研究名称在ROB数据和分析结果之间匹配
- 验证所有纳入研究都有ROB评估

### 性能问题

#### 处理缓慢
- 检查可用系统内存
- 减少大数据集的批量大小
- 验证输入数据质量和完整性

#### 内存错误
- 单独处理结局而不是批量处理
- 增加系统虚拟内存
- 优化数据预处理步骤

## 技术架构

### 核心组件

#### GradeEvaluator类
- **目的**: 主要评估引擎
- **职责**: 数据加载、领域评估、结果编译
- **关键方法**: `evaluate_grade()`、`evaluate_rob()`、`evaluate_inconsistency()`

#### 评估模块
- **ROB模块**: 基于权重分析的偏倚风险评价
- **不一致性模块**: 统计不一致性评估
- **不精确性模块**: 样本量和精确性分析
- **发表偏倚模块**: 网络完整性评价

#### 报告生成器
- **HTML引擎**: 交互式报告创建
- **模板系统**: 可定制报告布局
- **导出功能**: 多种输出格式支持

### 数据流架构

```
输入数据 → 验证 → 领域评估 → 结果编译 → 报告生成
     ↓       ↓        ↓         ↓          ↓
NMA结果 → 格式检查 → GRADE领域 → 最终评级 → 交互式HTML
```

### 算法实现

#### 基于权重的ROB评估
1. 从荟萃分析结果计算研究权重
2. 从ROB评估识别高风险研究
3. 计算高风险证据的加权比例
4. 应用可配置阈值进行评级确定

#### 网络不一致性分析
1. 从成对比较提取I²统计量
2. 评估置信区间重叠模式
3. 评估全局网络不一致性测量
4. 生成领域特异性不一致性评级

## 集成指南

### R netmeta集成

工具设计为与R netmeta包输出无缝协作：

#### 必需文件
- `outcome-nettable.csv`: 网络比较表
- `outcome-original_data.csv`: 原始研究数据
- `outcome-analysis_settings.csv`: 分析配置
- `outcome-netpairwise.csv`: 成对比较结果
- `outcome-meta_result_random.csv`: 随机效应结果

#### 文件格式要求
```r
# R代码生成兼容文件
library(netmeta)

# 运行网络荟萃分析
net_result <- netmeta(TE, seTE, treat1, treat2, studlab, data = your_data)

# 导出必需文件
write.csv(nettable(net_result), "outcome-nettable.csv")
write.csv(your_data, "outcome-original_data.csv")
# ... 其他导出
```

### 工作流程集成

#### 系统评价管道
1. **研究选择**: 完成筛选和选择过程
2. **数据提取**: 提取结局数据和研究特征
3. **ROB评估**: 进行偏倚风险评价
4. **网络荟萃分析**: 使用R netmeta进行统计分析
5. **GRADE评估**: 使用此工具进行证据确定性评价
6. **报告生成**: 创建最终系统评价报告

#### 质量保证集成
- **双重评估**: 支持独立评估者工作流程
- **共识建立**: 解决评估分歧的工具
- **审计文档**: 同行评议的完整评估轨迹

## 最佳实践

### 评估方法学

#### 评估前准备
1. **完成ROB评估**: 确保所有研究都有质量评估
2. **验证网络几何**: 检查断开的网络或稀疏数据
3. **定义MID值**: 建立临床重要差异阈值
4. **配置参数**: 为您的研究背景设置适当阈值

#### 评估期间
1. **审查自动判断**: 验证自动评估与临床专业知识一致
2. **记录理由**: 在适当时添加背景特异性推理
3. **考虑临床相关性**: 在临床背景下评估统计发现
4. **保持一致性**: 在比较中统一应用评估标准

#### 评估后审查
1. **验证结果**: 与临床专家交叉检查评估
2. **记录方法学**: 记录评估方法和参数选择
3. **准备同行评议**: 确保透明和可重现的评估过程

### 配置建议

#### 保守评估
```json
{
    "rob_params": {
        "high_risk_count_threshold": 0.3,
        "high_risk_weight_threshold": 30,
        "very_serious_weight_threshold": 60
    },
    "inconsistency_params": {
        "i2_threshold": 50,
        "i2_very_serious_threshold": 80
    }
}
```

#### 标准评估
```json
{
    "rob_params": {
        "high_risk_count_threshold": 0.5,
        "high_risk_weight_threshold": 50,
        "very_serious_weight_threshold": 80
    },
    "inconsistency_params": {
        "i2_threshold": 60,
        "i2_very_serious_threshold": 90
    }
}
```

### 质量保证

#### 验证步骤
1. **交叉验证**: 将结果与手动评估比较
2. **敏感性分析**: 测试不同参数配置
3. **专家审查**: 与领域专家验证评估
4. **可重现性测试**: 验证跨运行的一致结果

#### 文档标准
- **参数证明**: 记录阈值选择的理由
- **评估轨迹**: 维护评估过程的完整记录
- **版本控制**: 跟踪评估标准和结果的变化
- **同行评议准备**: 为外部审查组织文档

---

## 引用

在您的研究中使用此工具时，请引用：

> Lai H, Liu J, Ma N, et al. Development and Validation of SmartNMA: An Intelligent Agent for Interventional Systematic Reviews and Network Meta-Analysis.

## 支持和联系

如需技术支持、功能请求或合作机会，请联系兰州大学SmartEBM团队。

---

*本文档是SmartEBM系统评价和荟萃分析工具包的一部分，旨在提高证据综合过程的效率和可靠性。*