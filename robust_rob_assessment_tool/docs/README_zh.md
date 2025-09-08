# SmartEBM 偏倚风险评估工具 v2.0

### 具有双语界面的高级并行处理偏倚风险评估工具

本项目由兰州大学**SmartEBM（智能循证医学）团队**开发与维护。我们的团队专注于设计**智能体**，将复杂的类人推理工作流嵌入证据合成过程。

本代码库包含**SmartEBM 偏倚风险评估工具 v2.0**，具有高级并行处理能力、双语界面支持（中英文）、全面的进度监控和智能成本跟踪功能，用于系统综述中的自动化偏倚风险评估。

## 1. 项目背景

系统综述和网络meta分析是循证医学的基石。然而，其产出过程资源密集，尤其是偏倚风险（RoB）评估阶段——评估纳入研究的方法学质量——特别耗费人力且容易产生主观性。

SmartEBM偏倚风险评估工具通过与ROBUST-RCT框架的先进集成来解决这些挑战，在SmartNMA研究验证中对3,276项评估实现了97.5%的高置信度准确率。该工具采用创新的两步分解方法，将复杂的偏倚评估分解为可管理的组件，结合基于置信度的分类，自动识别哪些评估可以信任，哪些需要人工审查。

### ROBUST-RCT框架集成

ROBUST-RCT（使用结构化思维的偏倚风险评估-随机对照试验）框架提供了系统性的偏倚评估方法，我们的工具通过以下方式实现：

**两步分解过程：**
1. **领域分析**：每个偏倚领域（随机化、分配隐藏、盲法等）使用特定领域的提示和标准独立评估
2. **综合整合**：将单个领域评估综合为整体研究级别的偏倚评估，并进行置信度评分

**基于置信度的分类：**
- **高置信度（97.5%准确率）**：明确证据且LLM在各领域达成一致
- **中等置信度**：需要针对性审查的轻微差异
- **低置信度**：需要人工评估的重大冲突或信息不足

这种方法使研究人员能够将有限的时间集中在真正不确定的案例上，同时信任明确评估的自动化结果。

### SmartEBM智能体生态系统

虽然本代码库专注于偏倚风险评估工具，但它是我们团队正在开发的更大智能体生态系统的一部分，还包括：

- **标题和摘要筛选智能体**：自动化初始文献筛选
- **全文筛选智能体**：筛选全文文章以确定最终纳入
- **数据提取智能体**：从纳入研究中提取PICOS数据、研究特征和结果
- **数据分析智能体**：执行网络meta分析的统计计算
- **证据确定性（CoE）评估智能体**：协助使用GRADE方法对证据确定性进行评级

这种模块化设计为证据合成提供了灵活且强大的端到端解决方案。

## 2. 高级功能与特性

### 2.1 并行处理架构
- **智能资源检测**：自动检测系统CPU、内存和磁盘容量
- **最优工作进程分配**：基于系统资源推荐最优并行工作进程数
- **批处理**：将文档分布到多个工作进程以实现最大效率
- **容错能力**：单个文档失败不会停止整个评估过程
- **资源监控**：基于系统负载和性能进行动态调整

### 2.2 双语界面支持
- **交互式语言选择**：启动时可选择中文或英文
- **全面翻译**：所有用户消息、进度更新和错误消息均支持双语
- **文化适应**：界面设计适应中西方用户偏好
- **运行时语言切换**：无需重启应用程序即可更改语言

### 2.3 高级进度监控
- **实时进度显示**：实时更新完成百分比和预计完成时间
- **批次状态跟踪**：监控单个批次进度和性能指标
- **性能分析**：处理速度、每文档平均时间、资源利用率
- **成本跟踪**：实时LLM使用成本监控，支持多币种
- **交互式仪表板**：包含详细统计信息的综合进度可视化

### 2.4 检查点与恢复系统
- **自动状态保存**：处理过程中定期创建检查点
- **智能恢复**：中断后从最后检查点继续
- **状态验证**：自动检测和恢复损坏的检查点
- **进度保护**：永不因系统故障或中断而丢失工作

