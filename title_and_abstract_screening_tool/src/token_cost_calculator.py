#!/usr/bin/env python3
"""
Token Cost Calculator
Calculate token consumption costs for different LLM models

Author: SmartEBM Team
Version: 1.0
"""

import json
import os
from typing import Dict, List, Tuple, Any
from datetime import datetime

class TokenCostCalculator:
    """Token Cost Calculator"""
    
    def __init__(self, pricing_config_path: str = "llm_pricing.json"):
        """
        Initialize cost calculator
        
        Args:
            pricing_config_path: Pricing configuration file path
        """
        self.pricing_config_path = pricing_config_path
        self.pricing_data = self._load_pricing_config()
        self.exchange_rate = self.pricing_data.get("_exchange_rate_usd_to_cny", 7.25)
    
    def _load_pricing_config(self) -> Dict[str, Any]:
        """Load pricing configuration"""
        try:
            with open(self.pricing_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Pricing config file {self.pricing_config_path} not found, using default pricing")
            return self._get_default_pricing()
        except Exception as e:
            print(f"Error loading pricing config: {e}, using default pricing")
            return self._get_default_pricing()
    
    def _get_default_pricing(self) -> Dict[str, Any]:
        """Get default pricing configuration"""
        return {
            "_exchange_rate_usd_to_cny": 7.25,
            "models": {},
            "default_fallback": {
                "input_price_per_1m": 5.0,
                "output_price_per_1m": 15.0,
                "currency": "USD"
            },
            "currency_symbols": {
                "USD": "$",
                "CNY": "¥"
            }
        }
    
    def get_model_pricing(self, model_name: str) -> Dict[str, float]:
        """
        Get pricing information for specified model
        
        Args:
            model_name: Model name
            
        Returns:
            Dictionary containing pricing information
        """
        models = self.pricing_data.get("models", {})
        
        # Direct match
        if model_name in models:
            return models[model_name]
        
        # Fuzzy match (handle version differences)
        model_lower = model_name.lower()
        for key, pricing in models.items():
            if key.lower() in model_lower or model_lower in key.lower():
                return pricing
        
        # Use default pricing
        print(f"Warning: No pricing found for model '{model_name}', using default pricing")
        return self.pricing_data.get("default_fallback", {
            "input_price_per_1m": 5.0,
            "output_price_per_1m": 15.0,
            "currency": "USD"
        })
    
    def calculate_cost(self, 
                      prompt_tokens: int, 
                      completion_tokens: int, 
                      model_name: str, 
                      currency: str = "USD") -> Dict[str, Any]:
        """
        Calculate cost for specified token count
        
        Args:
            prompt_tokens: Input token count
            completion_tokens: Output token count
            model_name: Model name
            currency: Target currency ("USD" or "CNY")
            
        Returns:
            Dictionary containing cost information
        """
        pricing = self.get_model_pricing(model_name)
        
        # Calculate USD cost
        input_cost_usd = (prompt_tokens / 1_000_000) * pricing.get("input_price_per_1m", 5.0)
        output_cost_usd = (completion_tokens / 1_000_000) * pricing.get("output_price_per_1m", 15.0)
        total_cost_usd = input_cost_usd + output_cost_usd
        
        # Convert currency
        if currency.upper() == "CNY":
            input_cost = input_cost_usd * self.exchange_rate
            output_cost = output_cost_usd * self.exchange_rate
            total_cost = total_cost_usd * self.exchange_rate
        else:
            input_cost = input_cost_usd
            output_cost = output_cost_usd
            total_cost = total_cost_usd
        
        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "currency": currency.upper(),
            "model": model_name,
            "pricing_info": pricing
        }
    
    def calculate_tokens_log_costs(self, 
                                  tokens_log: List[Dict[str, Any]], 
                                  currency: str = "USD") -> Dict[str, Any]:
        """
        Calculate total cost from tokens log
        
        Args:
            tokens_log: List of token usage records
            currency: Target currency
            
        Returns:
            Detailed cost analysis results
        """
        if not tokens_log:
            return {
                "total_cost": 0.0,
                "currency": currency.upper(),
                "by_model": {},
                "by_llm": {},
                "summary": {
                    "total_tokens": 0,
                    "total_prompt_tokens": 0,
                    "total_completion_tokens": 0,
                    "total_calls": 0
                }
            }
        
        total_cost = 0.0
        by_model = {}
        by_llm = {}
        
        total_tokens = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_calls = len(tokens_log)
        
        for log in tokens_log:
            model_name = log.get("model", "unknown")
            llm_name = log.get("llm_name", "unknown")
            prompt_tokens = log.get("prompt_tokens", 0)
            completion_tokens = log.get("completion_tokens", 0)
            
            # Calculate cost for this record
            cost_info = self.calculate_cost(prompt_tokens, completion_tokens, model_name, currency)
            record_cost = cost_info["total_cost"]
            total_cost += record_cost
            
            # Statistics by model
            if model_name not in by_model:
                by_model[model_name] = {
                    "total_cost": 0.0,
                    "input_cost": 0.0,
                    "output_cost": 0.0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "calls": 0
                }
            
            by_model[model_name]["total_cost"] += record_cost
            by_model[model_name]["input_cost"] += cost_info["input_cost"]
            by_model[model_name]["output_cost"] += cost_info["output_cost"]
            by_model[model_name]["prompt_tokens"] += prompt_tokens
            by_model[model_name]["completion_tokens"] += completion_tokens
            by_model[model_name]["total_tokens"] += prompt_tokens + completion_tokens
            by_model[model_name]["calls"] += 1
            
            # Statistics by LLM
            if llm_name not in by_llm:
                by_llm[llm_name] = {
                    "total_cost": 0.0,
                    "input_cost": 0.0,
                    "output_cost": 0.0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "calls": 0,
                    "models": set()
                }
            
            by_llm[llm_name]["total_cost"] += record_cost
            by_llm[llm_name]["input_cost"] += cost_info["input_cost"]
            by_llm[llm_name]["output_cost"] += cost_info["output_cost"]
            by_llm[llm_name]["prompt_tokens"] += prompt_tokens
            by_llm[llm_name]["completion_tokens"] += completion_tokens
            by_llm[llm_name]["total_tokens"] += prompt_tokens + completion_tokens
            by_llm[llm_name]["calls"] += 1
            by_llm[llm_name]["models"].add(model_name)
            
            # Total statistics
            total_tokens += prompt_tokens + completion_tokens
            total_prompt_tokens += prompt_tokens
            total_completion_tokens += completion_tokens
        
        # Convert set to list (needed for JSON serialization)
        for llm_data in by_llm.values():
            llm_data["models"] = list(llm_data["models"])
        
        return {
            "total_cost": total_cost,
            "currency": currency.upper(),
            "by_model": by_model,
            "by_llm": by_llm,
            "summary": {
                "total_tokens": total_tokens,
                "total_prompt_tokens": total_prompt_tokens,
                "total_completion_tokens": total_completion_tokens,
                "total_calls": total_calls
            }
        }
    
    def format_cost_report(self, 
                          cost_analysis: Dict[str, Any], 
                          include_model_details: bool = True,
                          include_llm_details: bool = True) -> str:
        """
        Format cost report as readable text
        
        Args:
            cost_analysis: calculate_tokens_log_costs的返回结果
            include_model_details: 是否包含按模型的详细信息
            include_llm_details: 是否包含按LLM的详细信息
            
        Returns:
            格式化的报告文本
        """
        currency = cost_analysis["currency"]
        symbol = self.pricing_data.get("currency_symbols", {}).get(currency, currency)
        total_cost = cost_analysis["total_cost"]
        summary = cost_analysis["summary"]
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("📊 TOKEN成本分析报告")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # 总体统计
        report_lines.append("💰 总体成本:")
        report_lines.append(f"   总费用: {symbol}{total_cost:.4f} {currency}")
        report_lines.append(f"   总tokens: {summary['total_tokens']:,}")
        report_lines.append(f"   输入tokens: {summary['total_prompt_tokens']:,}")
        report_lines.append(f"   输出tokens: {summary['total_completion_tokens']:,}")
        report_lines.append(f"   API调用次数: {summary['total_calls']:,}")
        report_lines.append("")
        
        # 按LLM详细信息
        if include_llm_details and cost_analysis["by_llm"]:
            report_lines.append("🤖 按LLM统计:")
            report_lines.append("-" * 80)
            
            # 表头
            header = f"{'LLM名称':<15} {'费用':<12} {'Tokens':<10} {'调用次数':<8} {'模型':<20}"
            report_lines.append(header)
            report_lines.append("-" * 80)
            
            # 按费用排序
            sorted_llms = sorted(cost_analysis["by_llm"].items(), 
                               key=lambda x: x[1]["total_cost"], reverse=True)
            
            for llm_name, llm_data in sorted_llms:
                models_str = ", ".join(llm_data["models"][:2])  # 最多显示2个模型名
                if len(llm_data["models"]) > 2:
                    models_str += "..."
                
                row = f"{llm_name:<15} {symbol}{llm_data['total_cost']:<11.4f} {llm_data['total_tokens']:<10,} {llm_data['calls']:<8} {models_str:<20}"
                report_lines.append(row)
            
            report_lines.append("")
        
        # 按模型详细信息
        if include_model_details and cost_analysis["by_model"]:
            report_lines.append("🏷️ 按模型统计:")
            report_lines.append("-" * 80)
            
            # 表头
            header = f"{'模型名称':<20} {'总费用':<12} {'输入费用':<12} {'输出费用':<12} {'Tokens':<10} {'调用':<6}"
            report_lines.append(header)
            report_lines.append("-" * 80)
            
            # 按费用排序
            sorted_models = sorted(cost_analysis["by_model"].items(), 
                                 key=lambda x: x[1]["total_cost"], reverse=True)
            
            for model_name, model_data in sorted_models:
                row = (f"{model_name:<20} "
                      f"{symbol}{model_data['total_cost']:<11.4f} "
                      f"{symbol}{model_data['input_cost']:<11.4f} "
                      f"{symbol}{model_data['output_cost']:<11.4f} "
                      f"{model_data['total_tokens']:<10,} "
                      f"{model_data['calls']:<6}")
                report_lines.append(row)
            
            report_lines.append("")
        
        # 汇率信息（如果是人民币）
        if currency == "CNY":
            report_lines.append(f"💱 汇率信息: 1 USD = {self.exchange_rate} CNY")
            usd_total = total_cost / self.exchange_rate
            report_lines.append(f"   美元等价: ${usd_total:.4f} USD")
            report_lines.append("")
        
        # 时间戳
        report_lines.append(f"📅 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def save_cost_report(self, 
                        cost_analysis: Dict[str, Any], 
                        output_path: str,
                        include_json: bool = True) -> str:
        """
        保存成本报告到文件
        
        Args:
            cost_analysis: 成本分析结果
            output_path: 输出文件路径（不含扩展名）
            include_json: 是否同时保存JSON格式的详细数据
            
        Returns:
            报告文件路径
        """
        # 保存文本报告
        txt_path = f"{output_path}_cost_report.txt"
        report_text = self.format_cost_report(cost_analysis)
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        # 保存JSON详细数据
        if include_json:
            json_path = f"{output_path}_cost_analysis.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(cost_analysis, f, indent=2, ensure_ascii=False)
            
            try:
                from i18n.i18n_manager import get_message
                print(get_message("cost_report_saved"))
                print(get_message("text_report", path=txt_path))
                print(get_message("detailed_data", path=json_path))
            except:
                print(f"💾 Cost report saved:")
                print(f"   📄 Text report: {txt_path}")
                print(f"   📊 Detailed data: {json_path}")
        else:
            try:
                from i18n.i18n_manager import get_message
                print(get_message("cost_report_saved_simple", path=txt_path))
            except:
                print(f"💾 Cost report saved: {txt_path}")
        
        return txt_path

