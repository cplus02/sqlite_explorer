#!/usr/bin/env python3
"""
SQLite Explorer - Database Handler Test Suite
測試資料庫處理模組的功能
"""

import unittest
import os
import sys
import tempfile
import sqlite3

# 添加上一層目錄到 Python 路徑，以便能正確導入 db_handler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db_handler import DBHandler

class TestDBHandler(unittest.TestCase):
    """測試 DBHandler 類別"""
    
    def setUp(self):
        """設置測試環境"""
        # 創建一個臨時資料庫文件
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix='.db')
        
        # 創建 DBHandler 實例
        self.db_handler = DBHandler(self.temp_db_path)

        # 創建一個測試表格
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("INSERT INTO test_table (id, name) VALUES (1, 'test1')")
        cursor.execute("INSERT INTO test_table (id, name) VALUES (2, 'test2')")
        conn.commit()
        conn.close()
        
    def tearDown(self):
        """清理測試環境"""
        # 斷開資料庫連接
        self.db_handler.disconnect_database()
        # 關閉文件描述符
        os.close(self.temp_db_fd)
        # 刪除臨時資料庫文件
        os.unlink(self.temp_db_path)
    
    def test_connect_to_database(self):
        """測試連接到資料庫"""
        # 測試成功連接
        self.assertIsNotNone(self.db_handler.connection)
        
        # 測試連接不存在的資料庫
        bad_handler = DBHandler()
        result = bad_handler.connect_to_database('/non/existent/database.db')
        self.assertFalse(result)
    
    def test_list_tables(self):
        """測試獲取表格列表"""
        tables = self.db_handler.list_tables()
        self.assertIn('test_table', tables)
    
    def test_get_table_schema(self):
        """測試獲取表格結構"""
        schema = self.db_handler.get_table_schema('test_table')
        self.assertIsInstance(schema, list)
        self.assertEqual(len(schema), 2)
        self.assertEqual(schema[0][1], 'id')
        self.assertEqual(schema[1][1], 'name')

    def test_get_table_data(self):
        """測試獲取表格的資料"""
        data, columns = self.db_handler.get_table_data('test_table')
        self.assertIsInstance(data, list)
        self.assertIsInstance(columns, list)
        self.assertEqual(len(data), 2)
        self.assertEqual(len(columns), 2)
        self.assertEqual(columns[0], 'id')
        self.assertEqual(columns[1], 'name')
        self.assertEqual(data[0][1], 'test1')
        self.assertEqual(data[1][1], 'test2')
    
    def test_execute_query(self):
        """測試執行 SQL 查詢"""
        # 執行 SELECT 查詢
        result = self.db_handler.execute_query("SELECT * FROM test_table")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3) # header + 2 rows
        
        # 執行 INSERT 查詢
        result = self.db_handler.execute_query("INSERT INTO test_table (name) VALUES ('test_name2')")
        self.assertIsNone(result)

        # 驗證 INSERT 結果
        data, _ = self.db_handler.get_table_data('test_table')
        self.assertEqual(len(data), 3)

if __name__ == '__main__':
    unittest.main()