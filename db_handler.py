#!/usr/bin/env python3
"""
SQLite Explorer - Database Handler
處理 SQLite 資料庫的連接和操作
"""

import sqlite3
from PyQt5.QtCore import QObject, pyqtSignal
import os

class DBHandler(QObject):
    """處理 SQLite 資料庫連接和操作的類別"""
    
    # 定義信號，用於通知 UI 更新
    database_connected = pyqtSignal(str)
    database_disconnected = pyqtSignal()
    tables_loaded = pyqtSignal(list)
    query_result = pyqtSignal(object)
    
    def __init__(self, db_path=None):
        super().__init__()
        self.connection = None
        self.current_database = None
        if db_path:
            self.connect_to_database(db_path)
        
    def connect_to_database(self, db_path):
        """連接到 SQLite 資料庫"""
        try:
            # 檢查資料庫檔案是否存在
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"資料庫檔案不存在: {db_path}")
            
            # 建立資料庫連接
            self.connection = sqlite3.connect(db_path)
            self.current_database = db_path
            
            # 發送連接成功的信號
            self.database_connected.emit(db_path)
            
            return True
            
        except Exception as e:
            print(f"連接資料庫時發生錯誤: {e}")
            return False
    
    def disconnect_database(self):
        """斷開資料庫連接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.current_database = None
            self.database_disconnected.emit()
    
    def list_tables(self):
        """獲取資料庫中的所有表格名稱"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            # 發送表格載入完成的信號
            self.tables_loaded.emit(tables)
            
            return tables
            
        except Exception as e:
            print(f"獲取表格列表時發生錯誤: {e}")
            return []
    
    def get_table_schema(self, table_name):
        """獲取表格結構"""
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            schema = cursor.fetchall()

            return schema

        except Exception as e:
            print(f"獲取表格結構時發生錯誤: {e}")
            return []

    def get_table_indexes(self, table_name):
        """獲取表格的所有索引"""
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor()

            # 獲取所有索引
            cursor.execute(f"PRAGMA index_list({table_name});")
            indexes = cursor.fetchall()

            index_details = []
            for index in indexes:
                index_name = index[1]
                is_unique = index[2]
                is_primary = index[3]

                # 獲取索引的欄位信息
                cursor.execute(f"PRAGMA index_info({index_name});")
                index_columns = cursor.fetchall()

                index_detail = {
                    'name': index_name,
                    'unique': bool(is_unique),
                    'primary': bool(is_primary),
                    'columns': [{'name': col[2], 'seqno': col[0]} for col in index_columns]
                }
                index_details.append(index_detail)

            return index_details

        except Exception as e:
            print(f"獲取表格索引時發生錯誤: {e}")
            return []

    def get_table_data(self, table_name):
        """獲取表格的所有資料"""
        if not self.connection:
            return None, None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return data, columns
            
        except Exception as e:
            print(f"執行查詢時發生錯誤: {e}")
            return None, None
    
    def execute_query(self, query):
        """執行 SQL 查詢"""
        if not self.connection:
            return None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            # 如果是 SELECT 查詢，獲取結果
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                # 將結果轉換為列表的列表
                formatted_results = [columns] + results
                
                # 發送查詢結果信號
                self.query_result.emit(formatted_results)
                
                return formatted_results
            else:
                # 如果是其他類型的查詢（INSERT, UPDATE, DELETE 等）
                self.connection.commit()
                return None
                
        except Exception as e:
            print(f"執行查詢時發生錯誤: {e}")
            return None