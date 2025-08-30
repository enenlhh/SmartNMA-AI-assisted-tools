# SmartEBM Data Extraction Tool - Usage Examples

## Basic Usage / 基本用法

### 1. Interactive Mode / 交互模式
```bash
# Start with language selection
python3 main.py

# Select your preferred language:
# 1. English
# 2. 中文

# Then choose operation:
# 1. Start new data extraction task
# 2. Resume interrupted task
# 3. Monitor existing task progress
# 4. Merge existing results only
# 5. Clean temporary files
# 6. Exit
```

### 2. Command Line Mode / 命令行模式
```bash
# Start new task with default config
python3 main.py

# Use custom config file
python3 main.py --config examples/config_example.json

# Resume interrupted task
python3 main.py --resume

# Monitor existing task
python3 main.py --monitor extraction_state_20241226_143022.json

# Merge results only
python3 main.py --merge-only extraction_state_20241226_143022.json

# Clean temporary files
python3 main.py --cleanup
```

### 3. Language Selection / 语言选择
```bash
# Chinese interface
python3 main.py --lang zh

# English interface  
python3 main.py --lang en

# Interactive selection (default)
python3 main.py --lang auto
```

## Configuration Examples / 配置示例

### 1. Basic Configuration / 基本配置
```json
{
  "paths": {
    "input_folder": "input",
    "output_folder": "output"
  },
  "parallel_settings": {
    "parallel_workers": 2
  },
  "llm_configs": {
    "primary": {
      "api_key": "your_api_key",
      "model": "gpt-4o-mini"
    }
  }
}
```

### 2. High Performance Configuration / 高性能配置
```json
{
  "parallel_settings": {
    "parallel_workers": 6,
    "auto_distribute": true,
    "cleanup_temp_files": true
  },
  "resource_management": {
    "api_calls_per_minute_limit": 200,
    "memory_limit_mb": 4096
  }
}
```

### 3. Budget-Conscious Configuration / 预算控制配置
```json
{
  "cost_control": {
    "max_budget_usd": 50.0,
    "warning_threshold_percent": 70,
    "track_token_usage": true
  },
  "llm_configs": {
    "primary": {
      "model": "gpt-4o-mini"
    }
  }
}
```

## Workflow Examples / 工作流程示例

### 1. Daily Research Workflow / 日常研究工作流程
```bash
# Step 1: Prepare documents in input folder
# 步骤1: 在input文件夹中准备文档

# Step 2: Start extraction with interactive interface
# 步骤2: 使用交互界面开始提取
python3 main.py

# Step 3: Monitor progress in real-time
# 步骤3: 实时监控进度

# Step 4: Review results in output folder
# 步骤4: 在output文件夹中查看结果
```

### 2. Large-Scale Processing / 大规模处理
```bash
# Step 1: Configure for high performance
# 步骤1: 配置高性能设置
# Edit config.json: set parallel_workers to 6-8

# Step 2: Start processing
# 步骤2: 开始处理
python3 main.py --config config/high_performance_config.json

# Step 3: Monitor in separate terminal
# 步骤3: 在单独终端中监控
python3 main.py --monitor extraction_state_*.json

# Step 4: If interrupted, resume
# 步骤4: 如果中断，恢复处理
python3 main.py --resume
```

### 3. Error Recovery Workflow / 错误恢复工作流程
```bash
# If extraction fails or is interrupted:
# 如果提取失败或中断:

# Option 1: Resume from last checkpoint
# 选项1: 从最后检查点恢复
python3 main.py --resume

# Option 2: Merge existing partial results
# 选项2: 合并现有部分结果
python3 main.py --merge-only extraction_state_*.json

# Option 3: Clean up and restart
# 选项3: 清理并重新开始
python3 main.py --cleanup
python3 main.py
```

## Performance Optimization / 性能优化

### 1. System Resource Optimization / 系统资源优化
```bash
# Check system resources before starting
# 启动前检查系统资源
python3 main.py

# The system will show warnings like:
# 系统会显示类似警告:
# ⚠️  Resource Warning:
#    - Requested workers (5) exceed safe CPU cores (3)
# 💡 Suggestion:
#    - Recommend setting to 3 workers
```

### 2. API Usage Optimization / API使用优化
```json
{
  "resource_management": {
    "api_calls_per_minute_limit": 100,
    "delay_between_workers": 2
  },
  "llm_configs": {
    "primary": {
      "timeout": 300,
      "max_retries": 5
    }
  }
}
```

### 3. Cost Optimization / 成本优化
```json
{
  "cost_control": {
    "max_budget_usd": 100.0,
    "warning_threshold_percent": 80
  },
  "llm_configs": {
    "primary": {
      "model": "gpt-4o-mini"  // Most cost-effective
    }
  }
}
```

## Troubleshooting Examples / 故障排除示例

### 1. Memory Issues / 内存问题
```bash
# If you see memory warnings:
# 如果看到内存警告:
# Solution: Reduce parallel workers
# 解决方案: 减少并行工作器数量

# Edit config.json:
{
  "parallel_settings": {
    "parallel_workers": 2  // Reduce from 4 to 2
  }
}
```

### 2. API Rate Limits / API频率限制
```bash
# If you see rate limit errors:
# 如果看到频率限制错误:
# Solution: Adjust API settings
# 解决方案: 调整API设置

# Edit config.json:
{
  "resource_management": {
    "api_calls_per_minute_limit": 50,  // Reduce from 100
    "delay_between_workers": 5         // Increase delay
  }
}
```

### 3. Configuration Errors / 配置错误
```bash
# If you see configuration errors:
# 如果看到配置错误:

# Check API key
# 检查API密钥
# Make sure api_key is set in llm_configs

# Check file paths
# 检查文件路径
# Make sure input_folder exists and contains documents

# Validate JSON syntax
# 验证JSON语法
# Use online JSON validator to check config.json
```