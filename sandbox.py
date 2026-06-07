# -*- coding: utf-8 -*-
"""
Professional Code Risk Auditor V2.0 (PyQt6 稳定版 最终无错版)
适配 PyQt6 v6.11.0 稳定版 | 已修复所有导入错误
"""
import sys
import os
import time
from typing import List, Set, Dict, Tuple

# --------------- PyQt6 标准导入（100% 适配 v6.11.0）---------------
from PyQt6.QtWidgets import (
    # 基础控件
    QApplication, QMainWindow, QWidget, QFrame, QDialog,
    # 布局类
    QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox,
    # 按钮与输入控件
    QPushButton, QLineEdit, QTextEdit, QLabel,
    # 文件与消息框
    QFileDialog, QMessageBox, QDialogButtonBox,
    # 状态栏/工具栏/菜单栏（关键修正：从 QtWidgets 导入）
    QStatusBar, QToolBar, QMenuBar, QMenu,
    # 列表与进度条
    QListWidget, QListWidgetItem, QProgressBar
)

from PyQt6.QtGui import (
    QFont, QTextCharFormat, QColor, QTextCursor,
    QAction, QIcon
)

from PyQt6.QtCore import (
    Qt, QDateTime, QFileInfo, QDir
)

# ===================== 全局配置区 =====================
RISK_KEYWORDS: Set[str] = {
    "os", "subprocess", "socket", "ctypes", "shutil",
    "eval", "exec", "__import__", "system", "popen",
    "requests", "urllib", "ftp", "multiprocessing", "threading",
    "C:\\Windows", "/etc", "/root", "/bin", "/usr",
    "delattr", "setattr", "globals", "locals", "open("
}
SUPPORT_CODE_SUFFIX: Tuple[str, ...] = (".py", ".txt", ".cpp", ".c", ".bat", ".js", ".java", ".h", ".json")
FILE_DIALOG_FILTER = "代码文件 (*.py *.txt *.cpp *.c *.bat *.js *.java *.h);;所有文件 (*.*)"
SOFTWARE_VERSION = "V2.0 Professional (Stable v6.11.0)"
AUTHOR_INFO = "PyQt6 v6.11.0 Native Develop"

# ===================== 关于弹窗 =====================
class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于本软件")
        self.setStyleSheet("QDialog { background-color: rgba(42, 49, 60, 1.0); }")
        self.setFixedSize(420, 280)
        self.init_dialog_ui()

    def init_dialog_ui(self):
        layout = QVBoxLayout()
        title_label = QLabel("专业代码风险审查系统")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))

        ver_label = QLabel(f"软件版本：{SOFTWARE_VERSION}")
        ver_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dev_label = QLabel(f"开发架构：{AUTHOR_INFO}")
        dev_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tip_label = QLabel("纯原生PyQt6构建，无额外第三方图形库\n支持代码风险检测、编辑、清理、批量扫描")
        tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn_box.accepted.connect(self.close)

        layout.addWidget(title_label)
        layout.addSpacing(20)
        layout.addWidget(ver_label)
        layout.addWidget(dev_label)
        layout.addSpacing(15)
        layout.addWidget(tip_label)
        layout.addStretch()
        layout.addWidget(btn_box)
        self.setLayout(layout)

