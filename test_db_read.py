#!/usr/bin/env python3
"""
測試讀取 user_mapping_cache.db 文件
"""

import sqlite3
import os

def test_database_read():
    """測試讀取資料庫文件"""
    db_path = 'user_mapping_cache.db'
    
    # 檢查文件是否存在
    if not os.path.exists(db_path):
        print(f"資料庫文件不存在: {db_path}")
        return False
    
    try:
        # 嘗試連接資料庫
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 獲取所有表格
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"資料庫中包含的表格: {tables}")
        
        # 如果有表格，顯示第一個表格的結構
        if tables:
            first_table = tables[0]
            print(f"\n表格 '{first_table}' 的結構:")
            
            cursor.execute(f"PRAGMA table_info({first_table});")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - notnull: {col[3]}, default: {col[4]}, pk: {col[5]}")
            
            # 獲取表格數據（如果有的話）
            cursor.execute(f"SELECT * FROM {first_table} LIMIT 5;")
            rows = cursor.fetchall()
            
            print(f"\n表格數據 (前5行):")
            for row in rows:
                print(f"  {row}")
        
        conn.close()
        print("\n資料庫讀取成功!")
        return True
        
    except Exception as e:
        print(f"讀取資料庫時發生錯誤: {e}")
        return False

if __name__ == '__main__':
    test_database_read()