def load_tokens_from_csv(csv_path: str) -> List[Dict[str, Any]]:
    """
    从CSV文件加载tokens记录
    
    Args:
        csv_path: CSV文件路径
        
    Returns:
        tokens记录列表
    """
    import pandas as pd
    
    try:
        df = pd.read_csv(csv_path)
        return df.to_dict('records')
    except Exception as e:
        print(f"Error loading tokens from CSV: {e}")
        return []

# 使用示例
if __name__ == "__main__":
    # 创建计算器实例
    calculator = TokenCostCalculator()
    
    # 示例tokens日志
    sample_tokens_log = [
        {
            "timestamp": "2024-08-24T10:00:00",
            "operation": "study_screening",
            "llm_name": "LLM_A",
            "model": "gpt-4o-mini",
            "prompt_tokens": 1500,
            "completion_tokens": 200,
            "total_tokens": 1700
        },
        {
            "timestamp": "2024-08-24T10:01:00", 
            "operation": "study_screening",
            "llm_name": "LLM_B",
            "model": "gpt-4o-mini",
            "prompt_tokens": 1450,
            "completion_tokens": 180,
            "total_tokens": 1630
        }
    ]
    
    # 计算美元成本
    usd_analysis = calculator.calculate_tokens_log_costs(sample_tokens_log, "USD")
    print(calculator.format_cost_report(usd_analysis))
    
    print("\n" + "="*50 + "\n")
    
    # 计算人民币成本
    cny_analysis = calculator.calculate_tokens_log_costs(sample_tokens_log, "CNY")
    print(calculator.format_cost_report(cny_analysis))