### 2.5 ROBUST-RCT评估工作流
- **两步分解**：将偏倚评估系统性分解为特定领域评估，然后进行综合整合
- **多LLM验证**：双LLM方法结合交叉验证，增强可靠性和置信度评分
- **领域特定提示**：为每个ROBUST-RCT偏倚领域（随机化、分配隐藏、盲法、不完整结果数据、选择性报告、其他偏倚）量身定制的优化提示
- **基于置信度的分类**：基于LLM一致性和证据清晰度自动分类为高（97.5%准确率）、中、低置信度水平
- **质量保证集成**：内置识别需要人工审查的评估与适合自动化处理的评估
- **综合报告**：详细的Excel和HTML报告，带有置信度编码的视觉突出显示和领域特定推理

### 2.6 成本管理与优化
- **多模型成本跟踪**：分别跟踪不同LLM模型的成本
- **货币支持**：支持美元、欧元、英镑、人民币和日元的成本报告
- **使用分析**：详细的令牌消耗分析和优化建议
- **预算警报**：可配置的成本阈值警告和提醒
- **成本优化**：智能推荐以降低API成本

## 3. 安装与设置

### 3.1 系统要求

**最低要求：**
- Python 3.8+（推荐Python 3.10+）
- 4GB RAM（推荐8GB+用于并行处理）
- 2GB可用磁盘空间
- 互联网连接用于LLM API访问

**最佳性能推荐：**
- Python 3.10+
- 16GB+ RAM用于大型文档集
- 多核CPU（推荐4+核心）
- SSD存储以获得更快的I/O操作

**支持的操作系统：**
- Windows 10/11
- macOS 10.15+
- Linux（Ubuntu 18.04+，CentOS 7+）

### 3.2 安装步骤

1. **克隆代码库**
   ```bash
   git clone https://github.com/enenlhh/SmartNMA-AI-assisted-tools.git
   cd SmartNMA-AI-assisted-tools/robust_rob_assessment_tool
   ```

2. **创建虚拟环境**（推荐）
   ```bash
   # 使用venv
   python -m venv rob_env
   
   # Windows激活
   rob_env\Scripts\activate
   
   # macOS/Linux激活
   source rob_env/bin/activate
   ```

3. **安装依赖项**
   ```bash
   pip install -r requirements.txt
   ```

4. **验证安装**
   ```bash
   python main.py --version
   ```

### 3.3 快速开始指南

1. **交互模式**（推荐初学者）
   ```bash
   python main.py
   ```
   - 选择您的首选语言（中文/英文）
   - 按照交互菜单配置和开始评估

2. **命令行模式**（适用于高级用户）
   ```bash
   # 开始新评估
   python main.py start -c config/config.json
   
   # 恢复中断的评估
   python main.py resume -s checkpoint_file.json
   
   # 监控运行中的评估
   python main.py monitor
   ```

## 4. ROBUST-RCT框架和评估工作流

### 4.1 ROBUST-RCT集成概述

SmartEBM偏倚风险评估工具通过复杂的两步分解过程实现ROBUST-RCT框架，确保系统性和可靠的偏倚评估：

#### **步骤1：领域特定评估**
每个偏倚领域使用专门的提示和标准独立评估：

1. **随机序列生成**：评估随机化方法的充分性
2. **分配隐藏**：评估分配序列隐藏
3. **参与者和研究人员盲法**：评估实施偏倚风险
4. **结果评估盲法**：评估检测偏倚风险
5. **不完整结果数据**：评估失访偏倚处理
6. **选择性报告**：评估报告偏倚风险
7. **其他偏倚**：评估额外偏倚来源

#### **步骤2：综合和置信度评分**
单个领域评估通过置信度分类进行综合：

- **高置信度（97.5%准确率）**：明确证据、一致的LLM一致性、确定的偏倚判定
- **中等置信度**：LLM之间的轻微差异、总体明确的证据但有轻微不确定性
- **低置信度**：LLM之间的重大冲突、信息不足或需要人工审查的模糊证据

