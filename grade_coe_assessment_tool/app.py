import streamlit as st
import pandas as pd
import json
import os
import time
import io
from src.grade_evaluator import GradeEvaluator, list_available_outcomes

# --- 页面配置 ---
st.set_page_config(
    page_title="GRADE 证据质量评估工具",
    page_icon="📊",
    layout="wide"
)

st.title("📊 GRADE 证据质量评估工具")
st.markdown("一个用于网络荟萃分析（NMA）的交互式 GRADE 评估工具。")

# --- 辅助函数 ---

@st.cache_data(show_spinner=False)
def load_config():
    """加载并缓存配置文件"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("错误：`config.json` 文件未找到。请确保它与 `app.py` 在同一目录下。")
        return None
    except json.JSONDecodeError:
        st.error("错误：`config.json` 文件格式不正确。请检查 JSON 语法。")
        return None

def get_excel_download_link(df, filename):
    """生成用于下载 DataFrame 的 Excel 链接"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='GRADE_Results')
    excel_data = output.getvalue()
    st.download_button(
        label=f"📥 下载评估结果 ({filename})",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- 主应用逻辑 ---

# 1. 加载配置
config = load_config()

if config:
    # 在侧边栏显示当前配置
    with st.sidebar:
        st.header("⚙️ 当前配置")
        st.info(f"结果目录: `{config.get('base_dir')}`")
        with st.expander("查看详细参数"):
            st.json(config)
        st.markdown("---")
        st.markdown("如需修改，请直接编辑 `config.json` 文件并刷新本页面。")

    base_dir = config.get("base_dir")

    # 2. 检查路径并列出可用的结局
    if not base_dir or not os.path.exists(base_dir):
        st.warning(f"配置的 `base_dir` 路径不存在: `{base_dir}`。请在 `config.json` 中设置正确的路径。")
    else:
        with st.spinner("正在扫描可用的结局..."):
            available_outcomes = list_available_outcomes(base_dir)

        if not available_outcomes:
            st.warning("在指定目录下未找到任何可供评估的结局。请检查目录结构是否正确。")
        else:
            st.success(f"成功发现 {len(available_outcomes)} 个可用结局。")
            
            # 3. 创建用户输入界面
            col1, col2 = st.columns(2)
            
            with col1:
                outcome_options = {o['outcome']: o for o in available_outcomes}
                selected_outcome_name = st.selectbox(
                    "1. 请选择要评估的结局 (Outcome)",
                    options=outcome_options.keys()
                )
            
            with col2:
                selected_outcome_info = outcome_options[selected_outcome_name]
                selected_model = st.selectbox(
                    "2. 请选择模型 (Model)",
                    options=selected_outcome_info['models']
                )
            
            # 4. 运行评估
            if st.button("🚀 开始 GRADE 评估", type="primary", use_container_width=True):
                st.markdown("---")
                st.subheader("评估结果")

                with st.spinner(f"正在对 **{selected_outcome_name}** 使用 **{selected_model}** 模型进行评估..."):
                    try:
                        start_time = time.time()
                        
                        # 初始化评估器
                        evaluator = GradeEvaluator(
                            base_dir=base_dir,
                            outcome_name=selected_outcome_name,
                            model_type=selected_model,
                            ask_for_mid=False, # Web界面不进行交互式询问
                            mid_params=config.get('mid_params'),
                            rob_params=config.get('rob_params'),
                            inconsistency_params=config.get('inconsistency_params')
                        )
                        
                        # 执行评估
                        grade_results = evaluator.evaluate_grade()
                        
                        end_time = time.time()
                        
                        st.success(f"评估完成！耗时 {end_time - start_time:.2f} 秒。")
                        
                        # 显示结果表格
                        st.dataframe(grade_results)
                        
                        # 提供下载链接
                        output_filename = f"{selected_outcome_name}-{selected_model}-GRADE_Results.xlsx"
                        get_excel_download_link(grade_results, output_filename)

                    except Exception as e:
                        st.error(f"评估过程中发生错误：")
                        st.exception(e)

# 如果配置文件加载失败，显示引导信息
else:
    st.info("请先创建并正确配置 `config.json` 文件。")

