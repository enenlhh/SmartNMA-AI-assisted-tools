import sys
import os
import json
import pandas as pd
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QFileDialog, QTextEdit, QLineEdit, QLabel, 
                            QTableWidget, QTableWidgetItem, QProgressBar, QComboBox, QMessageBox,
                            QTabWidget, QFormLayout, QSpinBox, QCheckBox, QScrollArea, QGroupBox,
                            QInputDialog, QSplitter, QFrame, QGridLayout, QTextBrowser, QSizePolicy,
                            QDialog, QVBoxLayout, QHeaderView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap
from src.grade_evaluator import GradeEvaluator, run_grade_evaluation  # 导入您的工具

class ModernButton(QPushButton):
    """Custom styled button"""
    def __init__(self, text, primary=False):
        super().__init__(text)
        self.setMinimumHeight(35)

        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0066cc;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #0052a3; }
                QPushButton:pressed { background-color: #004085; }
                QPushButton:disabled { background-color: #cccccc; color: #666666; }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    color: #495057;
                    border: 1px solid #dee2e6;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover { background-color: #e9ecef; border-color: #adb5bd; }
                QPushButton:pressed { background-color: #dee2e6; }
                QPushButton:disabled { background-color: #f8f9fa; color: #6c757d; border-color: #dee2e6; }
            """)

class StatusCard(QFrame):
    """Status card widget"""
    def __init__(self, title, value="Not set", status="inactive"):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("QFrame { background-color: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 5px; }")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #495057;")
        
        self.value_label = QLabel(value)
        self.value_label.setWordWrap(True)
        self.value_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        
        self.status_indicator = QLabel("●")
        self.update_status(status)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_indicator)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
    
    def update_status(self, status):
        colors = {"active": "#28a745", "warning": "#ffc107", "error": "#dc3545", "inactive": "#6c757d"}
        self.status_indicator.setStyleSheet(f"color: {colors.get(status, '#6c757d')}; font-size: 16px;")
    
    def set_value(self, value):
        self.value_label.setText(value)

class GRADEProcessingWorker(QThread):
    """Worker thread for GRADE evaluation"""
    progress_updated = pyqtSignal(int, int, str)
    log_updated = pyqtSignal(str)
    finished = pyqtSignal(pd.DataFrame, str)  # results_df, output_file
    error_occurred = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.stop_requested = False

    def request_stop(self):
        self.stop_requested = True
        self.log_updated.emit("🛑 Stop request received...")


    def run(self):
        try:
            self.log_updated.emit("🚀 Starting GRADE evaluation...")
            
            model_types = [self.config['model_type']] if self.config['model_type'] != 'both' else ['random', 'fixed']
            all_results = []
            output_files = []
            
            for idx, m_type in enumerate(model_types, 1):
                if self.stop_requested:
                    return
                
                self.log_updated.emit(f"🔄 Processing model: {m_type} ({idx}/{len(model_types)})")
                
                grade_results, output_file = run_grade_evaluation(
                    base_dir=self.config['base_dir'],
                    outcome_name=self.config['outcome_name'],
                    model_type=m_type,
                    ask_for_mid=False,
                    mid_params=self.config.get('mid_params'),
                    rob_params=self.config.get('rob_params'),
                    inconsistency_params=self.config.get('inconsistency_params')
                )
                
                if grade_results is not None:
                    grade_results['Model_Type'] = m_type  # 添加列区分模型
                    all_results.append(grade_results)
                    output_files.append(output_file)
                else:
                    raise ValueError(f"Evaluation failed for {m_type}")
            
            combined_results = pd.concat(all_results, ignore_index=True) if len(all_results) > 1 else all_results[0]
            combined_output = ", ".join(output_files)  # 合并输出文件路径
            
            self.finished.emit(combined_results, combined_output)
                
        except Exception as e:
            self.error_occurred.emit(str(e))


class SmartEBMGRADEApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartEBM GRADE Assessment Agent")
        self.setGeometry(100, 100, 1500, 950)
        self.setMinimumSize(1300, 800)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #f8f9fa; }
            QTabWidget::pane { border: 1px solid #dee2e6; background-color: white; border-radius: 8px; }
            QTabBar::tab { background-color: #f8f9fa; color: #495057; border: 1px solid #dee2e6; padding: 8px 16px; margin-right: 2px; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background-color: white; color: #0066cc; border-bottom-color: white; }
            QTabBar::tab:hover { background-color: #e9ecef; }
            QGroupBox { font-weight: bold; border: 2px solid #dee2e6; border-radius: 8px; margin-top: 1ex; padding-top: 10px; background-color: white; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 10px 0 10px; color: #495057; }
            QLineEdit, QTextEdit, QComboBox, QSpinBox { border: 1px solid #ced4da; border-radius: 4px; padding: 6px; font-size: 13px; }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus { border-color: #0066cc; outline: none; }
            QLabel { color: #495057; }
        """)
        
        self.config = {}
        self.worker = None
        self.dark_mode = False
        self.init_ui()
        
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_indicators)
        self.status_timer.start(1000)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        self.create_header(main_layout)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 800])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter, 1)
        
        self.create_control_buttons(main_layout)

    def create_header(self, layout):
        header_frame = QFrame()
        header_frame.setMinimumHeight(100)
        header_frame.setStyleSheet("QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0066cc, stop:1 #004085); border-radius: 8px; }")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 20, 25, 20)
        header_layout.setSpacing(8)
        
        title_label = QLabel("SmartEBM GRADE Assessment Agent")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        subtitle_label = QLabel("AI-Powered Certainty of Evidence Evaluation for Network Meta-Analysis")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setStyleSheet("color: #cce7ff; margin-top: 5px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)

    def create_left_panel(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        config_group = QGroupBox("📁 Configuration Management")
        config_layout = QHBoxLayout(config_group)
        load_btn = ModernButton("Load from JSON")
        load_btn.clicked.connect(self.load_config_from_file)
        save_btn = ModernButton("Save to JSON")
        save_btn.clicked.connect(self.save_config_to_file)
        config_layout.addWidget(load_btn)
        config_layout.addWidget(save_btn)
        left_layout.addWidget(config_group)
        
        status_group = QGroupBox("📊 Project Status")
        status_layout = QGridLayout(status_group)
        
        self.base_dir_status = StatusCard("Base Directory", "No directory selected")
        self.outcome_status = StatusCard("Outcome Name", "Not set")
        self.model_status = StatusCard("Model Type", "Not selected")
        self.params_status = StatusCard("Parameters", "Default")
        
        status_layout.addWidget(self.base_dir_status, 0, 0)
        status_layout.addWidget(self.outcome_status, 0, 1)
        status_layout.addWidget(self.model_status, 1, 0)
        status_layout.addWidget(self.params_status, 1, 1)
        
        left_layout.addWidget(status_group)
        
        self.config_tabs = QTabWidget()
        self.config_tabs.setMinimumHeight(400)
        self.init_config_tabs()
        left_layout.addWidget(self.config_tabs)
        
        left_layout.addStretch()
        scroll_area.setWidget(left_widget)
        return scroll_area

    def create_right_panel(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)
        
        log_group = QGroupBox("📋 Process Log")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(10, 15, 10, 10)
        
        self.log_display = QTextBrowser()
        self.log_display.setStyleSheet("""
            QTextBrowser {
                background-color: #212529;
                color: #28a745;
                font-family: monospace;
                font-size: 12px;
                border: 1px solid #495057;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        self.log_display.append("🎯 SmartEBM GRADE ready - Configure parameters and start assessment")
        
        log_layout.addWidget(self.log_display)
        right_layout.addWidget(log_group, 1)
        
        scroll_area.setWidget(right_widget)
        return scroll_area

    def create_control_buttons(self, layout):
        button_frame = QFrame()
        button_frame.setFixedHeight(80)
        button_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 15px; }")
        
        outer_layout = QVBoxLayout(button_frame)
        outer_layout.setContentsMargins(15, 0, 15, 0)
        
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(15)
        
        self.start_btn = ModernButton("🚀 Run GRADE Assessment", primary=True)
        self.start_btn.clicked.connect(self.start_assessment)
        self.start_btn.setFixedHeight(45)
        self.start_btn.setMinimumWidth(200)
        
        self.stop_btn = ModernButton("⏹️ Stop Process")
        self.stop_btn.clicked.connect(self.stop_process)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setFixedHeight(45)
        self.stop_btn.setMinimumWidth(120)
        
        self.theme_btn = ModernButton("🌙 Dark Mode")
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setFixedHeight(45)
        self.theme_btn.setMinimumWidth(120)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.theme_btn)
        
        outer_layout.addStretch()
        outer_layout.addWidget(button_container)
        outer_layout.addStretch()
        
        layout.addWidget(button_frame)

    def init_config_tabs(self):
        # Paths tab
        paths_scroll = QScrollArea()
        paths_scroll.setWidgetResizable(True)
        paths_widget = QWidget()
        paths_layout = QFormLayout(paths_widget)
        
        # Base directory
        base_dir_layout = QHBoxLayout()
        self.base_dir_edit = QLineEdit()
        self.base_dir_edit.setPlaceholderText("Select base directory containing NMA results...")
        base_dir_browse = ModernButton("Browse")
        base_dir_browse.clicked.connect(self.select_base_dir)
        base_dir_layout.addWidget(self.base_dir_edit)
        base_dir_layout.addWidget(base_dir_browse)
        paths_layout.addRow("📂 Base Directory:", base_dir_layout)
        
        # Outcome name
        self.outcome_name_edit = QLineEdit()
        self.outcome_name_edit.setPlaceholderText("Enter outcome name...")
        paths_layout.addRow("🏷️ Outcome Name:", self.outcome_name_edit)
        
        # Model type
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems(["both","random", "fixed"])
        paths_layout.addRow("🔄 Model Type:", self.model_type_combo)
        
        paths_scroll.setWidget(paths_widget)
        self.config_tabs.addTab(paths_scroll, "📁 Paths")
        
        # Parameters tab
        params_scroll = QScrollArea()
        params_scroll.setWidgetResizable(True)
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        
        # MID parameters
        mid_group = QGroupBox("📏 MID Parameters")
        mid_layout = QFormLayout(mid_group)
        self.harmful_mid = QLineEdit()
        self.harmful_mid.setPlaceholderText("e.g., 1.25")
        mid_layout.addRow("Harmful MID Threshold:", self.harmful_mid)
        self.benefit_mid = QLineEdit()
        self.benefit_mid.setPlaceholderText("e.g., 0.8")
        mid_layout.addRow("Benefit MID Threshold:", self.benefit_mid)
        params_layout.addWidget(mid_group)
        
        # ROB parameters
        rob_group = QGroupBox("⚠️ ROB Parameters")
        rob_layout = QFormLayout(rob_group)
        self.high_risk_count = QLineEdit()
        self.high_risk_count.setPlaceholderText("e.g., 0.5")
        rob_layout.addRow("High-Risk Study Proportion Threshold:", self.high_risk_count)
        self.high_risk_weight = QLineEdit()
        self.high_risk_weight.setPlaceholderText("e.g., 50")
        rob_layout.addRow("High-Risk Study Weight Threshold:", self.high_risk_weight)
        self.very_serious_weight = QLineEdit()
        self.very_serious_weight.setPlaceholderText("e.g., 80")
        rob_layout.addRow("Very Serious Bias Weight Threshold:", self.very_serious_weight)
        params_layout.addWidget(rob_group)
        
        # Inconsistency parameters
        inc_group = QGroupBox("🔀 Inconsistency Parameters")
        inc_layout = QFormLayout(inc_group)
        self.i2_threshold = QLineEdit()
        self.i2_threshold.setPlaceholderText("e.g., 60")
        inc_layout.addRow("I² Inconsistency Threshold:", self.i2_threshold)
        self.i2_very_serious = QLineEdit()
        self.i2_very_serious.setPlaceholderText("e.g., 90")
        inc_layout.addRow("I² Very Serious Threshold:", self.i2_very_serious)
        self.ci_overlap = QLineEdit()
        self.ci_overlap.setPlaceholderText("e.g., 0.5")
        inc_layout.addRow("CI Overlap Threshold:", self.ci_overlap)
        params_layout.addWidget(inc_group)
        
        params_scroll.setWidget(params_widget)
        self.config_tabs.addTab(params_scroll, "⚙️ Parameters")

    def select_base_dir(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Base Directory")
        if folder_path:
            self.base_dir_edit.setText(folder_path)
            self.config['base_dir'] = folder_path
            self.log_display.append(f"📂 Base directory selected: {os.path.basename(folder_path)}")

    def collect_config(self):
        config = {
            'base_dir': self.base_dir_edit.text(),
            'outcome_name': self.outcome_name_edit.text(),
            'model_type': self.model_type_combo.currentText(),
            'mid_params': {
                'harmful_mid': float(self.harmful_mid.text()) if self.harmful_mid.text() else None,
                'benefit_mid': float(self.benefit_mid.text()) if self.benefit_mid.text() else None
            },
            'rob_params': {
                'high_risk_count_threshold': float(self.high_risk_count.text()) if self.high_risk_count.text() else 0.5,
                'high_risk_weight_threshold': float(self.high_risk_weight.text()) if self.high_risk_weight.text() else 50,
                'very_serious_weight_threshold': float(self.very_serious_weight.text()) if self.very_serious_weight.text() else 80
            },
            'inconsistency_params': {
                'i2_threshold': float(self.i2_threshold.text()) if self.i2_threshold.text() else 60,
                'i2_very_serious_threshold': float(self.i2_very_serious.text()) if self.i2_very_serious.text() else 90,
                'ci_overlap_threshold': float(self.ci_overlap.text()) if self.ci_overlap.text() else 0.5
            }
        }
        return config

    def load_config_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.populate_ui_from_config()
                self.log_display.append(f"✅ Configuration loaded from: {os.path.basename(file_path)}")
                QMessageBox.information(self, "Success", "Configuration loaded successfully!")
            except Exception as e:
                self.log_display.append(f"❌ Failed to load configuration: {str(e)}")
                QMessageBox.warning(self, "Error", f"Failed to load configuration:\n{str(e)}")

    def populate_ui_from_config(self):
        self.base_dir_edit.setText(self.config.get('base_dir', ''))
        self.outcome_name_edit.setText(self.config.get('outcome_name', ''))
        self.model_type_combo.setCurrentText(self.config.get('model_type', 'random'))
        
        mid = self.config.get('mid_params', {})
        self.harmful_mid.setText(str(mid.get('harmful_mid', '')))
        self.benefit_mid.setText(str(mid.get('benefit_mid', '')))
        
        rob = self.config.get('rob_params', {})
        self.high_risk_count.setText(str(rob.get('high_risk_count_threshold', '')))
        self.high_risk_weight.setText(str(rob.get('high_risk_weight_threshold', '')))
        self.very_serious_weight.setText(str(rob.get('very_serious_weight_threshold', '')))
        
        inc = self.config.get('inconsistency_params', {})
        self.i2_threshold.setText(str(inc.get('i2_threshold', '')))
        self.i2_very_serious.setText(str(inc.get('i2_very_serious_threshold', '')))
        self.ci_overlap.setText(str(inc.get('ci_overlap_threshold', '')))

    def save_config_to_file(self):
        self.config = self.collect_config()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "config_grade.json", "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4)
                self.log_display.append(f"✅ Configuration saved to: {os.path.basename(file_path)}")
                QMessageBox.information(self, "Success", "Configuration saved successfully!")
            except Exception as e:
                self.log_display.append(f"❌ Failed to save configuration: {str(e)}")
                QMessageBox.warning(self, "Error", f"Failed to save configuration:\n{str(e)}")

    def start_assessment(self):
        self.config = self.collect_config()
        
        if not self.config['base_dir'] or not os.path.exists(self.config['base_dir']):
            QMessageBox.warning(self, "Configuration Error", "Please select a valid base directory.")
            return
        
        if not self.config['outcome_name']:
            QMessageBox.warning(self, "Configuration Error", "Please enter an outcome name.")
            return
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.worker = GRADEProcessingWorker(self.config)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.log_updated.connect(self.update_log)
        self.worker.finished.connect(self.assessment_finished)
        self.worker.error_occurred.connect(self.process_error)
        self.worker.start()

    def stop_process(self):
        if self.worker and self.worker.isRunning():
            self.worker.request_stop()
            if self.worker.wait(5000):
                self.log_display.append("✅ Process stopped successfully")
            else:
                self.worker.terminate()
                self.log_display.append("⚠️ Process forcefully terminated")
            self.reset_buttons()

    def update_progress(self, current, total, message):
        progress_percent = int((current / total) * 100) if total > 0 else 0
        self.log_display.append(f"Progress: {message} ({progress_percent}%)")

    def update_log(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.append(f"[{timestamp}] {message}")
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def assessment_finished(self, results_df, output_file):
        self.reset_buttons()
        self.log_display.append("🎉 GRADE assessment completed!")
        self.log_display.append(f"📊 Results saved to: {output_file}")
        
        # Display results
        self.show_results_table(results_df)

    def show_results_table(self, df):
        """Display editable results table (reference HTML logic)"""
        dialog = QDialog(self)
        dialog.setWindowTitle("GRADE Assessment Results")
        dialog.setMinimumSize(1200, 800)
        
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setRowCount(len(df))
        table.setColumnCount(len(df.columns))
        table.setHorizontalHeaderLabels(df.columns)
        
        for i in range(len(df)):
            for j in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                table.setItem(i, j, item)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)
        
        save_btn = ModernButton("Save Modified Results")
        save_btn.clicked.connect(lambda: self.save_modified_results(df))
        layout.addWidget(save_btn)
        
        dialog.exec()

    def save_modified_results(self, df):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Results", "", "Excel Files (*.xlsx);;CSV Files (*.csv)")
        if file_path:
            if file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
            else:
                df.to_csv(file_path, index=False)
            self.log_display.append(f"✅ Modified results saved to: {file_path}")

    def process_error(self, error_message):
        self.reset_buttons()
        self.log_display.append(f"❌ Error: {error_message}")
        QMessageBox.critical(self, "Error", f"GRADE assessment failed:\n{error_message}")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.theme_btn.setText("☀️ Light Mode")
            self.log_display.setStyleSheet("background-color: #212529; color: #28a745;")
            self.log_display.append("🌙 Switched to dark mode")
        else:
            self.theme_btn.setText("🌙 Dark Mode")
            self.log_display.setStyleSheet("background-color: white; color: #0066cc;")
            self.log_display.append("☀️ Switched to light mode")

    def reset_buttons(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def update_status_indicators(self):
        """Update status indicators based on current configuration"""
        # Base directory status
        base_dir = self.base_dir_edit.text()
        if base_dir and os.path.exists(base_dir):
            self.base_dir_status.set_value(f"✓ {os.path.basename(base_dir)}")
            self.base_dir_status.update_status("active")
        else:
            self.base_dir_status.set_value("No directory selected" if not base_dir else "❌ Directory not found")
            self.base_dir_status.update_status("inactive" if not base_dir else "error")
        
        # Outcome name status
        outcome_name = self.outcome_name_edit.text()
        if outcome_name:
            self.outcome_status.set_value(f"✓ {outcome_name}")
            self.outcome_status.update_status("active")
        else:
            self.outcome_status.set_value("Not set")
            self.outcome_status.update_status("inactive")
        
        # Model type status
        model_type = self.model_type_combo.currentText()
        if model_type:
            self.model_status.set_value(f"✓ {model_type.capitalize()}")
            self.model_status.update_status("active")
        else:
            self.model_status.set_value("Not selected")
            self.model_status.update_status("inactive")
        
        # Parameters status (check if any are set; simplistic check)
        params_set = any([
            self.harmful_mid.text(), self.benefit_mid.text(),
            self.high_risk_count.text(), self.high_risk_weight.text(), self.very_serious_weight.text(),
            self.i2_threshold.text(), self.i2_very_serious.text(), self.ci_overlap.text()
        ])
        if params_set:
            self.params_status.set_value("✓ Custom parameters set")
            self.params_status.update_status("active")
        else:
            self.params_status.set_value("Default")
            self.params_status.update_status("warning")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SmartEBMGRADEApp()
    window.show()
    sys.exit(app.exec())