# ===================== 主窗口 =====================
class ProfessionalCodeAudit(QMainWindow):
    def __init__(self):
        super().__init__()
        self.window_title = f"专业代码风险审查工具 {SOFTWARE_VERSION}"
        self.setWindowTitle(self.window_title)
        self.resize(1400, 850)
        self.setMinimumSize(950, 600)

        # 全局变量
        self.current_file_path: str = ""
        self.risk_line_list: List[int] = []
        self.scan_file_history: List[str] = []
        self.is_file_modified: bool = False

        # 初始化调用链
        self.create_tool_bar()
        self.create_status_bar()
        self.build_main_ui_layout()
        self.create_menu_bar()
        self.set_global_style_sheet()
        self.bind_all_signal_slot()
        self.update_status_tips("系统初始化完成，等待加载代码文件")

    # ========== 菜单栏 ==========
    def create_menu_bar(self):
        menu_bar = QMenuBar(self)
        # 文件菜单
        file_menu = QMenu("文件(F)", self)
        open_act = QAction("打开代码文件", self)
        save_act = QAction("保存当前修改", self)
        save_as_act = QAction("另存为文件", self)
        exit_act = QAction("退出程序", self)
        file_menu.addAction(open_act)
        file_menu.addAction(save_act)
        file_menu.addAction(save_as_act)
        file_menu.addSeparator()
        file_menu.addAction(exit_act)

        # 编辑菜单
        edit_menu = QMenu("编辑(E)", self)
        undo_act = QAction("撤销操作", self)
        redo_act = QAction("重做操作", self)
        clear_act = QAction("清空编辑区", self)
        edit_menu.addAction(undo_act)
        edit_menu.addAction(redo_act)
        edit_menu.addSeparator()
        edit_menu.addAction(clear_act)

        # 扫描菜单
        scan_menu = QMenu("扫描(S)", self)
        single_scan_act = QAction("单文件风险扫描", self)
        dir_scan_act = QAction("目录批量扫描", self)
        scan_menu.addAction(single_scan_act)
        scan_menu.addAction(dir_scan_act)

        # 帮助菜单
        help_menu = QMenu("帮助(H)", self)
        about_act = QAction("关于软件", self)
        help_menu.addAction(about_act)

        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(scan_menu)
        menu_bar.addMenu(help_menu)
        self.setMenuBar(menu_bar)

        # 绑定信号
        open_act.triggered.connect(self.open_code_file)
        save_act.triggered.connect(self.save_current_file)
        save_as_act.triggered.connect(self.save_file_as_new)
        exit_act.triggered.connect(self.close)
        undo_act.triggered.connect(self.code_editor.undo)
        redo_act.triggered.connect(self.code_editor.redo)
        clear_act.triggered.connect(self.clear_editor_content)
        single_scan_act.triggered.connect(self.start_risk_scan)
        dir_scan_act.triggered.connect(self.batch_scan_directory)
        about_act.triggered.connect(self.show_about_dialog)

    # ========== 工具栏 ==========
    def create_tool_bar(self):
        tool_bar = QToolBar("快捷工具栏", self)
        tool_bar.setMovable(False)

        self.tool_open_btn = QPushButton("打开文件")
        self.tool_scan_btn = QPushButton("风险扫描")
        self.tool_del_btn = QPushButton("删除风险行")
        self.tool_save_btn = QPushButton("保存文件")

        tool_bar.addWidget(self.tool_open_btn)
        tool_bar.addWidget(self.tool_scan_btn)
        tool_bar.addWidget(self.tool_del_btn)
        tool_bar.addWidget(self.tool_save_btn)
        self.addToolBar(tool_bar)

    # ========== 状态栏 ==========
    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_file_info = QLabel("当前文件：无")
        self.status_risk_info = QLabel("风险数量：0")
        self.status_bar.addPermanentWidget(self.status_file_info)
        self.status_bar.addPermanentWidget(self.status_risk_info)

    # ========== 主界面布局 ==========
    def build_main_ui_layout(self):
        center_widget = QWidget()
        self.setCentralWidget(center_widget)
        main_hor_layout = QHBoxLayout(center_widget)
        main_hor_layout.setContentsMargins(20, 20, 20, 20)
        main_hor_layout.setSpacing(18)

        # 左侧功能面板
        left_group = QGroupBox("功能操作面板")
        left_group.setFixedWidth(240)
        left_layout = QVBoxLayout(left_group)
        left_layout.setContentsMargins(15, 20, 15, 20)
        left_layout.setSpacing(16)

        self.btn_open_file = QPushButton("📂 打开代码文件")
        self.btn_scan_risk = QPushButton("🔍 一键风险扫描")
        self.btn_remove_line = QPushButton("❌ 删除指定代码行")
        self.btn_clear_edit = QPushButton("🧹 清空编辑内容")
        self.btn_save_edit = QPushButton("💾 保存修改文件")

        del_tip_label = QLabel("请输入待删除行号，多行列逗号分隔")
        self.line_input_box = QLineEdit()
        self.line_input_box.setPlaceholderText("例如：2,5,9,16")

        history_label = QLabel("最近打开文件记录")
        self.history_list = QListWidget()

        left_layout.addWidget(self.btn_open_file)
        left_layout.addWidget(self.btn_scan_risk)
        left_layout.addWidget(del_tip_label)
        left_layout.addWidget(self.line_input_box)
        left_layout.addWidget(self.btn_remove_line)
        left_layout.addWidget(self.btn_save_edit)
        left_layout.addWidget(self.btn_clear_edit)
        left_layout.addSpacing(10)
        left_layout.addWidget(history_label)
        left_layout.addWidget(self.history_list)

        # 右侧代码编辑区
        right_group = QGroupBox("代码编辑预览区")
        right_layout = QVBoxLayout(right_group)
        right_layout.setContentsMargins(12, 12, 12, 12)

        edit_desc_label = QLabel("规则说明：红色加粗代码判定为高危风险代码，可手动删除清理")
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 11))

        right_layout.addWidget(edit_desc_label)
        right_layout.addWidget(self.code_editor)

        main_hor_layout.addWidget(left_group)
        main_hor_layout.addWidget(right_group)

    # ========== 样式表 ==========
    def set_global_style_sheet(self):
        self.setStyleSheet("""
        QMainWindow{
            background-color: #1E232B;
        }
        QGroupBox{
            color: #E5EDF7;
            font-size: 11pt;
            font-weight: bold;
            border: 1px solid #404A5C;
            border-radius: 10px;
            margin-top: 8px;
            padding-top: 12px;
        }
        QLabel{
            color: #D1D9E8;
            font-size: 10pt;
        }
        QPushButton{
            background-color: #2979FF;
            color: #FFFFFF;
            border-radius: 7px;
            padding: 10px;
            font-size: 10pt;
            border: none;
        }
        QPushButton:hover{
            background-color: #1967D2;
        }
        QPushButton:pressed{
            background-color: #0D47A1;
        }
        QTextEdit{
            background-color: #151920;
            color: #C5CDDA;
            border-radius: 8px;
            border: 1px solid #3A4454;
        }
        QLineEdit{
            background-color: #151920;
            color: #FFFFFF;
            border-radius: 6px;
            border: 1px solid #3A4454;
            padding: 8px;
            font-size: 10pt;
        }
        QListWidget{
            background-color: #151920;
            color: #C5CDDA;
            border-radius: 6px;
            border: 1px solid #3A4454;
        }
        QStatusBar{
            background-color: #272E3A;
            color: #E5EDF7;
        }
        QMenuBar{
            background-color: #272E3A;
            color: #E5EDF7;
        }
        """)

    # ========== 信号绑定 ==========
    def bind_all_signal_slot(self):
        self.btn_open_file.clicked.connect(self.open_code_file)
        self.btn_scan_risk.clicked.connect(self.start_risk_scan)
        self.btn_remove_line.clicked.connect(self.delete_assign_code_line)
        self.btn_clear_edit.clicked.connect(self.clear_editor_content)
        self.btn_save_edit.clicked.connect(self.save_current_file)

        self.tool_open_btn.clicked.connect(self.open_code_file)
        self.tool_scan_btn.clicked.connect(self.start_risk_scan)
        self.tool_del_btn.clicked.connect(self.delete_assign_code_line)
        self.tool_save_btn.clicked.connect(self.save_current_file)

        self.code_editor.textChanged.connect(self.mark_file_modify_state)

    # ========== 状态栏更新 ==========
    def update_status_tips(self, msg: str):
        self.status_bar.showMessage(msg, 3000)

    def refresh_file_status_info(self):
        if self.current_file_path:
            file_name = os.path.basename(self.current_file_path)
            self.status_file_info.setText(f"当前文件：{file_name}")
        else:
            self.status_file_info.setText("当前文件：无")
        self.status_risk_info.setText(f"风险数量：{len(self.risk_line_list)}")

    # ========== 文件修改标记 ==========
    def mark_file_modify_state(self):
        self.is_file_modified = True

    # ========== 打开文件 ==========
    def open_code_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择代码审查文件", "", FILE_DIALOG_FILTER)
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            self.code_editor.setPlainText(content)
            self.current_file_path = file_path
            self.risk_line_list.clear()
            self.is_file_modified = False

            if file_path not in self.scan_file_history:
                self.scan_file_history.append(file_path)
                QListWidgetItem(os.path.basename(file_path), self.history_list)

            self.refresh_file_status_info()
            self.update_status_tips(f"成功加载文件：{os.path.basename(file_path)}")
            QMessageBox.information(self, "加载完成", f"文件读取成功\n路径：{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "读取失败", f"文件读取异常：{str(e)}")

    # ========== 风险扫描 ==========
    def start_risk_scan(self):
        raw_text = self.code_editor.toPlainText()
        if not raw_text.strip():
            QMessageBox.warning(self, "扫描提示", "编辑区暂无代码内容，无法扫描")
            return

        normal_format = QTextCharFormat()
        normal_format.setForeground(QColor(197, 205, 218))
        cursor = self.code_editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.mergeCharFormat(normal_format)

        self.risk_line_list.clear()
        line_content_list = raw_text.splitlines()

        for line_idx, line_text in enumerate(line_content_list):
            hit_risk = any(risk_word in line_text for risk_word in RISK_KEYWORDS)
            if hit_risk:
                real_line_num = line_idx + 1
                self.risk_line_list.append(real_line_num)
                char_start_pos = sum(len(line)+1 for line in line_content_list[:line_idx])
                risk_format = QTextCharFormat()
                risk_format.setForeground(QColor(255, 70, 70))
                risk_format.setFontWeight(QFont.Weight.Bold)
                cursor.setPosition(char_start_pos)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
                cursor.mergeCharFormat(risk_format)

        risk_count = len(self.risk_line_list)
        self.refresh_file_status_info()
        if risk_count > 0:
            self.update_status_tips(f"扫描完成，检测到 {risk_count} 处高危代码")
            QMessageBox.warning(self, "风险扫描结果", f"共发现 {risk_count} 条可疑风险代码\n风险行号列表：{self.risk_line_list}")
        else:
            self.update_status_tips("扫描结束，未发现任何高危风险代码")
            QMessageBox.information(self, "扫描结果", "代码安全检测通过，无危险内容")

    # ========== 删除指定行 ==========
    def delete_assign_code_line(self):
        input_num_text = self.line_input_box.text().strip()
        if not input_num_text:
            QMessageBox.warning(self, "操作提示", "请输入需要删除的行号数字")
            return
        try:
            num_str_list = input_num_text.split(",")
            delete_line_nums = []
            for s in num_str_list:
                clean_num = s.strip()
                if clean_num.isdigit():
                    delete_line_nums.append(int(clean_num))
        except Exception:
            QMessageBox.critical(self, "格式错误", "行号仅支持纯数字，多个行号用英文逗号分隔")
            return

        original_text = self.code_editor.toPlainText()
        all_lines = original_text.splitlines()
        sorted_del_nums = sorted(delete_line_nums, reverse=True)
        del_success_count = 0
        for line_num in sorted_del_nums:
            if 1 <= line_num <= len(all_lines):
                del all_lines[line_num - 1]
                del_success_count += 1

        new_edit_text = "\n".join(all_lines)
        self.code_editor.setPlainText(new_edit_text)
        self.line_input_box.clear()
        self.update_status_tips(f"成功删除 {del_success_count} 行代码内容")
        QMessageBox.information(self, "删除完成", f"指定风险代码行清理完毕，共移除{del_success_count}行")

    # ========== 清空编辑区 ==========
    def clear_editor_content(self):
        if self.code_editor.toPlainText().strip():
            confirm = QMessageBox.question(self, "清空确认", "确定要清空当前所有编辑代码吗？")
            if confirm == QMessageBox.StandardButton.Yes:
                self.code_editor.clear()
                self.risk_line_list.clear()
                self.current_file_path = ""
                self.refresh_file_status_info()
                self.update_status_tips("编辑区内容已全部清空")
        else:
            QMessageBox.information(self, "提示", "编辑区域原本为空")

    # ========== 保存文件 ==========
    def save_current_file(self):
        if not self.current_file_path:
            self.save_file_as_new()
            return
        try:
            save_content = self.code_editor.toPlainText()
            with open(self.current_file_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(save_content)
            self.is_file_modified = False
            self.update_status_tips("文件修改内容保存成功")
            QMessageBox.information(self, "保存成功", "代码文件已覆盖保存")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"文件写入出错：{str(e)}")

    # ========== 另存为 ==========
    def save_file_as_new(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "另存代码文件", "", FILE_DIALOG_FILTER)
        if not save_path:
            return
        try:
            save_content = self.code_editor.toPlainText()
            with open(save_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(save_content)
            self.current_file_path = save_path
            self.is_file_modified = False
            self.refresh_file_status_info()
            self.update_status_tips("文件另存操作完成")
            QMessageBox.information(self, "另存成功", f"文件已保存至：{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "另存失败", f"文件保存异常：{str(e)}")

    # ========== 批量扫描目录 ==========
    def batch_scan_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择批量扫描目录", "")
        if not dir_path:
            return
        file_count = 0
        risk_total = 0
        dir_obj = QDir(dir_path)
        all_file_info_list = dir_obj.entryInfoList()
        for file_info in all_file_info_list:
            file_suffix = file_info.suffix().lower()
            if f".{file_suffix}" in SUPPORT_CODE_SUFFIX:
                file_count += 1
                try:
                    with open(file_info.absoluteFilePath(), "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                    for line in text.splitlines():
                        if any(word in line for word in RISK_KEYWORDS):
                            risk_total += 1
                except:
                    continue
        self.update_status_tips(f"目录扫描结束，共检测{file_count}个代码文件")
        QMessageBox.information(self, "批量扫描统计", f"扫描文件总数：{file_count}\n累计发现风险代码：{risk_total}处")

    # ========== 关于弹窗 ==========
    def show_about_dialog(self):
        about_dlg = AboutDialog(self)
        about_dlg.exec()

    # ========== 关闭事件 ==========
    def closeEvent(self, event):
        if self.is_file_modified:
            res = QMessageBox.question(self, "退出提醒", "当前代码存在未保存修改，确定直接退出吗？")
            if res == QMessageBox.StandardButton.No:
                event.ignore()
                return
        event.accept()

# ===================== 程序入口 =====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei"))
    main_window = ProfessionalCodeAudit()
    main_window.show()
    sys.exit(app.exec())