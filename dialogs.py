#!/usr/bin/env python3
"""
SQLite Explorer - Dialogs
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLineEdit, QFileDialog, QMessageBox, QInputDialog, QLabel, QFormLayout, QTableView, QHeaderView, QFrame, QWidget, QScrollArea, QTextEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QGridLayout
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QTimer, QEvent
from config import ConfigManager
import os

class DeleteConfirmDialog(QDialog):
    def __init__(self, parent, item_name):
        super().__init__(parent)
        self.setWindowTitle("Delete Connection")

        self.layout = QVBoxLayout(self)

        self.main_layout = QHBoxLayout()
        self.icon_label = QLabel("?")
        font = self.icon_label.font()
        font.setPointSize(24)
        self.icon_label.setFont(font)
        self.message_label = QLabel(f"Are you sure you want to delete '{item_name}'?")

        self.main_layout.addWidget(self.icon_label)
        self.main_layout.addWidget(self.message_label)

        self.buttons_layout = QHBoxLayout()
        self.yes_button = QPushButton("Yes")
        self.yes_button.clicked.connect(self.accept)
        self.no_button = QPushButton("No")
        self.no_button.clicked.connect(self.reject)
        self.no_button.setDefault(True)

        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.yes_button)
        self.buttons_layout.addWidget(self.no_button)

        self.layout.addLayout(self.main_layout)
        self.layout.addLayout(self.buttons_layout)

class ConnectionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Connections")
        self.config_manager = ConfigManager()
        self.selected_connection = None

        self.layout = QVBoxLayout(self)

        self.connections_list = QListWidget()
        self.connections_list.itemDoubleClicked.connect(self.accept)
        self.connections_list.itemSelectionChanged.connect(self.update_button_states)
        self.layout.addWidget(self.connections_list)

        self.buttons_layout = QHBoxLayout()
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.accept)
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_connection)
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_connection)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_connection)
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.reject)

        self.buttons_layout.addWidget(self.connect_button)
        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.edit_button)
        self.buttons_layout.addWidget(self.delete_button)
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.quit_button)

        self.layout.addLayout(self.buttons_layout)

        self.load_connections()

    def load_connections(self):
        self.config_manager.reload_config()
        self.connections_list.clear()
        connections = self.config_manager.get_all_connections()
        for name in connections.keys():
            self.connections_list.addItem(name)
        self.update_button_states()

    def update_button_states(self):
        has_connections = self.connections_list.count() > 0
        has_selection = self.connections_list.currentItem() is not None

        self.connect_button.setEnabled(has_selection)
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def add_connection(self):
        dialog = AddConnectionDialog(self)
        if dialog.exec_():
            self.load_connections()

    def edit_connection(self):
        selected_item = self.connections_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "Please select a connection to edit.")
            return

        old_name = selected_item.text()
        dialog = AddConnectionDialog(self, connection_name=old_name)
        if dialog.exec_():
            self.load_connections()

    def delete_connection(self):
        selected_item = self.connections_list.currentItem()
        if not selected_item:
            return

        dialog = DeleteConfirmDialog(self, selected_item.text())
        if dialog.exec_() == QDialog.Accepted:
            self.config_manager.remove_connection(selected_item.text())
            self.load_connections()

    def accept(self):
        selected_item = self.connections_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "Please select a connection.")
            return
        self.selected_connection = selected_item.text()
        super().accept()

class AddConnectionDialog(QDialog):
    def __init__(self, parent=None, connection_name=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Connection")
        self.config_manager = ConfigManager()
        self.connection_name = connection_name

        self.layout = QVBoxLayout(self)

        # Use QFormLayout for proper alignment
        self.form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.form_layout.addRow("Connection Name:", self.name_edit)
        
        self.path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        self.path_layout.addWidget(self.path_edit)
        self.path_layout.addWidget(self.browse_button)
        
        self.form_layout.addRow("Database Path:", self.path_layout)
        
        self.layout.addLayout(self.form_layout)

        self.buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_connection)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.buttons_layout)

        if self.connection_name:
            self.name_edit.setText(self.connection_name)
            self.path_edit.setText(self.config_manager.get_connection(self.connection_name))

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Database File", "", "SQLite Databases (*.db *.sqlite *.sqlite3);;All Files (*)")
        if file_path:
            self.path_edit.setText(file_path)

    def save_connection(self):
        name = self.name_edit.text().strip()
        path = self.path_edit.text().strip()

        if not name or not path:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please enter a name and select a path.")
            return

        if not os.path.exists(path):
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "The specified database file does not exist.")
            return

        try:
            # 如果是編輯現有連線，先刪除舊的連線記錄
            if self.connection_name:
                self.config_manager.remove_connection(self.connection_name)

            self.config_manager.add_connection(name, path)
            self.accept()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to save connection: {str(e)}")

class RecordEditDialog(QDialog):
    def __init__(self, parent, table_name, columns, row_data=None, table_schema=None):
        super().__init__(parent)
        self.table_name = table_name
        self.columns = columns
        self.row_data = row_data or {}
        self.table_schema = table_schema or {}
        self.form_fields = {}
        
        is_edit_mode = bool(row_data)
        self.setWindowTitle(f"{'Edit' if is_edit_mode else 'Add'} - {table_name}")
        self.setMinimumSize(500, 300)
        
        self.setup_ui()
        self.load_data()
        
        # 計算並設置最佳對話框高度
        self.adjust_dialog_height()
        
    def adjust_dialog_height(self):
        """根據欄位數量調整對話框高度，避免不必要的滾動"""
        # 計算欄位的數量
        field_count = len(self.columns)
        
        # 基礎高度組件
        title_height = 50      # 標題區域
        footer_height = 60     # 按鈕區域
        padding_height = 40    # 邊距
        
        # 每個欄位的高度（包含標籤和輸入框）
        field_height = 45
        
        # 計算總高度
        total_height = title_height + (field_count * field_height) + footer_height + padding_height
        
        # 限制最大高度（避免對話框過高）
        max_height = 700
        optimal_height = min(total_height, max_height)
        
        # 記錄是否需要滾動（當內容超過最大高度時）
        self.needs_scrolling = total_height > max_height
        
        # 設置對話框大小
        self.resize(600, optimal_height)
        
    def setup_ui(self):
        """設置對話框 UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 簡潔的標題
        is_edit = bool(self.row_data)
        title = QLabel(f"{'Editing' if is_edit else 'Adding'}: {self.table_name}")
        title.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 600;
                color: #1d1d1f;
                padding-bottom: 8px;
            }
        """)
        main_layout.addWidget(title)
        
        # 可滾動的表單區域（只有在需要時才啟用滾動）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        
        # 根據是否需要滾動來設置滾動條策略
        if hasattr(self, 'needs_scrolling') and self.needs_scrolling:
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 預設隱藏，滾動時出現
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            # 創建自定義滾動條行為
            self.setup_scroll_behavior(scroll_area)
        else:
            # 如果不需要滾動，完全禁用滾動條
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 設定滾動區域的大小策略
        from PyQt5.QtWidgets import QSizePolicy
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 滾動條樣式（初始透明隱藏）
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
                border: none;
                opacity: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 4px;
                min-height: 20px;
                margin: 0px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 0, 0, 0.5);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # 表單內容
        content_widget = self.create_form_content()
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # 底部按鈕
        footer_widget = self.create_footer()
        main_layout.addWidget(footer_widget)
        
    def create_form_content(self):
        """創建表單內容區域"""
        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        
        # 設定內容區域的大小策略
        from PyQt5.QtWidgets import QSizePolicy
        content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        
        # 使用 QFormLayout 更簡潔
        form_layout = QFormLayout(content)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignTop)
        form_layout.setContentsMargins(10, 10, 10, 10)  # 添加一些邊距
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)  # 輸入框會擴展填滿
        
        # 為每個欄位創建輸入
        for column in self.columns:
                
            # 創建標籤
            column_type = self.get_column_type(column)
            label_text = column
            if column_type:
                label_text += f" ({column_type})"
            
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #333333;
                    font-weight: 500;
                }
            """)
            
            # 創建輸入控件
            input_widget = self.create_input_widget(column, column_type)
            
            # 添加到表單
            form_layout.addRow(label, input_widget)
        
        return content
        
    def create_input_widget(self, column_name, column_type):
        """根據資料類型創建適當的輸入控件"""
        column_type_lower = column_type.lower() if column_type else ""
        
        # 簡化的樣式
        base_style = """
            border: 1px solid rgba(0, 0, 0, 0.15);
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
            background-color: white;
            min-height: 24px;
            min-width: 300px;
        """
        
        if 'text' in column_type_lower and len(str(self.row_data.get(column_name, ""))) > 100:
            # 長文本使用 QTextEdit
            widget = QTextEdit()
            widget.setMaximumHeight(80)
            widget.setStyleSheet(f"""
                QTextEdit {{
                    {base_style}
                }}
                QTextEdit:focus {{
                    border: 2px solid #007AFF;
                }}
            """)
            # 設置當前值的提示
            if self.row_data and column_name in self.row_data:
                widget.setPlaceholderText(f"Current: {str(self.row_data[column_name])[:50]}...")
        else:
            # 統一使用 QLineEdit（簡化設計）
            widget = QLineEdit()
            widget.setStyleSheet(f"""
                QLineEdit {{
                    {base_style}
                }}
                QLineEdit:focus {{
                    border: 2px solid #007AFF;
                }}
            """)
            # 設置當前值的提示
            if self.row_data and column_name in self.row_data:
                widget.setPlaceholderText(f"Current: {str(self.row_data[column_name])}")
            
        self.form_fields[column_name] = widget
        return widget
        
    def get_column_type(self, column_name):
        """獲取欄位類型"""
        if self.table_schema and column_name in self.table_schema:
            return self.table_schema[column_name].get('type', '')
        return ''
        
    def create_footer(self):
        """創建底部按鈕區域"""
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(8)
        
        # 取消按鈕
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setMinimumWidth(80)
        self.cancel_btn.setFixedHeight(28)
        
        # 保存按鈕
        save_text = "Save" if self.row_data else "Add"
        self.save_btn = QPushButton(save_text)
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setMinimumWidth(80)
        self.save_btn.setFixedHeight(28)
        self.save_btn.setDefault(True)
        
        # 簡潔的按鈕樣式
        cancel_style = """
            QPushButton {
                border: 1px solid rgba(0, 0, 0, 0.15);
                border-radius: 5px;
                background: #ffffff;
                color: #1d1d1f;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #f5f5f7;
                border: 1px solid rgba(0, 0, 0, 0.2);
            }
            QPushButton:pressed {
                background: #e8e8ea;
                border: 1px solid rgba(0, 0, 0, 0.25);
            }
        """
        
        save_style = """
            QPushButton {
                border: 1px solid #007AFF;
                border-radius: 5px;
                background: #007AFF;
                color: white;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #0056CC;
                border: 1px solid #0056CC;
            }
            QPushButton:pressed {
                background: #004299;
                border: 1px solid #004299;
            }
        """
        
        self.cancel_btn.setStyleSheet(cancel_style)
        self.save_btn.setStyleSheet(save_style)
        
        layout.addStretch()
        layout.addWidget(self.cancel_btn)
        layout.addWidget(self.save_btn)
        
        return footer
        
    def setup_scroll_behavior(self, scroll_area):
        """設置滾動條只在捲動時出現的行為"""
        self.scroll_area = scroll_area
        self.scroll_timer = None
        
        # 只有在實際需要滾動時才設置行為
        if hasattr(self, 'needs_scrolling') and self.needs_scrolling:
            # 安裝事件過濾器來監聽滾輪事件
            scroll_area.installEventFilter(self)
            
            # 監聽滾動條值變化
            scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)
        
    def eventFilter(self, obj, event):
        """事件過濾器：監聽滾輪事件"""
        if (obj == self.scroll_area and 
            hasattr(self, 'needs_scrolling') and self.needs_scrolling):
            if event.type() == QEvent.Wheel:
                self.show_scrollbar_temporarily()
        return super().eventFilter(obj, event)
        
    def on_scroll(self):
        """滾動時顯示滾動條"""
        self.show_scrollbar_temporarily()
        
    def show_scrollbar_temporarily(self):
        """暫時顯示滾動條"""
        # 顯示滾動條
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 如果已經有定時器，先停止它
        if hasattr(self, 'scroll_timer') and self.scroll_timer:
            self.scroll_timer.stop()
        
        # 設置定時器在1.5秒後隱藏滾動條
        from PyQt5.QtCore import QTimer
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.hide_scrollbar)
        self.scroll_timer.setSingleShot(True)
        self.scroll_timer.start(1500)  # 1.5秒後隱藏
        
    def hide_scrollbar(self):
        """隱藏滾動條"""
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
    def load_data(self):
        """載入資料到表單"""
        if self.row_data:
            for column, widget in self.form_fields.items():
                value = self.row_data.get(column, "")
                
                if isinstance(widget, QTextEdit):
                    widget.setPlainText(str(value) if value is not None else "")
                elif isinstance(widget, QLineEdit):
                    widget.setText(str(value) if value is not None else "")
    
    def get_form_data(self):
        """獲取表單資料"""
        data = {}
        for column, widget in self.form_fields.items():
            if isinstance(widget, QTextEdit):
                data[column] = widget.toPlainText().strip()
            elif isinstance(widget, QLineEdit):
                data[column] = widget.text().strip()
            else:
                data[column] = ""
        return data

