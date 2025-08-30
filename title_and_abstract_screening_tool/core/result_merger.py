#!/usr/bin/env python3
"""
结果合并器
按顺序合并各个并行筛选器产生的XML和Excel文件
"""

import os
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import json
import shutil


class ResultMerger:
    """结果合并器"""
    
    def __init__(self, output_directory, final_output_prefix="final_results"):
        self.output_directory = Path(output_directory)
        self.final_output_prefix = final_output_prefix
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
    def merge_xml_files(self, xml_file_paths, output_xml_path):
        """
        合并多个XML文件，保持记录顺序
        
        Args:
            xml_file_paths (list): XML文件路径列表，按批次顺序排列
            output_xml_path (str): 输出XML文件路径
        """
        try:
            try:
                from i18n.i18n_manager import get_message
                print(f"\n{get_message('xml_merge_start')}")
                print(get_message("files_to_merge", count=len(xml_file_paths)))
            except:
                print(f"\n📄 Starting XML file merge...")
                print(f"Files to merge: {len(xml_file_paths)}")
            
            # 检查所有文件是否存在
            missing_files = []
            for file_path in xml_file_paths:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                raise FileNotFoundError(f"以下文件不存在: {missing_files}")
            
            # 解析第一个文件作为基础结构
            first_file = xml_file_paths[0]
            tree = ET.parse(first_file)
            root = tree.getroot()
            
            # 获取records容器
            records_container = root.find('.//records')
            if records_container is None:
                # 如果没有records容器，创建一个
                records_container = ET.SubElement(root, 'records')
            else:
                # 清空现有记录
                records_container.clear()
            
            total_merged_records = 0
            
            # 按顺序合并所有文件的记录
            for i, file_path in enumerate(xml_file_paths, 1):
                try:
                    from i18n.i18n_manager import get_message
                    print(get_message("processing_file", current=i, total=len(xml_file_paths), filename=os.path.basename(file_path)))
                except:
                    print(f"  Processing file {i}/{len(xml_file_paths)}: {os.path.basename(file_path)}")
                
                # 解析当前文件
                current_tree = ET.parse(file_path)
                current_root = current_tree.getroot()
                
                # 获取当前文件的records
                current_records = current_root.findall('.//record')
                
                # 将记录添加到主文件
                for record in current_records:
                    records_container.append(record)
                    total_merged_records += 1
            
            # 保存合并后的文件
            ET.indent(tree, space="  ", level=0)  # 格式化XML
            tree.write(output_xml_path, encoding='utf-8', xml_declaration=True)
            
            try:
                from i18n.i18n_manager import get_message
                print(get_message("xml_merge_completed", count=total_merged_records))
                print(get_message("xml_output_file", path=output_xml_path))
            except:
                print(f"✓ XML merge completed: {total_merged_records} records")
                print(f"✓ Output file: {output_xml_path}")
            
            return {
                'success': True,
                'total_records': total_merged_records,
                'output_file': output_xml_path
            }
            
        except Exception as e:
            try:
                from i18n.i18n_manager import get_message
                print(get_message("xml_merge_failed", error=str(e)))
            except:
                print(f"❌ XML merge failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def merge_excel_files(self, excel_file_paths, output_excel_path):
        """
        合并多个Excel文件，保持记录顺序
        
        Args:
            excel_file_paths (list): Excel文件路径列表，按批次顺序排列
            output_excel_path (str): 输出Excel文件路径
        """
        try:
            try:
                from i18n.i18n_manager import get_message
                print(f"\n{get_message('excel_merge_start')}")
                print(get_message("files_to_merge", count=len(excel_file_paths)))
            except:
                print(f"\n📊 Starting Excel file merge...")
                print(f"Files to merge: {len(excel_file_paths)}")
            
            # 检查所有文件是否存在
            missing_files = []
            for file_path in excel_file_paths:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                raise FileNotFoundError(f"以下文件不存在: {missing_files}")
            
            merged_dataframes = []
            total_merged_records = 0
            
            # 按顺序读取并合并所有Excel文件
            for i, file_path in enumerate(excel_file_paths, 1):
                try:
                    from i18n.i18n_manager import get_message
                    print(get_message("excel_processing_file", current=i, total=len(excel_file_paths), filename=os.path.basename(file_path)))
                except:
                    print(f"  Processing file {i}/{len(excel_file_paths)}: {os.path.basename(file_path)}")
                
                try:
                    # 读取Excel文件
                    df = pd.read_excel(file_path)
                    
                    if not df.empty:
                        merged_dataframes.append(df)
                        total_merged_records += len(df)
                        print(f"    - 读取 {len(df)} 条记录")
                    else:
                        print(f"    - 文件为空，跳过")
                        
                except Exception as e:
                    print(f"    ⚠️  读取文件失败: {str(e)}")
                    continue
            
            if not merged_dataframes:
                raise ValueError("没有有效的Excel文件可以合并")
            
            # 合并所有DataFrame
            final_df = pd.concat(merged_dataframes, ignore_index=True)
            
            # 添加批次信息（可选）
            if 'batch_id' not in final_df.columns:
                batch_info = []
                current_batch = 1
                current_count = 0
                
                for df in merged_dataframes:
                    batch_size = len(df)
                    batch_info.extend([current_batch] * batch_size)
                    current_batch += 1
                
                final_df['batch_id'] = batch_info
            
            # 保存合并后的文件
            final_df.to_excel(output_excel_path, index=False)
            
            print(f"✓ Excel合并完成: {total_merged_records} 条记录")
            print(f"✓ 输出文件: {output_excel_path}")
            
            return {
                'success': True,
                'total_records': total_merged_records,
                'output_file': output_excel_path,
                'columns': list(final_df.columns)
            }
            
        except Exception as e:
            print(f"❌ Excel合并失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def merge_batch_results(self, state, backup_individual=True):
        """
        根据状态文件合并所有批次结果
        
        Args:
            state (dict): 包含批次信息的状态字典
            backup_individual (bool): 是否备份个别结果文件
        """
        try:
            print(f"\n🔄 开始合并批次结果...")
            
            # 获取已完成的批次
            completed_batches = [b for b in state['batches'] if b['status'] == 'completed']
            
            if not completed_batches:
                raise ValueError("没有已完成的批次可以合并")
            
            # 按batch_id排序确保顺序正确
            completed_batches.sort(key=lambda x: x['batch_id'])
            
            print(f"发现 {len(completed_batches)} 个已完成批次")
            
            # 收集文件路径
            xml_files = []
            excel_files = []
            
            for batch in completed_batches:
                if 'output_files' in batch:
                    xml_file = batch['output_files'].get('xml')
                    excel_file = batch['output_files'].get('excel')
                    
                    if xml_file and os.path.exists(xml_file):
                        xml_files.append(xml_file)
                    
                    if excel_file and os.path.exists(excel_file):
                        excel_files.append(excel_file)
            
            # 生成输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            output_xml = self.output_directory / f"{self.final_output_prefix}_{timestamp}.xml"
            output_excel = self.output_directory / f"{self.final_output_prefix}_{timestamp}.xlsx"
            
            results = {
                'timestamp': timestamp,
                'session_id': state.get('session_id', 'unknown'),
                'total_batches': len(completed_batches),
                'xml_merge': None,
                'excel_merge': None
            }
            
            # 合并XML文件
            if xml_files:
                print(f"\n📄 合并 {len(xml_files)} 个XML文件...")
                results['xml_merge'] = self.merge_xml_files(xml_files, str(output_xml))
            else:
                print("⚠️  没有找到XML文件")
            
            # 合并Excel文件
            if excel_files:
                print(f"\n📊 合并 {len(excel_files)} 个Excel文件...")
                results['excel_merge'] = self.merge_excel_files(excel_files, str(output_excel))
            else:
                print("⚠️  没有找到Excel文件")
            
            # 💰 新增：合并token统计和成本分析
            print(f"\n📈 合并token统计和成本分析...")
            results['token_merge'] = self.merge_token_statistics(state, timestamp)
            
            # 备份个别结果文件
            if backup_individual:
                self.backup_individual_files(xml_files + excel_files, timestamp)
            
            # 生成合并报告
            self.generate_merge_report(results, completed_batches)
            
            return results
            
        except Exception as e:
            print(f"❌ 批次结果合并失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def backup_individual_files(self, file_paths, timestamp):
        """备份个别结果文件"""
        try:
            backup_dir = self.output_directory / f"backup_{timestamp}"
            backup_dir.mkdir(exist_ok=True)
            
            print(f"\n💾 备份个别结果文件到: {backup_dir}")
            
            for file_path in file_paths:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    backup_path = backup_dir / filename
                    shutil.copy2(file_path, backup_path)
                    print(f"  ✓ {filename}")
            
            print(f"✓ 备份完成: {len(file_paths)} 个文件")
            
        except Exception as e:
            print(f"⚠️  备份失败: {str(e)}")
    
    def generate_merge_report(self, results, completed_batches):
        """生成合并报告"""
        try:
            timestamp = results['timestamp']
            report_path = self.output_directory / f"merge_report_{timestamp}.txt"
            
            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("并行筛选结果合并报告")
            report_lines.append("=" * 80)
            report_lines.append("")
            
            # 基本信息
            report_lines.append("基本信息:")
            report_lines.append(f"  会话ID: {results['session_id']}")
            report_lines.append(f"  合并时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"  合并批次数: {results['total_batches']}")
            report_lines.append("")
            
            # XML合并结果
            if results['xml_merge']:
                xml_result = results['xml_merge']
                if xml_result['success']:
                    report_lines.append("XML合并结果:")
                    report_lines.append(f"  状态: ✅ 成功")
                    report_lines.append(f"  总记录数: {xml_result['total_records']}")
                    report_lines.append(f"  输出文件: {os.path.basename(xml_result['output_file'])}")
                else:
                    report_lines.append("XML合并结果:")
                    report_lines.append(f"  状态: ❌ 失败")
                    report_lines.append(f"  错误: {xml_result['error']}")
                report_lines.append("")
            
            # Excel合并结果
            if results['excel_merge']:
                excel_result = results['excel_merge']
                if excel_result['success']:
                    report_lines.append("Excel合并结果:")
                    report_lines.append(f"  状态: ✅ 成功")
                    report_lines.append(f"  总记录数: {excel_result['total_records']}")
                    report_lines.append(f"  输出文件: {os.path.basename(excel_result['output_file'])}")
                    report_lines.append(f"  包含列: {', '.join(excel_result['columns'])}")
                else:
                    report_lines.append("Excel合并结果:")
                    report_lines.append(f"  状态: ❌ 失败")
                    report_lines.append(f"  错误: {excel_result['error']}")
                report_lines.append("")
            
            # 💰 新增：Token成本统计
            if results.get('token_merge'):
                token_result = results['token_merge']
                if token_result.get('success', False):
                    report_lines.append("Token成本统计:")
                    report_lines.append(f"  状态: ✅ 成功")
                    report_lines.append(f"  Token记录数: {token_result['total_records']}")
                    report_lines.append(f"  合并CSV: {os.path.basename(token_result['merged_csv'])}")
                    
                    # 显示成本信息（如果有）
                    if 'usd_analysis' in token_result:
                        usd_analysis = token_result['usd_analysis']
                        cny_analysis = token_result['cny_analysis']
                        
                        report_lines.append(f"  总token数: {usd_analysis['summary']['total_tokens']:,}")
                        report_lines.append(f"  API调用次数: {usd_analysis['summary']['total_calls']:,}")
                        report_lines.append(f"  美元成本: ${usd_analysis['total_cost']:.4f} USD")
                        report_lines.append(f"  人民币成本: ¥{cny_analysis['total_cost']:.2f} CNY")
                        
                        # 按模型成本统计
                        report_lines.append("  按模型成本:")
                        for model_name, model_data in usd_analysis['by_model'].items():
                            cny_cost = cny_analysis['by_model'][model_name]['total_cost']
                            report_lines.append(f"    - {model_name}: ${model_data['total_cost']:.4f} USD / ¥{cny_cost:.2f} CNY")
                    
                    if 'cost_error' in token_result:
                        report_lines.append(f"  成本计算错误: {token_result['cost_error']}")
                        
                else:
                    report_lines.append("Token成本统计:")
                    report_lines.append(f"  状态: ❌ 失败")
                    report_lines.append(f"  错误: {token_result.get('error', '未知错误')}")
                
                report_lines.append("")
            
            # 批次详情
            report_lines.append("批次详情:")
            report_lines.append("-" * 80)
            header = f"{'批次ID':<8} {'起始记录':<10} {'结束记录':<10} {'记录数':<8} {'状态':<10}"
            report_lines.append(header)
            report_lines.append("-" * 80)
            
            for batch in completed_batches:
                row = (f"{batch['batch_id']:<8} "
                      f"{batch['start_record']:<10} "
                      f"{batch['end_record']:<10} "
                      f"{batch['record_count']:<8} "
                      f"{batch['status']:<10}")
                report_lines.append(row)
            
            report_lines.append("-" * 80)
            report_lines.append("")
            report_lines.append("=" * 80)
            
            # 保存报告
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            print(f"\n📋 合并报告已生成: {report_path}")
            
        except Exception as e:
            print(f"⚠️  生成合并报告失败: {str(e)}")
    
    def merge_token_statistics(self, state, timestamp):
        """
        合并各批次的token统计和成本分析
        
        Args:
            state (dict): 状态字典
            timestamp (str): 时间戳
        """
        try:
            print(f"\n📊 开始合并token统计...")
            
            # 获取已完成的批次
            completed_batches = [b for b in state['batches'] if b['status'] == 'completed']
            
            if not completed_batches:
                print("⚠️  没有已完成批次的token统计可以合并")
                return None
            
            # 收集所有token CSV文件
            token_csv_files = []
            all_tokens_log = []
            
            for batch in completed_batches:
                if 'output_files' in batch:
                    # 尝试查找token usage CSV文件
                    xml_file = batch['output_files'].get('xml', '')
                    if xml_file:
                        # 从XML文件路径推导token CSV文件路径
                        base_name = os.path.splitext(xml_file)[0]
                        token_csv = f"{base_name}_tokens_usage.csv"
                        
                        if os.path.exists(token_csv):
                            token_csv_files.append(token_csv)
                            print(f"  找到批次 {batch['batch_id']} 的token统计: {os.path.basename(token_csv)}")
                            
                            # 读取CSV数据
                            try:
                                import pandas as pd
                                df = pd.read_csv(token_csv)
                                batch_tokens = df.to_dict('records')
                                all_tokens_log.extend(batch_tokens)
                            except Exception as e:
                                print(f"    ⚠️  读取失败: {str(e)}")
                        else:
                            print(f"  批次 {batch['batch_id']} 没有找到token统计文件")
            
            if not all_tokens_log:
                print("⚠️  没有找到有效的token统计数据")
                return None
            
            print(f"📋 总计收集到 {len(all_tokens_log)} 条token使用记录")
            
            # 保存合并后的token统计CSV
            merged_csv_path = self.output_directory / f"final_tokens_usage_{timestamp}.csv"
            
            import pandas as pd
            merged_df = pd.DataFrame(all_tokens_log)
            merged_df.to_csv(merged_csv_path, index=False)
            print(f"✓ 合并token统计CSV: {merged_csv_path}")
            
            # 计算并保存成本分析
            try:
                from src.token_cost_calculator import TokenCostCalculator
                
                calculator = TokenCostCalculator()
                
                # 计算美元和人民币成本
                usd_analysis = calculator.calculate_tokens_log_costs(all_tokens_log, "USD")
                cny_analysis = calculator.calculate_tokens_log_costs(all_tokens_log, "CNY")
                
                # 保存成本报告
                base_path = str(self.output_directory / f"final_cost_analysis_{timestamp}")
                calculator.save_cost_report(usd_analysis, f"{base_path}_usd")
                calculator.save_cost_report(cny_analysis, f"{base_path}_cny")
                
                # 显示成本汇总
                print(f"\n💰 最终成本汇总:")
                print(f"  美元费用: ${usd_analysis['total_cost']:.4f} USD")
                print(f"  人民币费用: ¥{cny_analysis['total_cost']:.2f} CNY")
                print(f"  总tokens: {usd_analysis['summary']['total_tokens']:,}")
                print(f"  API调用次数: {usd_analysis['summary']['total_calls']:,}")
                
                # 按模型显示成本
                print(f"\n🏷️  各模型成本统计:")
                for model_name, model_data in usd_analysis['by_model'].items():
                    cny_cost = cny_analysis['by_model'][model_name]['total_cost']
                    print(f"  - {model_name}: ${model_data['total_cost']:.4f} USD / ¥{cny_cost:.2f} CNY")
                
                return {
                    'success': True,
                    'merged_csv': str(merged_csv_path),
                    'usd_analysis': usd_analysis,
                    'cny_analysis': cny_analysis,
                    'total_records': len(all_tokens_log)
                }
                
            except ImportError:
                print("⚠️  成本计算模块未找到，仅保存基础token统计")
                return {
                    'success': True,
                    'merged_csv': str(merged_csv_path),
                    'total_records': len(all_tokens_log)
                }
                
            except Exception as e:
                print(f"⚠️  成本计算失败: {str(e)}")
                return {
                    'success': True,
                    'merged_csv': str(merged_csv_path),
                    'total_records': len(all_tokens_log),
                    'cost_error': str(e)
                }
            
        except Exception as e:
            print(f"❌ token统计合并失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_temp_files(self, temp_files):
        """清理临时文件"""
        try:
            print(f"\n🧹 清理临时文件...")
            
            cleaned_count = 0
            for file_path in temp_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned_count += 1
                    print(f"  ✓ 删除: {os.path.basename(file_path)}")
            
            print(f"✓ 清理完成: {cleaned_count} 个文件")
            
        except Exception as e:
            print(f"⚠️  清理临时文件失败: {str(e)}")


def merge_results_from_state(state_file_path, output_directory, 
                           final_output_prefix="final_results", 
                           backup_individual=True):
    """
    从状态文件合并结果的便捷函数
    
    Args:
        state_file_path (str): 状态文件路径
        output_directory (str): 输出目录
        final_output_prefix (str): 最终文件前缀
        backup_individual (bool): 是否备份个别文件
    """
    try:
        # 读取状态文件
        with open(state_file_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # 创建合并器
        merger = ResultMerger(output_directory, final_output_prefix)
        
        # 执行合并
        results = merger.merge_batch_results(state, backup_individual)
        
        return results
        
    except Exception as e:
        print(f"❌ 从状态文件合并失败: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试代码
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python result_merger.py <状态文件> <输出目录>")
        sys.exit(1)
    
    state_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("🔄 开始结果合并...")
    results = merge_results_from_state(state_file, output_dir)
    
    if results.get('success', False):
        print("✅ 合并成功!")
    else:
        print(f"❌ 合并失败: {results.get('error', '未知错误')}")
        sys.exit(1)