### 4.2 评估工作流程

#### **评估前阶段**
1. **文档处理**：PDF文本提取，扫描文档使用OCR备用方案
2. **内容验证**：验证研究类型和方法学信息可用性
3. **批次组织**：智能分组以优化并行处理

#### **评估执行**
1. **领域分析**：使用专门提示对每个ROBUST-RCT领域进行顺序评估
2. **交叉验证**：多LLM评估与一致性分析
3. **置信度评分**：基于证据清晰度和LLM共识的自动分类
4. **质量标记**：识别需要人工审查的评估

#### **评估后处理**
1. **结果综合**：将领域特定评估整合为整体偏倚评估
2. **报告生成**：创建带有置信度指标的详细Excel和HTML报告
3. **质量保证**：标记低置信度评估以供人工审查

### 4.3 偏倚评估标准配置

工具允许自定义偏倚评估标准，同时保持ROBUST-RCT框架合规性：

```json
{
  "rob_framework": {
    "type": "robust_rct",
    "domains": {
      "random_sequence_generation": {
        "weight": 1.0,
        "confidence_threshold": 0.8,
        "require_explicit_method": true
      },
      "allocation_concealment": {
        "weight": 1.0,
        "confidence_threshold": 0.8,
        "require_concealment_method": true
      },
      "blinding_participants": {
        "weight": 0.9,
        "confidence_threshold": 0.7,
        "allow_open_label_justification": true
      }
    }
  }
}
```

## 5. 配置指南

### 5.1 配置文件设置

工具使用综合的JSON配置文件。通过复制模板创建您的配置：

```bash
cp config/config_template.json config/config.json
```

### 4.2 基本配置部分

#### **文件路径配置**
```json
{
  "paths": {
    "input_folder": "input/documents",
    "output_folder": "output/results", 
    "checkpoint_file": "checkpoints/assessment.json",
    "temp_folder": "temp_parallel",
    "llm_pricing_config": "config/llm_pricing.json"
  }
}
```

#### **并行处理配置**
```json
{
  "parallel": {
    "enabled": true,
    "max_workers": 4,
    "max_documents_per_batch": 50,
    "checkpoint_interval": 10,
    "retry_attempts": 3,
    "timeout_seconds": 300,
    "memory_limit_gb": 8.0,
    "auto_detect_workers": true
  }
}
```

#### **LLM模型配置**
```json
{
  "llm_models": [
    {
      "name": "主要模型",
      "api_key": "your_openai_api_key",
      "base_url": "https://api.openai.com/v1",
      "model_name": "gpt-4",
      "max_retries": 3,
      "timeout": 60
    },
    {
      "name": "次要模型", 
      "api_key": "your_anthropic_api_key",
      "base_url": "https://api.anthropic.com/v1",
      "model_name": "claude-3-sonnet",
      "max_retries": 3,
      "timeout": 60
    }
  ]
}
```

#### **成本跟踪配置**
```json
{
  "cost_tracking": {
    "enabled": true,
    "currency": "CNY",
    "track_by_model": true,
    "generate_reports": true,
    "cost_alerts": true,
    "max_cost_threshold": 500.0
  }
}
```

### 4.3 配置验证

工具会自动验证您的配置并提供有用的错误消息：

```bash
# 验证配置
python main.py start -c config/config.json --validate-only
```

**常见配置问题：**
- 缺少API密钥
- 无效的文件路径
- 错误的模型名称
- 资源限制超出系统容量

## 5. 使用指南

### 5.1 交互模式（推荐）

以交互模式启动工具进行引导操作：

```bash
python main.py
```

**交互功能：**
1. **语言选择**：选择中文或英文界面
2. **操作菜单**：从带有描述的可用操作中选择
3. **系统信息**：查看系统资源和建议
4. **配置指导**：逐步配置协助
5. **进度监控**：实时进度更新和统计

