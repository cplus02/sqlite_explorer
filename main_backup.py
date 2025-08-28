
import sys
import os
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QTableView, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QPushButton, QDialog, QTreeWidget, QTreeWidgetItem, QHeaderView, QSplitter, QStackedWidget, QStatusBar, QLabel, QComboBox, QFrame, QListWidgetItem, QToolBar, QAction, QSizePolicy, QMessageBox, QLineEdit, QCheckBox, QScrollArea, QGridLayout
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QColor, QIcon, QSyntaxHighlighter, QTextCharFormat, QPixmap, QPainter, QBrush, QLinearGradient, QPainterPath
from db_handler import DBHandler
from config import ConfigManager
from dialogs import ConnectionsDialog, AddConnectionDialog, RecordEditDialog

class SQLSyntaxHighlighter(QSyntaxHighlighter):
    """簡單的 SQL 語法高亮器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 設置不同類型的格式
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(128, 0, 255))  # 紫色
        self.keyword_format.setFontWeight(QFont.Bold)
        
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(255, 0, 0))  # 紅色
        
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(0, 128, 0))  # 綠色
        self.comment_format.setFontItalic(True)
        
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor(0, 0, 255))  # 藍色
        
        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor(255, 128, 0))  # 橙色
        
        # SQL 關鍵字列表
        self.sql_keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP',
            'ALTER', 'TABLE', 'INDEX', 'VIEW', 'DATABASE', 'SCHEMA', 'PRIMARY', 'KEY',
            'FOREIGN', 'REFERENCES', 'CONSTRAINT', 'UNIQUE', 'NOT', 'NULL', 'DEFAULT',
            'AUTO_INCREMENT', 'AS', 'ALIAS', 'DISTINCT', 'ALL', 'AND', 'OR', 'IN',
            'BETWEEN', 'LIKE', 'IS', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
            'IF', 'ELSEIF', 'WHILE', 'FOR', 'LOOP', 'BEGIN', 'END', 'DELIMITER',
            'ORDER', 'BY', 'ASC', 'DESC', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET',
            'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER', 'CROSS', 'ON', 'USING',
            'UNION', 'INTERSECT', 'EXCEPT', 'WITH', 'RECURSIVE', 'COMMIT', 'ROLLBACK',
            'TRANSACTION', 'START', 'SAVEPOINT', 'RELEASE', 'SET', 'SHOW', 'DESCRIBE',
            'EXPLAIN', 'ANALYZE', 'OPTIMIZE', 'REPAIR', 'CHECK', 'BACKUP', 'RESTORE'
        ]
        
        # SQL 函數列表
        self.sql_functions = [
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'LENGTH', 'SUBSTR', 'UPPER', 'LOWER',
            'TRIM', 'LTRIM', 'RTRIM', 'REPLACE', 'CONCAT', 'ROUND', 'CEIL', 'FLOOR',
            'ABS', 'SQRT', 'POWER', 'MOD', 'NOW', 'CURDATE', 'CURTIME', 'DATE',
            'TIME', 'YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND', 'DATEDIFF',
            'DATEADD', 'FORMAT', 'CAST', 'CONVERT', 'COALESCE', 'NULLIF', 'IFNULL'
        ]
    
    def highlightBlock(self, text):
        """對文本塊進行語法高亮"""
        
        # 高亮 SQL 關鍵字
        for keyword in self.sql_keywords:
            pattern = r'\b' + keyword + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                self.setFormat(match.start(), match.end() - match.start(), self.keyword_format)
        
        # 高亮 SQL 函數
        for function in self.sql_functions:
            pattern = r'\b' + function + r'\s*\('
            for match in re.finditer(pattern, text, re.IGNORECASE):
                self.setFormat(match.start(), len(function), self.function_format)
        
        # 高亮字符串 (單引號)
        string_pattern = r"'[^']*'"
        for match in re.finditer(string_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)
        
        # 高亮字符串 (雙引號)
        string_pattern = r'"[^"]*"'
        for match in re.finditer(string_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)
        
        # 高亮數字
        number_pattern = r'\b\d+\.?\d*\b'
        for match in re.finditer(number_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)
        
        # 高亮註釋 (-- 開頭)
        comment_pattern = r'--.*$'
        for match in re.finditer(comment_pattern, text, re.MULTILINE):
            self.setFormat(match.start(), match.end() - match.start(), self.comment_format)
        
        # 高亮註釋 (/* */ 包圍)
        comment_pattern = r'/\*.*?\*/'
        for match in re.finditer(comment_pattern, text, re.DOTALL):
            self.setFormat(match.start(), match.end() - match.start(), self.comment_format)

class MainWindow(QMainWindow):
    def __init__(self, db_path=None):
        super().__init__()
        self.setWindowTitle("SQLite Explorer")
        self.setMinimumSize(800, 600)
        
        # 設定應用程式圖示（視窗層級）
        import os
        icons_dir = os.path.join(os.path.dirname(__file__), "icons")
        app_icon = QIcon()
        # 添加不同尺寸的圖示
        icon_sizes = [16, 32, 64, 128, 256, 512]
        for size in icon_sizes:
            icon_path = os.path.join(icons_dir, f"AppIcon-{size}.png")
            if os.path.exists(icon_path):
                app_icon.addFile(icon_path, QSize(size, size))
        self.setWindowIcon(app_icon)
        self.db_handler = DBHandler(db_path) if db_path else None
        self.config_manager = ConfigManager()
        self.current_db_path = db_path
        
        # 編輯狀態管理
        self.is_editing = False
        self.current_table_name = None
        self.pending_changes = []  # 存放待提交的變更
        
        # 搜尋延時計時器
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_delayed_search)
        
        # 欄位寬度記錄（像素值）
        self.column_widths = {}
        # 垂直標題寬度記錄
        self.vertical_header_widths = {}
        # 欄位顯示狀態記錄
        self.column_visibility = {}
        # 欄位顯示控制項
        self.column_checkboxes = {}
        
        # 恢復視窗幾何
        self.restore_window_geometry()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # Create sidebar navigation
        self.setup_sidebar()
        
        # Create stacked widget for content
        self.content_stack = QStackedWidget()
        
        # Create content pages
        self.setup_data_page()
        self.setup_query_page()
        
        # Add to splitter
        self.main_splitter.addWidget(self.sidebar_widget)
        self.main_splitter.addWidget(self.content_stack)
        
        # 恢復側邊欄寬度
        self.restore_splitter_sizes()
        
        # 監聽 splitter 變化
        self.main_splitter.splitterMoved.connect(self.on_splitter_moved)
        
        self.main_layout.addWidget(self.main_splitter)
        
        # 添加底部狀態列
        self.setup_status_bar()

        # 延遲載入資料，確保所有組件已初始化
        QTimer.singleShot(100, self.load_last_database)
        
        # 延遲恢復 schema 大小，確保 splitter 已完全建立
        QTimer.singleShot(150, self.restore_schema_sizes)

    def update_toolbar_state(self):
        """更新工具列按鈕狀態"""
        has_table = self.current_table_name is not None
        has_changes = len(self.pending_changes) > 0
        has_selection = False
        
        # 檢查是否有選中的記錄
        if hasattr(self, 'table_view') and self.table_view.selectionModel():
            has_selection = len(self.table_view.selectionModel().selectedRows()) > 0
        
        # 基本功能按鈕
        self.add_row_btn.setEnabled(has_table)
        self.delete_row_btn.setEnabled(has_table and has_selection)
        
        # Commit/Rollback 按鈕
        self.commit_btn.setEnabled(has_changes)
        self.rollback_btn.setEnabled(has_changes)

    def load_last_database(self):
        """載入上次打開的資料庫"""
        last_db = self.config_manager.get_last_database()
        if last_db and os.path.exists(last_db):
            self.connect_to_database(last_db)
        else:
            self.load_tables()

    def open_edit_dialog(self):
        """打開編輯選中記錄的對話框"""
        if not self.current_table_name or not self.db_handler:
            return
            
        # 檢查是否有選中的記錄
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a record to edit.")
            return
        
        try:
            # 獲取表格結構和 schema 信息
            cursor = self.db_handler.connection.cursor()
            cursor.execute(f"SELECT * FROM {self.current_table_name}")
            columns = [description[0] for description in cursor.description]
            
            # 獲取表格 schema
            table_schema = {}
            schema_info = self.db_handler.get_table_schema(self.current_table_name)
            for column_info in schema_info:
                if len(column_info) >= 3:
                    column_name = column_info[1]
                    column_type = column_info[2]
                    table_schema[column_name] = {'type': column_type}
            
            # 獲取選中行的資料
            row_index = selected_rows[0].row()
            model = self.table_view.model()
            row_data = {}
            
            for col in range(model.columnCount()):
                column_name = model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
                item = model.item(row_index, col)
                value = item.text() if item else ""
                row_data[column_name] = value
            
            # 打開編輯對話框
            dialog = RecordEditDialog(self, self.current_table_name, columns, row_data, table_schema)
            
            if dialog.exec_() == dialog.Accepted:
                # 用戶保存了變更，更新到 pending_changes
                form_data = dialog.get_form_data()
                
                # 記錄變更
                self.pending_changes.append({
                    'action': 'update',
                    'row': row_index,
                    'old_data': row_data.copy(),
                    'new_data': form_data.copy()
                })
                
                # 更新表格顯示
                for col, (column_name, new_value) in enumerate(form_data.items()):
                    if column_name in row_data:
                        item = model.item(row_index, col)
                        if item:
                            item.setText(str(new_value))
                
                # 標記修改過的行
                self.highlight_modified_row(row_index)
                
                self.update_toolbar_state()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open edit dialog:\n{str(e)}")

    def on_table_double_clicked(self, index):
        """處理表格雙擊事件來編輯記錄"""
        if not self.current_table_name or not self.db_handler:
            return
        
        if not index.isValid():
            return
            
        try:
            # 獲取表格結構和 schema 信息
            cursor = self.db_handler.connection.cursor()
            cursor.execute(f"SELECT * FROM {self.current_table_name}")
            columns = [description[0] for description in cursor.description]
            
            # 獲取表格 schema
            table_schema = {}
            schema_info = self.db_handler.get_table_schema(self.current_table_name)
            for column_info in schema_info:
                if len(column_info) >= 3:
                    column_name = column_info[1]
                    column_type = column_info[2]
                    table_schema[column_name] = {'type': column_type}
            
            # 獲取雙擊行的資料
            row_index = index.row()
            model = self.table_view.model()
            row_data = {}
            
            for col in range(model.columnCount()):
                column_name = model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
                item = model.item(row_index, col)
                value = item.text() if item else ""
                row_data[column_name] = value
            
            # 打開編輯對話框
            dialog = RecordEditDialog(self, self.current_table_name, columns, row_data, table_schema)
            
            if dialog.exec_() == dialog.Accepted:
                # 用戶保存了變更，更新到 pending_changes
                form_data = dialog.get_form_data()
                
                # 記錄變更
                self.pending_changes.append({
                    'action': 'update',
                    'row': row_index,
                    'old_data': row_data.copy(),
                    'new_data': form_data.copy()
                })
                
                # 更新表格顯示
                for col, (column_name, new_value) in enumerate(form_data.items()):
                    if column_name in row_data:
                        item = model.item(row_index, col)
                        if item:
                            item.setText(str(new_value))
                
                # 標記修改過的行
                self.highlight_modified_row(row_index)
                
                # 更新工具列狀態
                self.update_toolbar_state()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open edit dialog:\n{str(e)}")

    def toggle_edit_mode(self):
        """切換編輯模式"""
        if self.pending_changes:
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, 'Unsaved Changes',
                                       'You have unsaved changes. Do you want to commit them before switching modes?',
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                       QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.commit_changes()
            elif reply == QMessageBox.No:
                self.rollback_changes()
            else:
                # 用戶取消
                return
        
        self.is_editing = not self.is_editing
        self.update_table_edit_mode()
        self.update_toolbar_state()

    def update_table_edit_mode(self):
        """更新表格的編輯模式"""
        if hasattr(self, 'table_view') and self.table_view.model():
            if self.is_editing:
                from PyQt5.QtWidgets import QAbstractItemView
                self.table_view.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
            else:
                from PyQt5.QtWidgets import QAbstractItemView
                self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def add_new_row(self):
        """新增一筆記錄"""
        if not self.current_table_name or not self.db_handler:
            return
            
        try:
            # 獲取表格結構和 schema 信息
            cursor = self.db_handler.connection.cursor()
            cursor.execute(f"SELECT * FROM {self.current_table_name}")
            columns = [description[0] for description in cursor.description]
            
            # 獲取表格 schema
            table_schema = {}
            schema_info = self.db_handler.get_table_schema(self.current_table_name)
            for column_info in schema_info:
                if len(column_info) >= 3:
                    column_name = column_info[1]
                    column_type = column_info[2]
                    table_schema[column_name] = {'type': column_type}
            
            # 打開新增對話框
            dialog = RecordEditDialog(self, self.current_table_name, columns, None, table_schema)
            
            if dialog.exec_() == dialog.Accepted:
                # 用戶保存了新記錄
                form_data = dialog.get_form_data()
                
                # 在表格模型中插入新行
                model = self.table_view.model()
                row_count = model.rowCount()
                model.insertRow(row_count)
                
                # 設置新行的資料
                for col_index, (column_name, value) in enumerate(form_data.items()):
                    item = QStandardItem(str(value))
                    model.setItem(row_count, col_index, item)
                
                # 記錄變更
                self.pending_changes.append({
                    'action': 'insert',
                    'row': row_count,
                    'data': form_data.copy()
                })
                
                # 標記新增的行
                self.highlight_modified_row(row_count)
                
                self.update_toolbar_state()
                
                # 選中新行
                index = model.index(row_count, 0)
                self.table_view.setCurrentIndex(index)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add new record:\n{str(e)}")

    def delete_selected_row(self):
        """刪除選中的行"""
        if not self.current_table_name:
            return
            
        current_index = self.table_view.currentIndex()
        if not current_index.isValid():
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Selection", "Please select a row to delete.")
            return
            
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, 'Delete Row',
                                   'Are you sure you want to delete the selected row?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        if reply == QMessageBox.Yes:
            row = current_index.row()
            model = self.table_view.model()
            
            # 獲取要刪除的行數據
            row_data = {}
            for col in range(model.columnCount()):
                header = model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
                item = model.item(row, col)
                value = item.text() if item else None
                row_data[header] = value
            
            # 記錄變更
            self.pending_changes.append({
                'action': 'delete',
                'row': row,
                'data': row_data
            })
            
            # 從模型中移除行
            model.removeRow(row)
            self.update_toolbar_state()

    def commit_changes(self):
        """提交所有變更到資料庫"""
        if not self.pending_changes or not self.current_table_name:
            return
            
        try:
            # 開始資料庫事務
            cursor = self.db_handler.connection.cursor()
            
            for change in self.pending_changes:
                if change['action'] == 'insert':
                    # 處理插入操作
                    self.execute_insert(cursor, change)
                elif change['action'] == 'delete':
                    # 處理刪除操作
                    self.execute_delete(cursor, change)
                elif change['action'] == 'update':
                    # 處理更新操作
                    self.execute_update(cursor, change)
            
            # 提交事務
            self.db_handler.connection.commit()
            
            # 清空變更記錄
            change_count = len(self.pending_changes)
            self.pending_changes.clear()
            
            # 清除所有背景色標記
            self.clear_all_highlights()
            
            # 重新載入資料
            self.load_table_data(self.current_table_name)
            
            self.update_toolbar_state()
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Success", f"Changes committed successfully!\n{change_count} changes applied.")
            
        except Exception as e:
            # 回滾事務
            self.db_handler.connection.rollback()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Commit Failed", f"Failed to commit changes:\n{str(e)}")

    def rollback_changes(self):
        """回滾所有未提交的變更"""
        if not self.pending_changes:
            return
            
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, 'Rollback Changes',
                                   f'Are you sure you want to discard {len(self.pending_changes)} unsaved changes?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.pending_changes.clear()
            
            # 清除所有背景色標記
            self.clear_all_highlights()
            
            # 重新載入原始資料
            if self.current_table_name:
                self.load_table_data(self.current_table_name)
            
            self.update_toolbar_state()

    def execute_insert(self, cursor, change):
        """執行插入操作"""
        if not self.current_table_name:
            return
            
        # 獲取表格結構，確定所有欄位
        schema = self.db_handler.get_table_schema(self.current_table_name)
        if not schema:
            return
            
        # 從模型獲取新增行的資料
        model = self.table_view.model()
        row = change['row']
        
        columns = []
        values = []
        placeholders = []
        
        # 收集非空的欄位和值
        for col in range(model.columnCount()):
            column_name = model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            item = model.item(row, col)
            value = item.text().strip() if item and item.text() else None
            
            # 只插入非空值，讓 SQLite 處理預設值和 NULL
            if value:
                columns.append(column_name)
                values.append(value)
                placeholders.append('?')
        
        if columns:
            # 構建 INSERT SQL
            sql = f"INSERT INTO {self.current_table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(sql, values)

    def execute_delete(self, cursor, change):
        """執行刪除操作"""
        if not self.current_table_name:
            return
            
        # 獲取要刪除的行數據
        row_data = change['data']
        
        # 構建 WHERE 條件
        where_conditions = []
        where_values = []
        
        # 使用所有非 NULL 欄位作為條件
        for column, value in row_data.items():
            if value is not None and str(value).strip():
                where_conditions.append(f"{column} = ?")
                where_values.append(value)
        
        if where_conditions:
            # 構建 DELETE SQL
            sql = f"DELETE FROM {self.current_table_name} WHERE {' AND '.join(where_conditions)}"
            cursor.execute(sql, where_values)

    def execute_update(self, cursor, change):
        """執行更新操作"""
        if not self.current_table_name:
            return
            
        # 獲取變更的資料
        old_data = change.get('old_data', {})
        new_data = change.get('new_data', {})
        
        if not old_data or not new_data:
            return
            
        # 構建 SET 條件（只更新變更的欄位）
        set_conditions = []
        set_values = []
        
        for column, new_value in new_data.items():
            if column in old_data and old_data[column] != new_value:
                set_conditions.append(f"{column} = ?")
                set_values.append(new_value)
        
        if not set_conditions:
            return  # 沒有變更
            
        # 構建 WHERE 條件（使用原始資料）
        where_conditions = []
        where_values = []
        
        # 使用所有原始欄位作為條件
        for column, value in old_data.items():
            if value is not None and str(value).strip():
                where_conditions.append(f"{column} = ?")
                where_values.append(value)
        
        if where_conditions:
            # 構建 UPDATE SQL
            sql = f"UPDATE {self.current_table_name} SET {', '.join(set_conditions)} WHERE {' AND '.join(where_conditions)}"
            all_values = set_values + where_values
            cursor.execute(sql, all_values)

    def restore_window_geometry(self):
        """恢復視窗幾何"""
        geometry = self.config_manager.get_window_geometry()
        self.resize(geometry['width'], geometry['height'])
        self.move(geometry['x'], geometry['y'])

    def restore_splitter_sizes(self):
        """恢復 splitter 大小"""
        sidebar_width = self.config_manager.get_sidebar_width()
        # 計算內容區域寬度（總寬度減去側邊欄寬度）
        content_width = self.width() - sidebar_width
        self.main_splitter.setSizes([sidebar_width, content_width])

    def restore_schema_sizes(self):
        """恢復 schema splitter 大小"""
        # 恢復 data schema 寬度
        if hasattr(self, 'data_splitter'):
            data_schema_width = self.config_manager.get_data_schema_width()
            # 計算剩餘寬度給 table view
            total_width = self.width() - self.config_manager.get_sidebar_width() - 30  # 減去邊距
            table_width = max(total_width - data_schema_width, 300)  # 至少留 300px 給 table
            self.data_splitter.setSizes([data_schema_width, table_width])
        
        # 恢復 query schema 寬度  
        if hasattr(self, 'query_splitter'):
            query_schema_width = self.config_manager.get_query_schema_width()
            # 計算剩餘寬度給 editor
            total_width = self.width() - self.config_manager.get_sidebar_width() - 30  # 減去邊距
            editor_width = max(total_width - query_schema_width, 300)  # 至少留 300px 給 editor
            self.query_splitter.setSizes([query_schema_width, editor_width])

    def on_splitter_moved(self, pos, index):
        """當 splitter 移動時保存位置"""
        sizes = self.main_splitter.sizes()
        if len(sizes) >= 1:
            sidebar_width = sizes[0]
            self.config_manager.save_sidebar_width(sidebar_width)

    def on_data_splitter_moved(self, pos, index):
        """當 data splitter 移動時保存 schema 寬度"""
        sizes = self.data_splitter.sizes()
        if len(sizes) >= 1:
            schema_width = sizes[0]
            self.config_manager.save_data_schema_width(schema_width)

    def on_query_splitter_moved(self, pos, index):
        """當 query splitter 移動時保存 schema 寬度"""
        sizes = self.query_splitter.sizes()
        if len(sizes) >= 1:
            schema_width = sizes[0]
            self.config_manager.save_query_schema_width(schema_width)

    def on_column_resized(self, logical_index, old_size, new_size):
        """處理欄位寬度調整事件"""
        if not self.current_table_name or not self.current_db_path:
            return
            
        # 標記這個表格的欄位寬度已被手動調整
        table_key = f"{self.current_db_path}::{self.current_table_name}"
        if not hasattr(self, 'manually_resized_tables'):
            self.manually_resized_tables = set()
        self.manually_resized_tables.add(table_key)
        
        # 收集所有欄位的當前寬度
        header = self.table_view.horizontalHeader()
        column_widths = []
        for i in range(header.count()):
            column_widths.append(header.sectionSize(i))
        
        # 保存到配置文件
        self.config_manager.save_column_widths(self.current_db_path, self.current_table_name, column_widths)


    def get_type_color_and_icon(self, data_type):
        """根據資料類型返回顏色和圖示文字"""
        data_type = data_type.upper()

        if 'INT' in data_type:
            return QColor(52, 152, 219), "🔢"  # 藍色，數字圖示
        elif 'TEXT' in data_type or 'CHAR' in data_type or 'VARCHAR' in data_type:
            return QColor(46, 204, 113), "📝"  # 綠色，文字圖示
        elif 'REAL' in data_type or 'FLOAT' in data_type or 'DOUBLE' in data_type:
            return QColor(155, 89, 182), "🔘"  # 紫色，小數圖示
        elif 'BLOB' in data_type:
            return QColor(231, 76, 60), "📦"  # 紅色，二進制圖示
        elif 'DATE' in data_type or 'TIME' in data_type:
            return QColor(243, 156, 18), "🕒"  # 橙色，時間圖示
        elif 'BOOL' in data_type:
            return QColor(26, 188, 156), "✓"   # 青色，勾選圖示
        else:
            return QColor(127, 140, 141), "❓"  # 灰色，問號圖示

    def add_index_status_details(self, parent_item, table_name, index_info):
        """添加索引詳細狀態信息"""
        try:
            # 獲取索引的詳細統計信息
            index_stats = self.get_index_statistics(table_name, index_info['name'])

            # 創建狀態子項目
            status_text = f"📊 Status: {'Active' if index_stats['is_active'] else 'Inactive'}"
            status_item = QTreeWidgetItem([status_text])
            status_item.setData(0, Qt.UserRole, {'type': 'index_status', 'status': index_stats['is_active']})
            if index_stats['is_active']:
                status_item.setForeground(0, QColor(46, 204, 113))  # 綠色
            else:
                status_item.setForeground(0, QColor(231, 76, 60))  # 紅色
            parent_item.addChild(status_item)

            # 顯示欄位詳細信息
            if index_info['columns']:
                columns_text = f"📋 Columns: {len(index_info['columns'])} column(s)"
                columns_item = QTreeWidgetItem([columns_text])
                columns_item.setData(0, Qt.UserRole, {'type': 'index_columns', 'columns': index_info['columns']})
                columns_item.setForeground(0, QColor(149, 165, 166))  # 灰色

                # 添加每個欄位的詳細信息
                for col in index_info['columns']:
                    col_name = col['name']
                    col_seq = col['seqno']
                    col_detail = f"  └─ {col_name} (seq: {col_seq})"
                    col_item = QTreeWidgetItem([col_detail])
                    col_item.setData(0, Qt.UserRole, {'type': 'index_column_detail', 'column': col})
                    col_item.setForeground(0, QColor(189, 195, 199))  # 淺灰色
                    columns_item.addChild(col_item)

                parent_item.addChild(columns_item)

            # 顯示索引統計信息（如果可用）
            if index_stats.get('page_count', 0) > 0:
                stats_text = f"📈 Statistics: {index_stats['page_count']} pages"
                stats_item = QTreeWidgetItem([stats_text])
                stats_item.setData(0, Qt.UserRole, {'type': 'index_stats', 'stats': index_stats})
                stats_item.setForeground(0, QColor(155, 89, 182))  # 紫色
                parent_item.addChild(stats_item)

            # 添加索引類型和屬性信息
            properties_text = f"⚙️ Properties: {self.get_index_properties_text(index_info)}"
            properties_item = QTreeWidgetItem([properties_text])
            properties_item.setData(0, Qt.UserRole, {'type': 'index_properties', 'properties': index_info})
            properties_item.setForeground(0, QColor(52, 152, 219))  # 藍色
            parent_item.addChild(properties_item)

        except Exception as e:
            error_item = QTreeWidgetItem([f"❌ Error loading index details: {str(e)}"])
            error_item.setForeground(0, QColor(231, 76, 60))
            parent_item.addChild(error_item)

    def get_index_properties_text(self, index_info):
        """獲取索引屬性描述文字"""
        properties = []

        if index_info['primary']:
            properties.append("Primary Key")
        if index_info['unique']:
            properties.append("Unique")
        if not index_info['primary'] and not index_info['unique']:
            properties.append("Regular")

        # 添加欄位數量信息
        col_count = len(index_info['columns'])
        properties.append(f"{col_count} column{'s' if col_count != 1 else ''}")

        return ", ".join(properties)

    def get_index_statistics(self, table_name, index_name):
        """獲取索引統計信息"""
        try:
            cursor = self.db_handler.connection.cursor()

            # 檢查索引是否存在且有效
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?", (index_name,))
            exists = cursor.fetchone()
            is_active = exists is not None

            stats = {
                'is_active': is_active,
                'page_count': 0,
                'entry_count': 0
            }

            if is_active:
                # 嘗試獲取索引統計信息
                try:
                    # 獲取索引頁面數量（如果可用）
                    cursor.execute("SELECT * FROM sqlite_stat1 WHERE idx=?", (index_name,))
                    stat_info = cursor.fetchone()
                    if stat_info:
                        # sqlite_stat1 格式: tbl,idx,stat
                        # stat 包含條目數量和頁面信息
                        stat_parts = stat_info[2].split()
                        if stat_parts:
                            stats['entry_count'] = int(stat_parts[0])
                            if len(stat_parts) > 1:
                                stats['page_count'] = int(stat_parts[1])
                except:
                    pass  # sqlite_stat1 可能不存在或不可用

            return stats

        except Exception as e:
            print(f"Error getting index statistics: {e}")
            return {'is_active': False, 'page_count': 0, 'entry_count': 0}

    def setup_sidebar(self):
        """設置側邊欄導航"""
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setMinimumWidth(160)
        self.sidebar_widget.setMaximumWidth(200)
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 15, 0, 5)  # 減少側邊欄底部邊距
        
        # 導航項目列表
        self.nav_list = QListWidget()
        
        # 使用 emoji 圖示確保完美對齊
        self.nav_list.addItem("📊 Data Browser")    # 圖表代表資料瀏覽
        self.nav_list.addItem("🔍 Query Editor")    # 放大鏡代表查詢
        
        # 設置導航樣式
        font = QFont()
        font.setPointSize(12)
        self.nav_list.setFont(font)
        self.nav_list.setCurrentRow(0)  # 預設選擇第一項
        self.nav_list.currentRowChanged.connect(self.on_nav_changed)
        
        # 設置導航項目樣式
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 12px 8px 12px;
                margin: 1px 4px;
                border-radius: 4px;
                font-weight: normal;
                color: #333333;
                min-height: 20px;
            }
            QListWidget::item:selected {
                background-color: #007AFF;
                color: white;
                font-weight: 500;
            }
            QListWidget::item:hover:!selected {
                background-color: rgba(0, 122, 255, 0.1);
            }
        """)
        
        sidebar_layout.addWidget(self.nav_list)
        
        # 添加分隔線
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #d0d0d0; margin: 10px 8px;")
        sidebar_layout.addWidget(separator)
        
        # 添加 Connection 管理區域
        self.setup_connection_area(sidebar_layout)
        
        # 添加底部按鈕（不使用 addStretch，讓 connection_list 自動撐滿）
        connection_buttons = self.setup_connection_buttons()
        sidebar_layout.addWidget(connection_buttons)
        
        # 現在所有UI組件都創建完成，可以載入連接列表
        self.load_connections()
        
        # 設置側邊欄背景
        self.sidebar_widget.setStyleSheet("""
            QWidget {
                background-color: #f7f7f7;
                border-right: 1px solid #d0d0d0;
            }
        """)

    def setup_connection_area(self, sidebar_layout):
        """設置 Connection 管理區域"""
        # Connection 標題
        conn_label = QLabel("CONNECTIONS")
        conn_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 10px;
                font-weight: bold;
                padding: 8px 12px 4px 12px;
            }
        """)
        sidebar_layout.addWidget(conn_label)
        
        # Connection 列表
        self.connection_list = QListWidget()
        self.connection_list.setMinimumHeight(60)
        # 設定 size policy 讓它能擴展
        from PyQt5.QtWidgets import QSizePolicy
        self.connection_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.connection_list.itemClicked.connect(self.on_connection_selected)
        self.connection_list.itemSelectionChanged.connect(self.update_connection_buttons)
        self.connection_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                margin: 2px 8px;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
            QListWidget::item:hover:!selected {
                background-color: rgba(0, 122, 255, 0.1);
            }
        """)
        sidebar_layout.addWidget(self.connection_list, 1)  # stretch factor 1

    def setup_connection_buttons(self):
        """設置 Connection 管理按鈕（在側邊欄底部）"""
        # 按鈕區域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)
        button_layout.setContentsMargins(8, 0, 8, 0)  # 完全移除上下邊距
        
        # 添加連接按鈕
        self.add_conn_btn = QPushButton("+")
        self.add_conn_btn.setFixedSize(32, 32)
        self.add_conn_btn.setToolTip("Add Connection")
        self.add_conn_btn.clicked.connect(self.add_connection)
        
        # 編輯連接按鈕
        self.edit_conn_btn = QPushButton("⚙")  # 使用齒輪圖示，更清楚
        self.edit_conn_btn.setFixedSize(32, 32)
        self.edit_conn_btn.setToolTip("Edit Connection")
        self.edit_conn_btn.clicked.connect(self.edit_connection)
        self.edit_conn_btn.setEnabled(False)  # 預設禁用
        
        # 刪除連接按鈕
        self.delete_conn_btn = QPushButton("×")  # 使用 × 號，更清楚
        self.delete_conn_btn.setFixedSize(32, 32)
        self.delete_conn_btn.setToolTip("Delete Connection")
        self.delete_conn_btn.clicked.connect(self.delete_connection)
        self.delete_conn_btn.setEnabled(False)  # 預設禁用
        
        # macOS 原生按鈕樣式 (圖示按鈕)
        button_style = """
            QPushButton {
                border: 1px solid rgba(0, 0, 0, 0.15);
                border-radius: 6px;
                background: #ffffff;
                color: #1d1d1f;
                font-size: 16px;
                font-weight: 500;
                padding: 2px;
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
        
        self.add_conn_btn.setStyleSheet(button_style)
        self.edit_conn_btn.setStyleSheet(button_style)
        self.delete_conn_btn.setStyleSheet(button_style)
        
        button_layout.addWidget(self.add_conn_btn)
        button_layout.addWidget(self.edit_conn_btn)
        button_layout.addWidget(self.delete_conn_btn)
        
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        return button_widget

    def setup_status_bar(self):
        """設置狀態列"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 當前資料庫路徑標籤
        self.db_path_label = QLabel("No database connected")
        self.db_path_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
                padding: 2px 8px;
            }
        """)
        
        self.status_bar.addWidget(self.db_path_label)
        self.update_status_bar()

    def load_connections(self):
        """載入所有連接到列表"""
        self.connection_list.clear()
        
        # 重新讀取配置以確保同步
        self.config_manager.reload_config()
        connections = self.config_manager.get_all_connections()
        
        if not connections:
            # 顯示無連接狀態
            no_conn_item = QListWidgetItem("No connections")
            no_conn_item.setFlags(Qt.NoItemFlags)  # 不可選擇
            no_conn_item.setForeground(QColor(150, 150, 150))
            self.connection_list.addItem(no_conn_item)
        else:
            for name in connections.keys():
                self.connection_list.addItem(name)
                
            # 如果有當前連接，選中它
            if self.current_db_path:
                for i in range(self.connection_list.count()):
                    item = self.connection_list.item(i)
                    if item:
                        name = item.text()
                        path = self.config_manager.get_connection(name)
                        if path == self.current_db_path:
                            self.connection_list.setCurrentItem(item)
                            break
        
        # 更新按鈕狀態
        self.update_connection_buttons()

    def on_connection_selected(self, item):
        """處理連接選擇"""
        if not item or item.text() == "No connections":
            return
            
        connection_name = item.text()
        db_path = self.config_manager.get_connection(connection_name)
        
        if db_path and db_path != self.current_db_path:
            self.connect_to_database(db_path)
        
        # 更新按鈕狀態
        self.update_connection_buttons()

    def update_connection_buttons(self):
        """更新連接管理按鈕的狀態"""
        # 檢查按鈕是否已經創建
        if not hasattr(self, 'edit_conn_btn') or not hasattr(self, 'delete_conn_btn'):
            return
            
        current_item = self.connection_list.currentItem()
        has_selection = (current_item is not None and 
                        current_item.text() != "No connections" and
                        bool(current_item.flags() & Qt.ItemIsSelectable))
        
        self.edit_conn_btn.setEnabled(has_selection)
        self.delete_conn_btn.setEnabled(has_selection)

    def connect_to_database(self, db_path):
        """連接到指定的資料庫"""
        try:
            # 關閉舊連接
            if self.db_handler:
                self.db_handler.disconnect_database()
            
            # 建立新連接
            self.db_handler = DBHandler(db_path)
            self.current_db_path = db_path
            
            # 保存為上次開啟的資料庫
            self.config_manager.save_last_database(db_path)
            
            # 重新載入資料
            self.load_tables()
            
            # 自動載入第一個表格的內容
            self.auto_load_first_table()
            
            # 更新狀態列
            self.update_status_bar()
            
            # 更新窗口標題
            db_name = os.path.basename(db_path)
            self.setWindowTitle(f"SQLite Explorer - {db_name}")
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to database:\n{str(e)}")

    def auto_load_first_table(self):
        """自動載入第一個表格的內容"""
        if not self.db_handler:
            return
            
        try:
            # 獲取所有表格
            tables = self.db_handler.list_tables()
            if tables:
                # 載入第一個表格的內容
                first_table = tables[0]
                self.load_table_data(first_table)
                
                # 在樹狀結構中選中第一個表格
                if hasattr(self, 'data_schema_tree') and self.data_schema_tree.topLevelItemCount() > 0:
                    first_item = self.data_schema_tree.topLevelItem(0)
                    if first_item:
                        self.data_schema_tree.setCurrentItem(first_item)
                        
        except Exception as e:
            print(f"Error auto-loading first table: {e}")

    def add_connection(self):
        """添加新連接"""
        from dialogs import AddConnectionDialog
        dialog = AddConnectionDialog(self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            # 重新載入連接列表
            self.load_connections()
        else:
            pass

    def edit_connection(self):
        """編輯選中的連接"""
        current_item = self.connection_list.currentItem()
        if not current_item or current_item.text() == "No connections":
            return
            
        connection_name = current_item.text()
        dialog = AddConnectionDialog(self, connection_name=connection_name)
        if dialog.exec_() == QDialog.Accepted:
            self.load_connections()

    def delete_connection(self):
        """刪除選中的連接"""
        current_item = self.connection_list.currentItem()
        if not current_item or current_item.text() == "No connections":
            return
            
        connection_name = current_item.text()
        
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, 
                                   'Delete Connection',
                                   f'Are you sure you want to delete the connection "{connection_name}"?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 如果刪除的是當前連接，先斷開
            db_path = self.config_manager.get_connection(connection_name)
            if db_path == self.current_db_path:
                if self.db_handler:
                    self.db_handler.disconnect_database()
                self.db_handler = None
                self.current_db_path = None
                self.setWindowTitle("SQLite Explorer")
                self.load_tables()  # 清空樹狀結構
                self.update_status_bar()
            
            # 刪除連接
            self.config_manager.remove_connection(connection_name)
            self.load_connections()

    def update_status_bar(self):
        """更新狀態列"""
        if self.current_db_path:
            self.db_path_label.setText(f"Database: {self.current_db_path}")
        else:
            self.db_path_label.setText("No database connected")

    def setup_data_page(self):
        """設置資料瀏覽頁面"""
        data_widget = QWidget()
        data_layout = QVBoxLayout(data_widget)
        data_layout.setSpacing(0)
        data_layout.setContentsMargins(15, 8, 15, 15)
        
        # 建立 splitter 用於調整 schema 寬度
        self.data_splitter = QSplitter(Qt.Horizontal)
        
        # 左側區域包含 schema 樹狀結構和欄位選擇器
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(5)
        left_layout.setContentsMargins(0, 0, 0, 0)
        # 移除固定寬度限制，改用 splitter 控制
        
        # Schema 樹狀結構
        self.data_schema_tree = QTreeWidget()
        self.data_schema_tree.setHeaderLabel("Database Schema")
        self.data_schema_tree.itemClicked.connect(self.on_data_schema_item_clicked)
        
        # 設置樹狀結構樣式
        font = QFont()
        font.setPointSize(10)
        self.data_schema_tree.setFont(font)
        self.data_schema_tree.setAlternatingRowColors(True)
        
        # 移除內部左右間距
        self.data_schema_tree.setStyleSheet("""
            QTreeWidget::item {
                padding-left: 0px;
                padding-right: 0px;
            }
        """)
        
        # 欄位選擇器區域
        self.setup_column_selector()
        
        # 添加到左側佈局
        left_layout.addWidget(self.data_schema_tree, 3)  # 給樹狀結構更多空間
        left_layout.addWidget(self.column_selector_widget, 2)  # 欄位選擇器
        
        # 右側區域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(2)  # 減少垂直間距
        right_layout.setContentsMargins(0, 0, 0, 0)  # 移除右側區域的內邊距
        
        # 工具列
        self.data_toolbar = self.create_data_toolbar()
        right_layout.addWidget(self.data_toolbar)
        
        # 資料顯示區域
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        
        # 移除明確的滾動條策略設定，讓 Qt 使用預設行為
        # 預設情況下 QTableView 的滾動條策略就是 ScrollBarAsNeeded
        
        # 連接雙擊事件來觸發編輯
        self.table_view.doubleClicked.connect(self.on_table_double_clicked)
        
        # 連接欄位寬度變化事件
        self.table_view.horizontalHeader().sectionResized.connect(self.on_column_resized)
        
        # 設置等寬字型
        monospace_font = QFont("Monaco", 11)  # macOS 上的等寬字型
        if not monospace_font.exactMatch():
            monospace_font = QFont("Menlo", 11)  # macOS 備選等寬字型
            if not monospace_font.exactMatch():
                monospace_font = QFont("Courier New", 11)  # 跨平台等寬字型
        self.table_view.setFont(monospace_font)
        right_layout.addWidget(self.table_view)
        
        # 添加到 splitter
        self.data_splitter.addWidget(left_widget)
        self.data_splitter.addWidget(right_widget)
        
        # 設置初始大小比例（左側 schema：右側 table = 1:3）
        self.data_splitter.setStretchFactor(0, 1)
        self.data_splitter.setStretchFactor(1, 3)
        
        # 監聽 data splitter 變化
        self.data_splitter.splitterMoved.connect(self.on_data_splitter_moved)
        
        # 添加到佈局
        data_layout.addWidget(self.data_splitter)
        
        self.content_stack.addWidget(data_widget)

    def setup_column_selector(self):
        """設置欄位選擇器"""
        self.column_selector_widget = QWidget()
        selector_layout = QVBoxLayout(self.column_selector_widget)
        selector_layout.setSpacing(0)
        selector_layout.setContentsMargins(0, 0, 0, 0)
        
        # 使用 QTreeWidget 來保持與 Database Schema 一致的外觀
        self.column_tree = QTreeWidget()
        self.column_tree.setHeaderLabel("Column Visibility")
        self.column_tree.setRootIsDecorated(False)  # 不顯示展開箭頭
        self.column_tree.setIndentation(0)  # 移除縮進
        
        # 設置與 schema 樹狀結構相同的字體和樣式
        font = QFont()
        font.setPointSize(10)
        self.column_tree.setFont(font)
        self.column_tree.setAlternatingRowColors(True)
        
        # 移除內部左右間距，與 schema 樹保持一致
        self.column_tree.setStyleSheet("""
            QTreeWidget::item {
                padding-left: 0px;
                padding-right: 0px;
            }
        """)
        
        # 創建控制按鈕的工具列區域
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(4, 2, 4, 2)
        toolbar_layout.setSpacing(4)
        
        # 復原按鈕
        self.reset_columns_btn = QPushButton("↻")
        self.reset_columns_btn.setFixedSize(20, 20)
        self.reset_columns_btn.setToolTip("Reset to Default")
        self.reset_columns_btn.clicked.connect(self.reset_column_visibility)
        
        # macOS 原生風格的小按鈕樣式
        button_style = """
            QPushButton {
                border: 1px solid rgba(0, 0, 0, 0.12);
                border-radius: 3px;
                background: #ffffff;
                color: #333333;
                font-size: 9px;
                font-weight: 500;
                padding: 1px 2px;
            }
            QPushButton:hover:enabled {
                background: #f0f0f0;
                border: 1px solid rgba(0, 0, 0, 0.18);
            }
            QPushButton:pressed:enabled {
                background: #e0e0e0;
                border: 1px solid rgba(0, 0, 0, 0.25);
            }
            QPushButton:disabled {
                border: 1px solid rgba(0, 0, 0, 0.06);
                background: #f8f8f8;
                color: #999999;
            }
        """
        
        self.reset_columns_btn.setStyleSheet(button_style)
        
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.reset_columns_btn)
        
        # 添加到主佈局
        selector_layout.addWidget(self.column_tree)
        selector_layout.addWidget(toolbar_widget)
        
        # 預設隱藏（沒有表格時）
        self.column_selector_widget.hide()

    def create_data_toolbar(self):
        """創建資料編輯工具列"""
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setSpacing(8)
        toolbar_layout.setContentsMargins(0, 0, 0, 4)  # 只保留下邊距
        
        # 新增記錄按鈕
        self.add_row_btn = QPushButton("Add")
        self.add_row_btn.clicked.connect(self.add_new_row)
        self.add_row_btn.setEnabled(False)
        self.add_row_btn.setMinimumHeight(28)
        
        # 刪除記錄按鈕
        self.delete_row_btn = QPushButton("Delete")
        self.delete_row_btn.clicked.connect(self.delete_selected_row)
        self.delete_row_btn.setEnabled(False)
        self.delete_row_btn.setMinimumHeight(28)
        
        
        # Commit 按鈕
        self.commit_btn = QPushButton("Commit")
        self.commit_btn.clicked.connect(self.commit_changes)
        self.commit_btn.setEnabled(False)
        self.commit_btn.setMinimumHeight(28)
        
        # Rollback 按鈕
        self.rollback_btn = QPushButton("Rollback")
        self.rollback_btn.clicked.connect(self.rollback_changes)
        self.rollback_btn.setEnabled(False)
        self.rollback_btn.setMinimumHeight(28)
        
        # macOS 風格按鈕樣式
        # 普通按鈕樣式
        normal_button_style = """
            QPushButton {
                border: 1px solid rgba(0, 0, 0, 0.15);
                border-radius: 5px;
                background: #ffffff;
                color: #1d1d1f;
                font-size: 13px;
                font-weight: 500;
                padding: 6px 16px;
                min-width: 70px;
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
        
        
        # Primary 按鈕樣式（Commit）
        primary_button_style = """
            QPushButton {
                border: 1px solid #007AFF;
                border-radius: 5px;
                background: #007AFF;
                color: white;
                font-size: 13px;
                font-weight: 600;
                padding: 6px 16px;
                min-width: 70px;
            }
            QPushButton:hover:enabled {
                background: #0056CC;
                border: 1px solid #0056CC;
            }
            QPushButton:pressed:enabled {
                background: #004299;
                border: 1px solid #004299;
            }
            QPushButton:disabled {
                border: 1px solid rgba(0, 0, 0, 0.08);
                background: #f9f9f9;
                color: #86868b;
            }
        """
        
        # Secondary 按鈕樣式（Rollback）
        secondary_button_style = """
            QPushButton {
                border: 1px solid #FF3B30;
                border-radius: 5px;
                background: #ffffff;
                color: #FF3B30;
                font-size: 13px;
                font-weight: 500;
                padding: 6px 16px;
                min-width: 70px;
            }
            QPushButton:hover:enabled {
                background: #fff0f0;
                border: 1px solid #FF3B30;
            }
            QPushButton:pressed:enabled {
                background: #ffe0e0;
                border: 1px solid #FF3B30;
            }
            QPushButton:disabled {
                border: 1px solid rgba(0, 0, 0, 0.08);
                background: #f9f9f9;
                color: #86868b;
            }
        """
        
        # 應用樣式
        self.add_row_btn.setStyleSheet(normal_button_style)
        self.delete_row_btn.setStyleSheet(normal_button_style)
        self.commit_btn.setStyleSheet(primary_button_style)
        self.rollback_btn.setStyleSheet(secondary_button_style)
        
        # 添加到佈局
        toolbar_layout.addWidget(self.add_row_btn)
        toolbar_layout.addWidget(self.delete_row_btn)
        toolbar_layout.addSpacing(16)
        toolbar_layout.addWidget(self.commit_btn)
        toolbar_layout.addWidget(self.rollback_btn)
        toolbar_layout.addStretch()
        
        # 搜尋功能
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: #666666; font-size: 12px;")
        toolbar_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in text fields...")
        self.search_input.setMinimumWidth(200)
        self.search_input.setMaximumWidth(250)
        self.search_input.setMinimumHeight(26)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid rgba(0, 0, 0, 0.15);
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #007AFF;
            }
        """)
        toolbar_layout.addWidget(self.search_input)
        
        # 工具列無背景色
        toolbar_widget.setStyleSheet("")
        
        return toolbar_widget

    def on_search_text_changed(self, text):
        """處理搜尋文字變更，加入延時機制"""
        # 每次文字變更時，先停止之前的計時器
        self.search_timer.stop()
        
        # 儲存搜尋文字
        self.pending_search_text = text.strip()
        
        # 無論輸入或刪除都使用延時機制
        if len(self.pending_search_text) >= 3:
            # 0.5秒後執行搜尋
            self.search_timer.start(500)
        else:
            # 如果少於3個字元，也延時後恢復原始資料
            self.search_timer.start(500)
    
    def perform_delayed_search(self):
        """延時計時器觸發的搜尋執行"""
        if hasattr(self, 'pending_search_text'):
            if len(self.pending_search_text) >= 3:
                self.perform_search(self.pending_search_text)
            else:
                # 如果少於3個字元，恢復原始資料
                if self.current_table_name:
                    self.load_table_data(self.current_table_name)

    def perform_search(self, search_text):
        """執行搜尋功能"""
        if not self.current_table_name or not self.db_handler:
            return
            
        try:
            # 獲取表格結構，找出 TEXT 和 VARCHAR 欄位
            schema_info = self.db_handler.get_table_schema(self.current_table_name)
            text_columns = []
            
            for column_info in schema_info:
                if len(column_info) >= 3:
                    column_name = column_info[1]
                    column_type = column_info[2].upper()
                    if 'TEXT' in column_type or 'VARCHAR' in column_type or 'CHAR' in column_type:
                        text_columns.append(column_name)
            
            if not text_columns:
                # 沒有文字欄位可搜尋
                return
                
            # 建立搜尋查詢
            cursor = self.db_handler.connection.cursor()
            
            # 構建 WHERE 條件，搜尋所有文字欄位
            where_conditions = []
            search_params = []
            
            for column in text_columns:
                where_conditions.append(f"{column} LIKE ?")
                search_params.append(f"%{search_text}%")
            
            # 組合查詢
            where_clause = " OR ".join(where_conditions)
            query = f"SELECT * FROM {self.current_table_name} WHERE {where_clause}"
            
            cursor.execute(query, search_params)
            data = cursor.fetchall()
            
            # 獲取欄位名稱
            columns = [description[0] for description in cursor.description]
            
            # 顯示搜尋結果 - 只更新資料模型，不調整欄位寬度
            if data is not None and columns is not None:
                self.update_table_model_only(data, columns)
                
                # 更新狀態列顯示搜尋結果數量
                result_count = len(data)
                if hasattr(self, 'status_bar'):
                    self.db_path_label.setText(f"Database: {self.current_db_path} | Search results: {result_count} rows")
                    
        except Exception as e:
            print(f"Search error: {e}")
            # 發生錯誤時恢復原始資料
            if self.current_table_name:
                self.load_table_data(self.current_table_name)

    def setup_query_page(self):
        """設置查詢編輯器頁面"""
        query_widget = QWidget()
        query_layout = QVBoxLayout(query_widget)
        query_layout.setSpacing(0)
        query_layout.setContentsMargins(15, 8, 15, 15)
        
        # 建立 splitter 用於調整 schema 寬度
        self.query_splitter = QSplitter(Qt.Horizontal)
        
        # 左側 schema 樹狀結構
        self.query_schema_tree = QTreeWidget()
        self.query_schema_tree.setHeaderLabel("Database Schema")
        self.query_schema_tree.itemDoubleClicked.connect(self.on_query_schema_item_double_clicked)
        # 移除固定寬度限制，改用 splitter 控制
        
        # 設置樹狀結構樣式
        font = QFont()
        font.setPointSize(10)
        self.query_schema_tree.setFont(font)
        self.query_schema_tree.setAlternatingRowColors(True)
        
        # 移除內部左右間距
        self.query_schema_tree.setStyleSheet("""
            QTreeWidget::item {
                padding-left: 0px;
                padding-right: 0px;
            }
        """)
        
        # 右側編輯和結果區域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        
        # SQL 編輯器區域
        self.query_editor = QTextEdit()
        self.query_editor.setPlaceholderText("Enter your SQL query here...\nTip: Double-click table names in the sidebar to insert them into your query.")
        self.query_editor.setMinimumHeight(150)
        
        # 設置編輯器字體
        font = QFont("Monaco", 12)  # macOS 上的等寬字體
        if not font.exactMatch():
            font = QFont("Courier New", 11)
        self.query_editor.setFont(font)
        
        # 設置 SQL 語法高亮
        self.sql_highlighter = SQLSyntaxHighlighter(self.query_editor.document())
        
        # 執行按鈕
        button_layout = QHBoxLayout()
        self.execute_button = QPushButton("Execute SQL")
        self.execute_button.clicked.connect(self.execute_sql)
        self.execute_button.setMinimumHeight(35)
        
        # 設置 macOS 風格樣式 (Primary 按鈕)
        execute_button_style = """
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
            QPushButton:hover:enabled {
                background: #0056CC;
                border: 1px solid #0056CC;
            }
            QPushButton:pressed:enabled {
                background: #004299;
                border: 1px solid #004299;
            }
            QPushButton:disabled {
                border: 1px solid rgba(0, 0, 0, 0.08);
                background: #f9f9f9;
                color: #86868b;
            }
        """
        self.execute_button.setStyleSheet(execute_button_style)
        
        button_layout.addStretch()
        button_layout.addWidget(self.execute_button)
        
        # 結果顯示區域
        self.query_result_view = QTableView()
        self.query_result_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.query_result_view.setAlternatingRowColors(True)
        self.query_result_view.setSortingEnabled(True)
        
        # 移除明確的滾動條策略設定，讓 Qt 使用預設行為
        
        # 設置等寬字型（與主要資料表格一致）
        query_monospace_font = QFont("Monaco", 11)  # macOS 上的等寬字型
        if not query_monospace_font.exactMatch():
            query_monospace_font = QFont("Menlo", 11)  # macOS 備選等寬字型
            if not query_monospace_font.exactMatch():
                query_monospace_font = QFont("Courier New", 11)  # 跨平台等寬字型
        self.query_result_view.setFont(query_monospace_font)
        
        right_layout.addWidget(self.query_editor)
        right_layout.addLayout(button_layout)
        right_layout.addWidget(self.query_result_view)
        
        # 添加到 splitter
        self.query_splitter.addWidget(self.query_schema_tree)
        self.query_splitter.addWidget(right_widget)
        
        # 設置初始大小比例（左側 schema：右側 editor = 1:3）
        self.query_splitter.setStretchFactor(0, 1)
        self.query_splitter.setStretchFactor(1, 3)
        
        # 監聽 query splitter 變化
        self.query_splitter.splitterMoved.connect(self.on_query_splitter_moved)
        
        # 添加到佈局
        query_layout.addWidget(self.query_splitter)
        
        self.content_stack.addWidget(query_widget)

    def on_nav_changed(self, index):
        """處理導航切換"""
        self.content_stack.setCurrentIndex(index)

    def load_tables(self):
        # Load schema trees for both tabs
        if self.db_handler:
            self.load_data_schema_tree()
            self.load_query_schema_tree()
        else:
            # 清空樹狀結構
            if hasattr(self, 'data_schema_tree'):
                self.data_schema_tree.clear()
            if hasattr(self, 'query_schema_tree'):
                self.query_schema_tree.clear()

    def load_data_schema_tree(self):
        """載入資料庫 schema 到 Data tab 的樹狀結構"""
        self.data_schema_tree.clear()

        if not self.db_handler:
            # 顯示無連接狀態
            no_conn_item = QTreeWidgetItem(["No database connected"])
            no_conn_item.setForeground(0, QColor(150, 150, 150))
            self.data_schema_tree.addTopLevelItem(no_conn_item)
            return

        tables = self.db_handler.list_tables()

        for table_name in tables:
            # 創建表格節點
            table_item = QTreeWidgetItem([f"📋 {table_name}"])
            table_item.setData(0, Qt.UserRole, {'type': 'table', 'name': table_name})
            table_item.setForeground(0, QColor(44, 62, 80))  # 深灰色表格名稱

            # 獲取表格結構資訊
            try:
                columns_info = self.db_handler.get_table_schema(table_name)
                if columns_info:
                    for column in columns_info:
                        column_name = column[1] if len(column) > 1 else str(column[0])
                        column_type = column[2] if len(column) > 2 else ""

                        # 獲取類型對應的顏色和圖示
                        color, icon = self.get_type_color_and_icon(column_type)

                        # 建立欄位顯示文字
                        column_text = f"{icon} {column_name}" if column_type else f"❓ {column_name}"
                        if column_type:
                            column_text += f" ({column_type})"

                        column_item = QTreeWidgetItem([column_text])
                        column_item.setData(0, Qt.UserRole, {
                            'type': 'column',
                            'table': table_name,
                            'name': column_name,
                            'data_type': column_type
                        })
                        column_item.setForeground(0, color)
                        table_item.addChild(column_item)

                # 獲取並顯示索引資訊
                try:
                    indexes_info = self.db_handler.get_table_indexes(table_name)
                    if indexes_info:
                        # 創建索引父節點
                        indexes_parent = QTreeWidgetItem(["🔗 Indexes"])
                        indexes_parent.setData(0, Qt.UserRole, {'type': 'indexes_group', 'table': table_name})
                        indexes_parent.setForeground(0, QColor(52, 73, 94))  # 深藍色

                        for index_info in indexes_info:
                            index_name = index_info['name']
                            is_unique = index_info['unique']
                            is_primary = index_info['primary']
                            columns = index_info['columns']

                            # 建立索引顯示文字
                            index_icon = "🔑" if is_primary else ("🔒" if is_unique else "🔗")
                            index_text = f"{index_icon} {index_name}"

                            # 添加索引類型信息
                            type_info = []
                            if is_primary:
                                type_info.append("PRIMARY")
                            if is_unique:
                                type_info.append("UNIQUE")

                            if type_info:
                                index_text += f" ({', '.join(type_info)})"

                            # 添加欄位信息
                            if columns:
                                column_names = [col['name'] for col in columns]
                                index_text += f" on ({', '.join(column_names)})"

                            index_item = QTreeWidgetItem([index_text])
                            index_item.setData(0, Qt.UserRole, {
                                'type': 'index',
                                'table': table_name,
                                'name': index_name,
                                'unique': is_unique,
                                'primary': is_primary,
                                'columns': columns
                             })

                             # 根據索引類型設置顏色
                             if is_primary:
                                 index_item.setForeground(0, QColor(52, 152, 219))  # 藍色
                             elif is_unique:
                                 index_item.setForeground(0, QColor(155, 89, 182))  # 紫色
                             else:
                                 index_item.setForeground(0, QColor(46, 204, 113))  # 綠色

                             # 添加索引詳細狀態信息
                             self.add_index_status_details(index_item, table_name, index_info)
                             indexes_parent.addChild(index_item)

                        table_item.addChild(indexes_parent)

                except Exception as e:
                    error_item = QTreeWidgetItem([f"❌ Error loading indexes: {str(e)}"])
                    error_item.setForeground(0, QColor(231, 76, 60))
                    table_item.addChild(error_item)

            except Exception as e:
                error_item = QTreeWidgetItem([f"❌ Error loading columns: {str(e)}"])
                error_item.setForeground(0, QColor(231, 76, 60))
                table_item.addChild(error_item)

            self.data_schema_tree.addTopLevelItem(table_item)

        # 展開所有項目
        self.data_schema_tree.expandAll()

    def load_query_schema_tree(self):
        """載入資料庫 schema 到 Query tab 的樹狀結構"""
        self.query_schema_tree.clear()
        
        if not self.db_handler:
            # 顯示無連接狀態
            no_conn_item = QTreeWidgetItem(["No database connected"])
            no_conn_item.setForeground(0, QColor(150, 150, 150))
            self.query_schema_tree.addTopLevelItem(no_conn_item)
            return
            
        tables = self.db_handler.list_tables()
        
        for table_name in tables:
            # 創建表格節點
            table_item = QTreeWidgetItem([f"📋 {table_name}"])
            table_item.setData(0, Qt.UserRole, {'type': 'table', 'name': table_name})
            table_item.setForeground(0, QColor(44, 62, 80))  # 深灰色表格名稱
            
            # 獲取表格結構資訊
            try:
                columns_info = self.db_handler.get_table_schema(table_name)
                if columns_info:
                    for column in columns_info:
                        column_name = column[1] if len(column) > 1 else str(column[0])
                        column_type = column[2] if len(column) > 2 else ""
                        
                        # 獲取類型對應的顏色和圖示
                        color, icon = self.get_type_color_and_icon(column_type)
                        
                        # 建立欄位顯示文字
                        column_text = f"{icon} {column_name}" if column_type else f"❓ {column_name}"
                        if column_type:
                            column_text += f" ({column_type})"
                        
                        column_item = QTreeWidgetItem([column_text])
                        column_item.setData(0, Qt.UserRole, {
                            'type': 'column', 
                            'table': table_name, 
                            'name': column_name,
                            'data_type': column_type
                        })
                        column_item.setForeground(0, color)
                        table_item.addChild(column_item)

                # 獲取並顯示索引資訊
                try:
                    indexes_info = self.db_handler.get_table_indexes(table_name)
                    if indexes_info:
                        # 創建索引父節點
                        indexes_parent = QTreeWidgetItem(["🔗 Indexes"])
                        indexes_parent.setData(0, Qt.UserRole, {'type': 'indexes_group', 'table': table_name})
                        indexes_parent.setForeground(0, QColor(52, 73, 94))  # 深藍色

                        for index_info in indexes_info:
                            index_name = index_info['name']
                            is_unique = index_info['unique']
                            is_primary = index_info['primary']
                            columns = index_info['columns']

                            # 建立索引顯示文字
                            index_icon = "🔑" if is_primary else ("🔒" if is_unique else "🔗")
                            index_text = f"{index_icon} {index_name}"

                            # 添加索引類型信息
                            type_info = []
                            if is_primary:
                                type_info.append("PRIMARY")
                            if is_unique:
                                type_info.append("UNIQUE")

                            if type_info:
                                index_text += f" ({', '.join(type_info)})"

                            # 添加欄位信息
                            if columns:
                                column_names = [col['name'] for col in columns]
                                index_text += f" on ({', '.join(column_names)})"

                            index_item = QTreeWidgetItem([index_text])
                            index_item.setData(0, Qt.UserRole, {
                                'type': 'index',
                                'table': table_name,
                                'name': index_name,
                                'unique': is_unique,
                                'primary': is_primary,
                                'columns': columns
                            })

                             # 根據索引類型設置顏色
                             if is_primary:
                                 index_item.setForeground(0, QColor(52, 152, 219))  # 藍色
                             elif is_unique:
                                 index_item.setForeground(0, QColor(155, 89, 182))  # 紫色
                             else:
                                 index_item.setForeground(0, QColor(46, 204, 113))  # 綠色

                             # 添加索引詳細狀態信息
                             self.add_index_status_details(index_item, table_name, index_info)
                             indexes_parent.addChild(index_item)

                        table_item.addChild(indexes_parent)

                except Exception as e:
                    error_item = QTreeWidgetItem([f"❌ Error loading indexes: {str(e)}"])
                    error_item.setForeground(0, QColor(231, 76, 60))
                    table_item.addChild(error_item)

            except Exception as e:
                error_item = QTreeWidgetItem([f"❌ Error loading columns: {str(e)}"])
                error_item.setForeground(0, QColor(231, 76, 60))
                table_item.addChild(error_item)

            self.query_schema_tree.addTopLevelItem(table_item)
        
        # 展開所有項目
        self.query_schema_tree.expandAll()

    def on_data_schema_item_clicked(self, item):
        """處理 Data tab 樹狀結構項目點擊"""
        data = item.data(0, Qt.UserRole)
        if data and data.get('type') == 'table':
            # 清空搜尋框
            if hasattr(self, 'search_input'):
                self.search_input.blockSignals(True)
                self.search_input.clear()
                self.search_input.blockSignals(False)
            
            # 如果點擊的是表格，載入該表格資料
            table_name = data.get('name')
            self.load_table_data(table_name)

    def on_query_schema_item_double_clicked(self, item):
        """處理 Query tab 樹狀結構項目雙擊 - 插入到 SQL 編輯器"""
        data = item.data(0, Qt.UserRole)
        if not data:
            return
            
        cursor = self.query_editor.textCursor()
        
        if data.get('type') == 'table':
            # 如果雙擊表格，插入表格名稱
            table_name = data.get('name')
            cursor.insertText(table_name)
        elif data.get('type') == 'column':
            # 如果雙擊欄位，插入欄位名稱
            column_name = data.get('name')
            cursor.insertText(column_name)
        
        self.query_editor.setTextCursor(cursor)
        self.query_editor.setFocus()

    def load_table_data(self, table_name):
        """載入指定表格的資料"""
        if not self.db_handler:
            return
            
        # 停止搜尋計時器
        self.search_timer.stop()
            
        try:
            # 直接查詢表格資料，不包含 ROWID
            cursor = self.db_handler.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            
            # 獲取欄位名稱
            columns = [description[0] for description in cursor.description]
            
            if data is not None and columns is not None:
                # 檢查是否是同一個表格（從搜尋恢復）還是新表格
                is_same_table = (self.current_table_name == table_name)
                self.current_table_name = table_name
                
                # 更新欄位選擇器
                self.update_column_selector(table_name, columns)
                
                if is_same_table and table_name in self.column_widths:
                    # 同一個表格且已有寬度記錄，只更新資料模型
                    self.update_table_model_only(data, columns)
                else:
                    # 新表格或首次載入，計算寬度分配
                    self.display_data_in_table_view(data, columns, self.table_view)
                
                # 應用欄位顯示設定
                self.apply_column_visibility()
                
                self.update_toolbar_state()
                # 重置狀態列（清除搜尋結果顯示）
                self.update_status_bar()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to load table data:\n{str(e)}")
            print(f"Error loading table data: {e}")

    def execute_sql(self):
        query = self.query_editor.toPlainText()
        if not query:
            return

        results = self.db_handler.execute_query(query)
        if results:
            columns = results[0]
            data = results[1:]
            self.display_data_in_table_view(data, columns, self.query_result_view)

    def display_data_in_table_view(self, data, columns, table_view):
        """在指定的 table view 中顯示資料"""
        model = QStandardItemModel(len(data), len(columns))
        model.setHorizontalHeaderLabels(columns)

        for row_num, row_data in enumerate(data):
            for col_num, cell_data in enumerate(row_data):
                item = QStandardItem(str(cell_data) if cell_data is not None else "")
                model.setItem(row_num, col_num, item)
        
        table_view.setModel(model)
        
        # 如果是主要的資料瀏覽表格，添加變更追蹤和選擇監聽
        if table_view == self.table_view:
            # 連接資料變更信號
            model.dataChanged.connect(self.on_data_changed)
            # 連接選擇變更信號
            selection_model = table_view.selectionModel()
            if selection_model:
                selection_model.selectionChanged.connect(self.on_selection_changed)
            # 儲存原始資料以便比較變更
            self.original_data = {}
            if data:
                for row_num, row_data in enumerate(data):
                    row_dict = {}
                    for col_num, cell_data in enumerate(row_data):
                        row_dict[columns[col_num]] = cell_data
                    self.original_data[row_num] = row_dict
        
        # 處理欄位寬度分配
        self.apply_column_width_settings(table_view, columns)
    
    def apply_column_width_settings(self, table_view, columns):
        """根據表格和欄位來應用或計算寬度設定"""
        if table_view != self.table_view:
            # 如果不是主要的資料瀏覽表格，使用預設行為
            table_view.resizeColumnsToContents()
            header = table_view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Interactive)
            return
        
        header = table_view.horizontalHeader()
        
        # 優先檢查配置文件中的欄位寬度設定
        if self.current_db_path and self.current_table_name:
            saved_widths = self.config_manager.get_column_widths(self.current_db_path, self.current_table_name)
            if saved_widths and len(saved_widths) == len(columns):
                # 使用配置文件中保存的寬度
                self.apply_config_column_widths(table_view, saved_widths)
                return
        
        # 如果沒有配置文件中的設定，檢查內存中的記錄
        table_key = self.current_table_name if self.current_table_name else "default"
        if table_key in self.column_widths:
            # 使用已記錄的寬度
            self.apply_saved_column_widths(table_view, table_key)
        else:
            # 第一次載入此表格，計算並記錄寬度
            self.calculate_and_save_column_widths(table_view, table_key, columns)
    
    def calculate_and_save_column_widths(self, table_view, table_key, columns):
        """計算並保存欄位寬度（像素值）"""
        # 先應用欄位顯示設定
        self.apply_column_visibility()
        
        # 然後根據可見欄位內容調整寬度
        table_view.resizeColumnsToContents()
        
        header = table_view.horizontalHeader()
        
        if header.count() > 0:
            # 記錄每個欄位的實際像素寬度（包括隱藏的欄位）
            column_widths = []
            for i in range(header.count()):
                current_width = header.sectionSize(i)
                column_widths.append(current_width)
            
            # 保存此表格的欄位寬度
            self.column_widths[table_key] = column_widths
        
        # 記錄垂直標題（列號區域）的寬度
        vertical_header = table_view.verticalHeader()
        if vertical_header:
            # 讓垂直標題根據內容調整寬度
            vertical_header.resizeSections(QHeaderView.ResizeToContents)
            # 記錄當前寬度
            self.vertical_header_widths[table_key] = vertical_header.width()
        
        # 設置為互動模式，允許用戶調整
        header.setSectionResizeMode(QHeaderView.Interactive)
    
    def apply_saved_column_widths(self, table_view, table_key):
        """應用已保存的欄位寬度（像素值）"""
        header = table_view.horizontalHeader()
        saved_widths = self.column_widths[table_key]
        
        if header.count() > 0 and len(saved_widths) == header.count():
            # 直接設置每個欄位的固定寬度
            for i, width in enumerate(saved_widths):
                header.resizeSection(i, width)
        
        # 應用欄位顯示設定
        self.apply_column_visibility()
        
        # 應用保存的垂直標題寬度
        if table_key in self.vertical_header_widths:
            vertical_header = table_view.verticalHeader()
            if vertical_header:
                saved_width = self.vertical_header_widths[table_key]
                vertical_header.setFixedWidth(saved_width)
        
        # 設置為互動模式，允許用戶調整
        header.setSectionResizeMode(QHeaderView.Interactive)
    
    def apply_config_column_widths(self, table_view, saved_widths):
        """應用配置文件中保存的欄位寬度"""
        header = table_view.horizontalHeader()
        
        # 應用欄位顯示設定
        self.apply_column_visibility()
        
        # 設置欄位寬度
        for i, width in enumerate(saved_widths):
            if i < header.count():
                header.resizeSection(i, width)
        
        # 設置為互動模式，允許用戶調整
        header.setSectionResizeMode(QHeaderView.Interactive)
    
    def update_table_model_only(self, data, columns):
        """只更新表格資料模型，不調整欄位寬度（用於搜尋結果）"""
        model = QStandardItemModel(len(data), len(columns))
        model.setHorizontalHeaderLabels(columns)

        for row_num, row_data in enumerate(data):
            for col_num, cell_data in enumerate(row_data):
                item = QStandardItem(str(cell_data) if cell_data is not None else "")
                model.setItem(row_num, col_num, item)
        
        # 只設置資料模型，不觸發任何寬度調整
        self.table_view.setModel(model)
        
        # 重新連接信號（因為模型變更了）
        model.dataChanged.connect(self.on_data_changed)
        selection_model = self.table_view.selectionModel()
        if selection_model:
            selection_model.selectionChanged.connect(self.on_selection_changed)
        
        # 應用欄位顯示設定
        self.apply_column_visibility()
        
        # 保持用戶調整的欄位寬度（搜尋時不改變寬度）
        if self.current_db_path and self.current_table_name:
            saved_widths = self.config_manager.get_column_widths(self.current_db_path, self.current_table_name)
            if saved_widths and len(saved_widths) == len(columns):
                header = self.table_view.horizontalHeader()
                for i, width in enumerate(saved_widths):
                    if i < header.count():
                        header.resizeSection(i, width)
        
        # 保持垂直標題寬度不變（搜尋時）
        table_key = self.current_table_name if self.current_table_name else "default"
        if table_key in self.vertical_header_widths:
            vertical_header = self.table_view.verticalHeader()
            if vertical_header:
                saved_width = self.vertical_header_widths[table_key]
                vertical_header.setFixedWidth(saved_width)

    def on_data_changed(self, top_left, bottom_right, roles=None):
        """處理資料變更事件"""
        if not self.is_editing or not hasattr(self, 'original_data'):
            return
            
        model = self.table_view.model()
        if not model:
            return
            
        # 處理變更的每個儲存格
        for row in range(top_left.row(), bottom_right.row() + 1):
            if row not in self.original_data:
                continue
                
            # 收集目前行的所有資料
            current_row_data = {}
            for col in range(model.columnCount()):
                column_name = model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
                item = model.item(row, col)
                value = item.text() if item else ""
                current_row_data[column_name] = value
            
            # 比較與原始資料的差異
            original_row_data = self.original_data[row]
            has_changes = False
            
            for column_name, current_value in current_row_data.items():
                original_value = str(original_row_data.get(column_name, ""))
                if current_value != original_value:
                    has_changes = True
                    break
            
            if has_changes:
                # 檢查是否已經記錄了這一行的變更
                existing_change = None
                for i, change in enumerate(self.pending_changes):
                    if (change['action'] == 'update' and 
                        change.get('row') == row):
                        existing_change = i
                        break
                
                # 更新或添加變更記錄
                if existing_change is not None:
                    self.pending_changes[existing_change]['new_data'] = current_row_data
                else:
                    self.pending_changes.append({
                        'action': 'update',
                        'row': row,
                        'old_data': original_row_data.copy(),
                        'new_data': current_row_data.copy()
                    })
                
                # 標記修改過的行（添加背景色）
                self.highlight_modified_row(row)
                
                self.update_toolbar_state()
            else:
                # 如果沒有變更，移除背景色標記
                self.remove_row_highlight(row)

    def highlight_modified_row(self, row):
        """為修改過的行添加背景色"""
        model = self.table_view.model()
        if not model:
            return
            
        # 設置淡黃色背景來標示修改過的行
        highlight_color = QColor(255, 248, 220)  # 淡黃色 (cornsilk)
        
        for col in range(model.columnCount()):
            item = model.item(row, col)
            if item:
                item.setBackground(highlight_color)

    def remove_row_highlight(self, row):
        """移除行的背景色標記"""
        model = self.table_view.model()
        if not model:
            return
            
        for col in range(model.columnCount()):
            item = model.item(row, col)
            if item:
                item.setBackground(QColor())  # 設置為預設背景（透明）

    def clear_all_highlights(self):
        """清除所有行的背景色標記"""
        model = self.table_view.model()
        if not model:
            return
            
        for row in range(model.rowCount()):
            for col in range(model.columnCount()):
                item = model.item(row, col)
                if item:
                    item.setBackground(QColor())  # 設置為預設背景（透明）

    def on_selection_changed(self, selected=None, deselected=None):
        """處理表格選擇變更"""
        _ = selected, deselected  # 忽略未使用的参数
        self.update_toolbar_state()

    def resizeEvent(self, event):
        """視窗大小改變時保存設置"""
        super().resizeEvent(event)
        if hasattr(self, 'config_manager'):
            # 延遲保存以避免頻繁寫入
            if hasattr(self, '_resize_timer'):
                self._resize_timer.stop()
            
            self._resize_timer = QTimer()
            self._resize_timer.timeout.connect(self.save_window_geometry)
            self._resize_timer.setSingleShot(True)
            self._resize_timer.start(500)  # 500ms 後保存
            

    def moveEvent(self, event):
        """視窗位置改變時保存設置"""
        super().moveEvent(event)
        if hasattr(self, 'config_manager'):
            # 延遲保存以避免頻繁寫入
            if hasattr(self, '_move_timer'):
                self._move_timer.stop()
            
            self._move_timer = QTimer()
            self._move_timer.timeout.connect(self.save_window_geometry)
            self._move_timer.setSingleShot(True)
            self._move_timer.start(500)  # 500ms 後保存

    def save_window_geometry(self):
        """保存當前視窗幾何"""
        self.config_manager.save_window_geometry(
            self.width(), self.height(), self.x(), self.y()
        )

    def update_column_selector(self, table_name, columns):
        """更新欄位選擇器內容"""
        if not table_name or not columns:
            self.column_selector_widget.hide()
            return
        
        # 清空現有的樹狀結構項目
        self.column_tree.clear()
        
        # 初始化表格的欄位顯示狀態（預設全勾選）
        if table_name not in self.column_visibility:
            self.column_visibility[table_name] = {col: True for col in columns}
        
        # 為當前表格創建新的複選框項目
        self.column_checkboxes[table_name] = {}
        
        for column in columns:
            # 創建樹狀結構項目
            item = QTreeWidgetItem([column])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            
            # 設置勾選狀態
            check_state = Qt.Checked if self.column_visibility[table_name].get(column, True) else Qt.Unchecked
            item.setCheckState(0, check_state)
            
            # 添加到樹狀結構
            self.column_tree.addTopLevelItem(item)
            
            # 記錄項目引用
            self.column_checkboxes[table_name][column] = item
        
        # 連接勾選狀態變更信號
        self.column_tree.itemChanged.connect(self.on_column_item_changed)
        
        # 顯示選擇器
        self.column_selector_widget.show()

    def on_column_item_changed(self, item, column):
        """處理欄位項目勾選狀態變更"""
        if not self.current_table_name or column != 0:
            return
        
        column_name = item.text(0)
        is_checked = item.checkState(0) == Qt.Checked
        self.column_visibility[self.current_table_name][column_name] = is_checked
        
        # 更新表格顯示
        self.apply_column_visibility()

    def on_column_visibility_changed(self, column_name, state):
        """處理欄位顯示狀態變更（保留舊方法以防相容性問題）"""
        if not self.current_table_name:
            return
        
        is_checked = state == Qt.Checked
        self.column_visibility[self.current_table_name][column_name] = is_checked
        
        # 更新表格顯示
        self.apply_column_visibility()

    def apply_column_visibility(self):
        """應用欄位顯示設定到表格"""
        if not self.current_table_name or not hasattr(self, 'table_view'):
            return
        
        model = self.table_view.model()
        if not model:
            return
        
        # 隱藏/顯示欄位
        for col_index in range(model.columnCount()):
            column_name = model.headerData(col_index, Qt.Horizontal, Qt.DisplayRole)
            is_visible = self.column_visibility[self.current_table_name].get(column_name, True)
            self.table_view.setColumnHidden(col_index, not is_visible)
        


    def reset_column_visibility(self):
        """重置欄位顯示狀態為預設（全勾選）"""
        if not self.current_table_name:
            return
        
        # 暫時斷開信號連接
        self.column_tree.blockSignals(True)
        
        # 重置為全選狀態
        for column in self.column_visibility[self.current_table_name]:
            self.column_visibility[self.current_table_name][column] = True
        
        # 更新樹狀項目的勾選狀態
        if self.current_table_name in self.column_checkboxes:
            for item in self.column_checkboxes[self.current_table_name].values():
                item.setCheckState(0, Qt.Checked)
        
        # 恢復信號連接
        self.column_tree.blockSignals(False)
        
        # 應用到表格
        self.apply_column_visibility()

    def closeEvent(self, event):
        # 保存視窗設置
        self.save_window_geometry()
        # This will just hide the window, the main loop will show the connections dialog
        self.hide()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('macintosh')
    
    # 設定應用程式層級的圖示
    import os
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    app_icon = QIcon()
    # 添加不同尺寸的圖示
    icon_sizes = [16, 32, 64, 128, 256, 512]
    loaded_icons = 0
    for size in icon_sizes:
        icon_path = os.path.join(icons_dir, f"AppIcon-{size}.png")
        if os.path.exists(icon_path):
            app_icon.addFile(icon_path, QSize(size, size))
            loaded_icons += 1
    
    if loaded_icons > 0:
        app.setWindowIcon(app_icon)
        print(f"Successfully loaded {loaded_icons} app icon sizes from icons directory")
    else:
        print("Warning: No app icon files found in icons directory")

    # 直接啟動主界面，不需要預先選擇資料庫
    main_win = MainWindow()
    main_win.show()
    
    sys.exit(app.exec_())
