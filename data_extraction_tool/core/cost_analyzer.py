#!/usr/bin/env python3
"""
成本分析模块
Cost Analysis Module

追踪和分析LLM API调用成本
Track and analyze LLM API call costs
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class APICallRecord:
    """API调用记录"""
    timestamp: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    response_time: float
    file_name: str = ""
    operation_type: str = "extraction"


class CostAnalyzer:
    """成本分析器 / Cost Analyzer"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.call_records: List[APICallRecord] = []
        self.total_cost_usd = 0.0
        self.total_tokens = 0
        self.start_time = datetime.now()
        
        # 默认定价（每1K tokens的价格，USD）
        self.default_pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
            "deepseek-chat": {"input": 0.0001, "output": 0.0002},
            "glm-4": {"input": 0.0001, "output": 0.0001}
        }
        
        # USD to CNY汇率（默认值，实际应该从API获取）
        self.usd_to_cny_rate = 7.2
        
    def record_api_call(self, 
                       model: str,
                       prompt_tokens: int,
                       completion_tokens: int,
                       response_time: float,
                       file_name: str = "",
                       operation_type: str = "extraction") -> float:
        """记录API调用"""
        total_tokens = prompt_tokens + completion_tokens
        estimated_cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        
        record = APICallRecord(
            timestamp=datetime.now().isoformat(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=estimated_cost,
            response_time=response_time,
            file_name=file_name,
            operation_type=operation_type
        )
        
        self.call_records.append(record)
        self.total_cost_usd += estimated_cost
        self.total_tokens += total_tokens
        
        # 检查预算警告
        self.check_budget_warning()
        
        return estimated_cost
    
    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """计算成本"""
        model_key = self.normalize_model_name(model)
        
        if model_key in self.default_pricing:
            pricing = self.default_pricing[model_key]
            input_cost = (prompt_tokens / 1000) * pricing["input"]
            output_cost = (completion_tokens / 1000) * pricing["output"]
            return input_cost + output_cost
        else:
            # 如果模型不在定价表中，使用保守估算
            return ((prompt_tokens + completion_tokens) / 1000) * 0.002
    
    def normalize_model_name(self, model: str) -> str:
        """标准化模型名称"""
        model_lower = model.lower()
        
        # 处理常见的模型名称变体
        if "gpt-4o-mini" in model_lower:
            return "gpt-4o-mini"
        elif "gpt-4o" in model_lower:
            return "gpt-4o"
        elif "gpt-4-turbo" in model_lower:
            return "gpt-4-turbo"
        elif "gpt-4" in model_lower:
            return "gpt-4"
        elif "gpt-3.5" in model_lower:
            return "gpt-3.5-turbo"
        elif "claude-3-opus" in model_lower:
            return "claude-3-opus"
        elif "claude-3-sonnet" in model_lower:
            return "claude-3-sonnet"
        elif "claude-3-haiku" in model_lower:
            return "claude-3-haiku"
        elif "deepseek" in model_lower:
            return "deepseek-chat"
        elif "glm-4" in model_lower:
            return "glm-4"
        else:
            return model
    
    def check_budget_warning(self):
        """检查预算警告"""
        if not self.config.get("cost_control", {}).get("track_token_usage", True):
            return
            
        max_budget = self.config.get("cost_control", {}).get("max_budget_usd", 100.0)
        warning_threshold = self.config.get("cost_control", {}).get("warning_threshold_percent", 80)
        
        if max_budget > 0:
            usage_percent = (self.total_cost_usd / max_budget) * 100
            
            try:
                from i18n.i18n_manager import get_message
            except ImportError:
                def get_message(key, **kwargs):
                    fallback_messages = {
                        "budget_exceeded": "🚨 Budget exceeded warning! Current cost: ${current:.2f} / ${max_budget:.2f}",
                        "budget_warning": "⚠️ Budget warning! Current cost: ${current:.2f} / ${max_budget:.2f} ({percentage:.1f}%)"
                    }
                    message = fallback_messages.get(key, key)
                    return message.format(**kwargs) if kwargs and isinstance(message, str) else message
            
            if usage_percent >= 100:
                print(get_message("budget_exceeded", current=self.total_cost_usd, max_budget=max_budget))
            elif usage_percent >= warning_threshold:
                print(get_message("budget_warning", current=self.total_cost_usd, max_budget=max_budget, percentage=usage_percent))
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """获取成本摘要"""
        if not self.call_records:
            return {}
        
        # 按模型统计
        model_stats = {}
        for record in self.call_records:
            if record.model not in model_stats:
                model_stats[record.model] = {
                    "call_count": 0,
                    "total_tokens": 0,
                    "total_cost_usd": 0.0,
                    "avg_response_time": 0.0
                }
            
            stats = model_stats[record.model]
            stats["call_count"] += 1
            stats["total_tokens"] += record.total_tokens
            stats["total_cost_usd"] += record.estimated_cost_usd
            stats["avg_response_time"] = (stats["avg_response_time"] * (stats["call_count"] - 1) + record.response_time) / stats["call_count"]
        
        # 计算总体统计
        total_calls = len(self.call_records)
        avg_cost_per_call = self.total_cost_usd / total_calls if total_calls > 0 else 0
        avg_tokens_per_call = self.total_tokens / total_calls if total_calls > 0 else 0
        
        # 处理时间统计
        processing_time = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "summary": {
                "total_calls": total_calls,
                "total_tokens": self.total_tokens,
                "total_cost_usd": self.total_cost_usd,
                "total_cost_cny": self.total_cost_usd * self.usd_to_cny_rate,
                "avg_cost_per_call": avg_cost_per_call,
                "avg_tokens_per_call": avg_tokens_per_call,
                "processing_time_seconds": processing_time
            },
            "by_model": model_stats,
            "currency_rate": {
                "usd_to_cny": self.usd_to_cny_rate,
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def print_cost_summary(self):
        """打印成本摘要"""
        summary = self.get_cost_summary()
        
        if not summary:
            try:
                from i18n.i18n_manager import get_message
                print(get_message("no_cost_data"))
            except ImportError:
                print("📊 No cost data available")
            return
        
        try:
            from i18n.i18n_manager import get_message
        except ImportError:
            def get_message(key, **kwargs):
                fallback_messages = {
                    "cost_summary_title": "💰 Cost Analysis Summary",
                    "total_api_calls": "Total API Calls: {calls:,}",
                    "total_tokens": "Total Tokens: {tokens:,}",
                    "total_cost": "Total Cost: ${cost_usd:.2f} USD / ¥{cost_cny:.2f} CNY",
                    "avg_cost_per_call": "Average Cost per Call: ${cost:.4f} USD",
                    "avg_tokens_per_call": "Average Tokens per Call: {tokens:.0f}",
                    "processing_time_hours": "Processing Time: {hours:.1f} hours",
                    "processing_time_minutes": "Processing Time: {minutes:.1f} minutes",
                    "model_breakdown": "📊 By Model Breakdown:",
                    "model_calls": "    Calls: {count}",
                    "model_tokens": "    Tokens: {tokens:,}",
                    "model_cost": "    Cost: ${cost:.2f} USD",
                    "model_avg_response_time": "    Avg Response Time: {time:.2f}s"
                }
                message = fallback_messages.get(key, key)
                return message.format(**kwargs) if kwargs and isinstance(message, str) else message
        
        print("\n" + "=" * 60)
        print(get_message("cost_summary_title"))
        print("=" * 60)
        
        stats = summary["summary"]
        print(get_message("total_api_calls", calls=stats['total_calls']))
        print(get_message("total_tokens", tokens=stats['total_tokens']))
        print(get_message("total_cost", cost_usd=stats['total_cost_usd'], cost_cny=stats['total_cost_cny']))
        print(get_message("avg_cost_per_call", cost=stats['avg_cost_per_call']))
        print(get_message("avg_tokens_per_call", tokens=stats['avg_tokens_per_call']))
        
        processing_hours = stats['processing_time_seconds'] / 3600
        if processing_hours >= 1:
            print(get_message("processing_time_hours", hours=processing_hours))
        else:
            processing_minutes = stats['processing_time_seconds'] / 60
            print(get_message("processing_time_minutes", minutes=processing_minutes))
        
        # 按模型详细统计
        if summary["by_model"]:
            breakdown_msg = get_message("model_breakdown")
            if breakdown_msg:
                print("\n" + str(breakdown_msg))
            for model, stats in summary["by_model"].items():
                print(f"  {model}:")
                print(get_message("model_calls", count=stats['call_count']))
                print(get_message("model_tokens", tokens=stats['total_tokens']))
                print(get_message("model_cost", cost=stats['total_cost_usd']))
                print(get_message("model_avg_response_time", time=stats['avg_response_time']))
        
        print("=" * 60)
    
    def save_detailed_report(self, output_path: str):
        """保存详细报告"""
        try:
            report_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "tool_version": "SmartEBM Data Extraction Tool v2.0",
                    "analysis_period": {
                        "start": self.start_time.isoformat(),
                        "end": datetime.now().isoformat()
                    }
                },
                "cost_summary": self.get_cost_summary(),
                "detailed_records": [asdict(record) for record in self.call_records]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"📄 Detailed cost report saved to: {output_path}")
            
        except Exception as e:
            print(f"Error saving cost report: {e}")
    
    def estimate_remaining_cost(self, remaining_documents: int, avg_tokens_per_doc: int = 5000) -> Dict[str, float]:
        """估算剩余成本"""
        if not self.call_records:
            # 如果没有历史记录，使用默认估算
            model = "gpt-4o-mini"  # 使用较经济的模型作为基准
            estimated_cost = self.calculate_cost(model, avg_tokens_per_doc, avg_tokens_per_doc // 10)
        else:
            # 基于历史数据估算
            avg_cost_per_call = self.total_cost_usd / len(self.call_records)
            estimated_cost = avg_cost_per_call
        
        total_estimated_cost = remaining_documents * estimated_cost
        
        return {
            "estimated_cost_per_document": estimated_cost,
            "total_estimated_cost_usd": total_estimated_cost,
            "total_estimated_cost_cny": total_estimated_cost * self.usd_to_cny_rate,
            "remaining_documents": remaining_documents
        }