### 5.2 命令行操作

#### **开始新评估**
```bash
# 使用配置文件基本启动
python main.py start -c config/config.json

# 使用自定义参数启动
python main.py start -c config/config.json -w 8 --batch-size 25

# 使用特定输入/输出目录启动
python main.py start -c config/config.json -i input/docs -o output/results
```

#### **恢复中断的评估**
```bash
# 从检查点恢复
python main.py resume -s checkpoint_file.json

# 使用不同工作进程数恢复
python main.py resume -s checkpoint_file.json -w 4
```

#### **监控进度**
```bash
# 自动检测监控
python main.py monitor

# 监控特定评估
python main.py monitor -s state_file.json -r 10
```

#### **清理操作**
```bash
# 清理临时文件
python main.py cleanup

# 强制清理
python main.py cleanup --force

# 保留结果，仅清理临时文件
python main.py cleanup --keep-results
```

#### **合并结果**
```bash
# 合并批次结果
python main.py merge -i results/batches -o final_results.xlsx

# 使用特定格式合并
python main.py merge -i results/batches -o results.json --format json
```

### 5.3 评估工作流

1. **准备阶段**
   - 系统资源检测
   - 配置验证
   - 输入文档发现
   - 批次创建和分发

2. **处理阶段**
   - 并行文档处理
   - 偏倚风险领域评估
   - 实时进度监控
   - 自动检查点创建

3. **完成阶段**
   - 结果整合
   - 报告生成（Excel/HTML）
   - 成本分析和报告
   - 临时文件清理

## 6. 输出与结果

### 6.1 生成的文件

**Excel报告（`rob_results.xlsx`）**
- 综合偏倚风险评估结果
- 颜色编码的置信度水平
- 每个领域的详细推理
- 摘要统计和指标
- 按模型分类的成本明细

**HTML可视化（`rob_visualization.html`）**
- 交互式交通灯图
- 按置信度水平过滤的结果
- 可导出为PDF格式
- 批次比较视图

**成本报告（`cost_analysis.xlsx`）**
- 详细的令牌使用统计
- 多币种成本计算
- 模型特定成本明细
- 优化建议

**检查点文件（`*.checkpoint.json`）**
- 用于恢复的评估状态
- 进度跟踪信息
- 配置快照
- 错误日志和恢复数据

### 6.2 结果解释

**置信度水平：**
- 🟢 **高置信度**：两个LLM在评估上达成一致
- 🟡 **中等置信度**：LLM之间存在轻微差异
- 🔴 **低置信度**：需要人工审查的重大冲突
- ⚪ **不确定**：信息不足无法评估

**质量保证建议：**
1. **强制审查**：所有低置信度和不确定的评估
2. **抽查**：高置信度结果的随机样本（10-20%）
3. **领域特定审查**：关注经常冲突的领域
4. **成本监控**：定期审查API使用和成本

## 7. 最佳实践与建议

### 7.1 评估前验证

**配置测试：**
```bash
# 使用小样本测试配置
python main.py start -c config/config.json --start-index 0 --batch-size 5
```

**提示验证：**
1. 审查配置中生成的提示
2. 在5-10个代表性文档上测试
3. 手动验证评估准确性
4. 根据需要调整配置

### 7.2 性能优化

**系统资源管理：**
- 使用自动检测获得最优工作进程数
- 处理过程中监控内存使用
- 根据文档复杂性调整批次大小
- 为长时间评估启用检查点间隔

**成本优化：**
- 使用成本跟踪和警报
- 根据准确性与成本考虑模型选择
- 对大型文档实施文本长度限制
- 定期审查定价配置

### 7.3 质量控制

**评估验证：**
- 始终审查低置信度结果
- 实施评估者间信度检查
- 记录评估标准和决策
- 维护人工覆盖的审计跟踪

**错误处理：**
- 监控错误日志以发现系统性问题
- 为瞬时故障实施重试逻辑
- 处理前验证文档格式
- 定期备份结果和检查点