class DataEditDialog(QDialog):
    def __init__(self, parent, table_name, data, columns, original_data=None):
        super().__init__(parent)
        self.table_name = table_name
        self.original_data = original_data or {}
        self.pending_changes = []
        
        self.setWindowTitle(f"Edit Table: {table_name}")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        self.setup_ui()
        self.load_data(data, columns)
        
    def setup_ui(self):
        """設置對話框 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # 標題區域
        title_label = QLabel(f"Editing table: {self.table_name}")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 500;
                color: #333333;
                padding: 8px 0px;
            }
        """)
        layout.addWidget(title_label)
        
        # 工具列
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # 表格區域
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(False)  # 編輯時不允許排序
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        layout.addWidget(self.table_view)
        
        # 狀態列
        self.status_label = QLabel("Ready to edit")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 4px 0px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # 按鈕區域
        button_layout = self.create_button_layout()
        layout.addLayout(button_layout)
        
    def create_toolbar(self):
        """創建工具列"""
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setSpacing(8)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # 新增行按鈕
        self.add_row_btn = QPushButton("Add Row")
        self.add_row_btn.clicked.connect(self.add_row)
        
        # 刪除行按鈕
        self.delete_row_btn = QPushButton("Delete Row")
        self.delete_row_btn.clicked.connect(self.delete_row)
        self.delete_row_btn.setEnabled(False)
        
        # macOS 原生按鈕樣式
        button_style = """
            QPushButton {
                border: 1px solid rgba(0, 0, 0, 0.15);
                border-radius: 5px;
                background: #ffffff;
                color: #1d1d1f;
                font-size: 13px;
                font-weight: 500;
                padding: 6px 16px;
                min-width: 70px;
                min-height: 28px;
            }
            QPushButton:hover:enabled {
                background: #f5f5f7;
                border: 1px solid rgba(0, 0, 0, 0.2);
            }
            QPushButton:pressed:enabled {
                background: #e8e8ea;
                border: 1px solid rgba(0, 0, 0, 0.25);
            }
            QPushButton:disabled {
                border: 1px solid rgba(0, 0, 0, 0.08);
                background: #f9f9f9;
                color: #86868b;
            }
        """
        
        self.add_row_btn.setStyleSheet(button_style)
        self.delete_row_btn.setStyleSheet(button_style)
        
        toolbar_layout.addWidget(self.add_row_btn)
        toolbar_layout.addWidget(self.delete_row_btn)
        toolbar_layout.addStretch()
        
        # 工具列背景
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #f8f8f8;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        
        return toolbar
        
    def create_button_layout(self):
        """創建底部按鈕佈局"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # 取消按鈕
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setMinimumHeight(32)
        
        # 儲存按鈕
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setMinimumHeight(32)
        
        # macOS 原生按鈕樣式
        cancel_style = """
            QPushButton {
                border: 1px solid rgba(0, 0, 0, 0.15);
                border-radius: 5px;
                background: #ffffff;
                color: #1d1d1f;
                font-size: 13px;
                font-weight: 500;
                padding: 8px 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #f5f5f7;
                border: 1px solid rgba(0, 0, 0, 0.2);
            }
            QPushButton:pressed {
                background: #e8e8ea;
                border: 1px solid rgba(0, 0, 0, 0.25);
            }
        """
        
        save_style = """
            QPushButton {
                border: 1px solid #007AFF;
                border-radius: 5px;
                background: #007AFF;
                color: white;
                font-size: 13px;
                font-weight: 600;
                padding: 8px 20px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: #0056CC;
                border: 1px solid #0056CC;
            }
            QPushButton:pressed {
                background: #004299;
                border: 1px solid #004299;
            }
        """
        
        self.cancel_btn.setStyleSheet(cancel_style)
        self.save_btn.setStyleSheet(save_style)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        return button_layout
        
    def load_data(self, data, columns):
        """載入資料到表格"""
        model = QStandardItemModel(len(data), len(columns))
        model.setHorizontalHeaderLabels(columns)
        
        for row_num, row_data in enumerate(data):
            for col_num, cell_data in enumerate(row_data):
                item = QStandardItem(str(cell_data) if cell_data is not None else "")
                model.setItem(row_num, col_num, item)
        
        self.table_view.setModel(model)
        self.table_view.resizeColumnsToContents()
        
        # 連接選擇變更事件
        selection_model = self.table_view.selectionModel()
        if selection_model:
            selection_model.selectionChanged.connect(self.on_selection_changed)
            
    def on_selection_changed(self):
        """處理選擇變更"""
        has_selection = len(self.table_view.selectionModel().selectedRows()) > 0
        self.delete_row_btn.setEnabled(has_selection)
        
    def add_row(self):
        """新增行"""
        model = self.table_view.model()
        if model:
            row_count = model.rowCount()
            model.insertRow(row_count)
            
            # 選中新行
            index = model.index(row_count, 0)
            self.table_view.setCurrentIndex(index)
            self.update_status(f"Added new row {row_count + 1}")
            
    def delete_row(self):
        """刪除選中的行"""
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        reply = QMessageBox.question(self, 'Delete Row', 
                                   f'Are you sure you want to delete {len(selected_rows)} row(s)?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            model = self.table_view.model()
            rows_to_delete = [index.row() for index in selected_rows]
            rows_to_delete.sort(reverse=True)  # 從後面開始刪除
            
            for row in rows_to_delete:
                model.removeRow(row)
                
            self.update_status(f"Deleted {len(rows_to_delete)} row(s)")
            
    def update_status(self, message):
        """更新狀態"""
        self.status_label.setText(message)
        
    def get_changes(self):
        """獲取所有變更"""
        # 這裡可以實作獲取變更的邏輯
        # 目前返回整個表格資料
        model = self.table_view.model()
        if not model:
            return []
            
        changes = []
        for row in range(model.rowCount()):
            row_data = {}
            for col in range(model.columnCount()):
                header = model.horizontalHeaderItem(col).text()
                item = model.item(row, col)
                value = item.text() if item else ""
                row_data[header] = value
            changes.append(row_data)
            
        return changes