## 8. 故障排除

### 8.1 常见问题

**安装问题：**
```bash
# Python版本问题
python --version  # 应该是3.8+

# 依赖冲突
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# 权限错误（Linux/macOS）
sudo chown -R $USER:$USER /path/to/tool
```

**配置错误：**
- **无效API密钥**：验证密钥是否有效且有足够配额
- **路径问题**：使用绝对路径或确保相对路径正确
- **模型可用性**：检查指定模型是否可访问
- **资源限制**：如果系统资源不足，减少工作进程数

**运行时问题：**
```bash
# 内存错误
# 在配置中减少并行工作进程或批次大小

# 网络超时
# 在LLM配置中增加超时值

# 磁盘空间问题
# 清理临时文件：python main.py cleanup
```

### 8.2 性能问题

**处理缓慢：**
- 增加并行工作进程（在系统限制内）
- 减少文档文本长度限制
- 使用更快的LLM模型
- 优化批次大小

**高成本：**
- 启用成本跟踪和警报
- 对初始评估使用更小/更便宜的模型
- 实施文本预处理以减少令牌使用
- 审查和优化提示

**内存问题：**
- 减少并行工作进程
- 减少批次大小
- 在配置中启用内存限制
- 以更小的块处理文档

### 8.3 偏倚评估特定问题

**低置信度评估：**
- **研究信息不足**：确保PDF包含完整的方法学部分
- **报告模糊**：对方法学描述不清楚的研究考虑人工审查
- **LLM分歧**：审查领域特定评估以识别冲突来源
- **语言障碍**：验证非英语研究的文本提取质量

**领域特定挑战：**
```bash
# 随机化评估问题
# 检查明确的随机化方法描述
# 验证序列生成细节是否存在

# 分配隐藏问题  
# 寻找隐藏方法描述
# 确保分配时机信息可用

# 盲法评估困难
# 验证参与者和结果评估者盲法描述
# 检查开放标签研究的合理性说明
```

**质量保证建议：**
- **强制审查**：所有低置信度评估（通常占研究的10-15%）
- **抽查**：高置信度结果的随机样本（推荐10-20%）
- **领域重点**：对经常冲突的领域给予额外关注（通常是盲法和分配隐藏）
- **评估者间信度**：定期与人工评估进行验证

**评估准确性优化：**
```json
{
  "quality_control": {
    "confidence_thresholds": {
      "high_confidence_minimum": 0.85,
      "manual_review_maximum": 0.60
    },
    "domain_weights": {
      "randomization": 1.0,
      "allocation_concealment": 1.0,
      "blinding": 0.8
    }
  }
}
```

### 8.4 获取帮助

**文档：**
- 查看`docs/`目录获取详细指南
- 审查配置模板注释
- 查阅故障排除部分
- ROBUST-RCT框架文档

**支持渠道：**
- GitHub Issues：报告错误和功能请求
- 邮件支持：contact@smartebm.org
- 社区论坛：[SmartEBM社区](https://community.smartebm.org)
- ROBUST-RCT框架支持：[Cochrane方法学](https://methods.cochrane.org)

**调试信息：**
```bash
# 启用包含偏倚评估详情的详细日志记录
python main.py start -c config.json --verbose --log-file debug.log --include-prompts

# 验证偏倚评估配置
python main.py start -c config.json --validate-rob-config

# 在样本文档上测试评估
python main.py start -c config.json --test-mode --sample-size 5
```

## 9. 项目结构

```
robust_rob_assessment_tool/
├── main.py                     # 带CLI界面的主入口点
├── requirements.txt            # Python依赖项
├── config/
│   ├── config_template.json   # 配置模板
│   ├── config.json            # 用户配置（从模板创建）
│   └── llm_pricing.json       # LLM定价参考
├── core/                      # 核心系统模块
│   ├── parallel_controller.py # 并行处理管理
│   ├── progress_monitor.py    # 实时进度监控
│   ├── result_merger.py       # 结果整合
│   ├── system_detector.py     # 系统资源检测
│   ├── state_manager.py       # 检查点和状态管理
│   └── resume_manager.py      # 评估恢复逻辑
├── src/                       # 处理引擎
│   ├── rob_evaluator.py       # 偏倚风险评估逻辑
│   ├── document_processor.py  # 文档文本提取
│   ├── cost_analyzer.py       # 成本跟踪和分析
│   ├── visualizer.py          # HTML报告生成
│   ├── config_manager.py      # 配置管理
│   └── data_models.py         # 数据结构
├── i18n/                      # 国际化
│   ├── i18n_manager.py        # 语言管理
│   └── i18n_config.json       # 双语消息
├── docs/                      # 文档
│   ├── README.md              # 英文文档
│   ├── README_zh.md           # 中文文档
│   └── checkpoint_resume.md   # 检查点系统指南
├── examples/                  # 使用示例
│   └── checkpoint_resume_example.py
├── scripts/                   # 实用脚本
│   └── resume_cli.py          # 恢复命令行界面
├── input/                     # 输入文档目录
├── output/                    # 结果和报告
└── temp_parallel/             # 临时处理文件
```

## 10. 高级功能

### 10.1 检查点系统
- **自动检查点**：每N个文档保存进度（可配置）
- **智能恢复**：检测已完成的工作并从中断点继续
- **状态验证**：验证检查点完整性并处理损坏
- **多重检查点**：维护滚动检查点以获得最大安全性

### 10.2 成本管理
- **实时跟踪**：评估进行时监控成本
- **多币种支持**：以美元、欧元、英镑、人民币、日元查看成本
- **预算警报**：可配置的成本阈值和警告
- **优化建议**：AI驱动的成本降低建议

### 10.3 质量保证
- **置信度评分**：自动评估结果可靠性
- **冲突检测**：识别LLM模型间的分歧
- **错误隔离**：个别失败不影响批处理
- **审计跟踪**：所有评估决策的完整日志记录

## 11. API参考

### 11.1 命令行界面

```bash
# 主要操作
python main.py [操作] [选项]

# 可用操作：
start     # 开始新评估
resume    # 从检查点恢复  
monitor   # 监控进度
cleanup   # 清理临时文件
merge     # 合并批次结果

# 全局选项：
-l, --language {en,zh}    # 界面语言
-v, --verbose             # 详细输出
-q, --quiet              # 抑制输出
--log-file FILE          # 记录到文件
```

### 11.2 配置架构

**必需字段：**
- `paths.input_folder`：输入文档目录
- `paths.output_folder`：输出结果目录
- `llm_models`：至少一个LLM配置

**可选字段：**
- `parallel.enabled`：启用并行处理（默认：true）
- `cost_tracking.enabled`：启用成本跟踪（默认：true）
- `rob_framework.type`：偏倚风险框架类型（默认："rob2"）

## 12. 许可证与引用

### 12.1 许可证
本项目采用MIT许可证。详见`LICENSE`文件。

### 12.2 引用
如果您在研究中使用此工具，请引用：

```bibtex
@software{smartebm_rob_tool_2024,
  title={SmartEBM ROB Assessment Tool v2.0},
  author={Lai, Haoran and Liu, Jing and Ma, Ning and SmartEBM Group at Lanzhou University},
  year={2024},
  url={https://github.com/enenlhh/SmartNMA-AI-assisted-tools},
  version={2.0}
}
```

**相关出版物：**
> Lai H, Liu J, Ma N, et al. Development and Validation of SmartNMA: An Intelligent Agent for Interventional Systematic Reviews and Network Meta-Analysis.

### 12.3 致谢
- 兰州大学SmartEBM团队
- 贡献者和测试用户
- 开源社区提供的依赖项和工具

---

**联系信息：**
- 邮箱：enenlhh@outlook.com
- GitHub：https://github.com/enenlhh/SmartNMA-AI-assisted-tools
- 团队：SmartEBM Group at Lanzhou University