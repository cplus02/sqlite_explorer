#!/usr/bin/env python3
"""
SQLite Explorer - Configuration
應用程式的設定檔
"""

import configparser
import os
import sys

def get_config_path():
    """獲取配置檔案的路徑（用戶目錄下可寫入）"""
    home_dir = os.path.expanduser("~")
    app_dir = os.path.join(home_dir, ".sqlite_explorer")
    
    # 確保應用程式目錄存在
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    
    return os.path.join(app_dir, "config.ini")

CONFIG_FILE = get_config_path()

class ConfigManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        # 保留 option 名稱的原始大小寫
        self.config.optionxform = str
        self.config_file = CONFIG_FILE
        if not os.path.exists(self.config_file):
            self.create_default_config()
        else:
            self.config.read(self.config_file)

    def reload_config(self):
        # 清除現有配置然後重新讀取
        self.config.clear()
        self.config.read(self.config_file)

    def create_default_config(self):
        self.config['connections'] = {}
        self.config['window'] = {
            'width': '1000',
            'height': '700',
            'x': '100',
            'y': '100',
            'sidebar_width': '200'
        }
        self.config['app'] = {
            'last_database': ''
        }
        self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def add_connection(self, name, path):
        if 'connections' not in self.config:
            self.config['connections'] = {}
        self.config['connections'][name] = path
        self.save_config()

    def get_connection(self, name):
        return self.config['connections'].get(name)

    def get_all_connections(self):
        if 'connections' in self.config:
            return self.config['connections']
        return {}

    def remove_connection(self, name):
        if 'connections' in self.config and name in self.config['connections']:
            del self.config['connections'][name]
            self.save_config()

    def save_window_geometry(self, width, height, x, y):
        """保存視窗幾何資訊"""
        if 'window' not in self.config:
            self.config['window'] = {}
        self.config['window']['width'] = str(width)
        self.config['window']['height'] = str(height)
        self.config['window']['x'] = str(x)
        self.config['window']['y'] = str(y)
        self.save_config()

    def get_window_geometry(self):
        """獲取視窗幾何資訊"""
        if 'window' in self.config:
            try:
                return {
                    'width': int(self.config['window'].get('width', '1000')),
                    'height': int(self.config['window'].get('height', '700')),
                    'x': int(self.config['window'].get('x', '100')),
                    'y': int(self.config['window'].get('y', '100'))
                }
            except ValueError:
                pass
        return {'width': 1000, 'height': 700, 'x': 100, 'y': 100}

    def save_sidebar_width(self, width):
        """保存側邊欄寬度"""
        if 'window' not in self.config:
            self.config['window'] = {}
        self.config['window']['sidebar_width'] = str(width)
        self.save_config()

    def get_sidebar_width(self):
        """獲取側邊欄寬度"""
        if 'window' in self.config:
            try:
                return int(self.config['window'].get('sidebar_width', '200'))
            except ValueError:
                pass
        return 200

    def save_data_schema_width(self, width):
        """保存 Data Schema 寬度"""
        if 'window' not in self.config:
            self.config['window'] = {}
        self.config['window']['data_schema_width'] = str(width)
        self.save_config()

    def get_data_schema_width(self):
        """獲取 Data Schema 寬度"""
        if 'window' in self.config:
            try:
                return int(self.config['window'].get('data_schema_width', '250'))
            except ValueError:
                pass
        return 250

    def save_query_schema_width(self, width):
        """保存 Query Schema 寬度"""
        if 'window' not in self.config:
            self.config['window'] = {}
        self.config['window']['query_schema_width'] = str(width)
        self.save_config()

    def get_query_schema_width(self):
        """獲取 Query Schema 寬度"""
        if 'window' in self.config:
            try:
                return int(self.config['window'].get('query_schema_width', '250'))
            except ValueError:
                pass
        return 250

    def save_column_widths(self, db_path, table_name, column_widths):
        """保存表格欄位寬度"""
        if 'column_widths' not in self.config:
            self.config['column_widths'] = {}
        
        # 使用安全的 key 格式，避免特殊字符
        import hashlib
        key_string = f"{db_path}::{table_name}"
        key = hashlib.md5(key_string.encode()).hexdigest()
        self.config['column_widths'][key] = ','.join(map(str, column_widths))
        self.save_config()

    def get_column_widths(self, db_path, table_name):
        """獲取表格欄位寬度"""
        if 'column_widths' not in self.config:
            return None
            
        # 使用相同的 key 生成方式
        import hashlib
        key_string = f"{db_path}::{table_name}"
        key = hashlib.md5(key_string.encode()).hexdigest()
        widths_str = self.config['column_widths'].get(key)
        
        if widths_str:
            try:
                return [int(w) for w in widths_str.split(',')]
            except ValueError:
                pass
        return None

    def save_last_database(self, db_path):
        """保存上次打開的資料庫"""
        if 'app' not in self.config:
            self.config['app'] = {}
        self.config['app']['last_database'] = db_path
        self.save_config()

    def get_last_database(self):
        """獲取上次打開的資料庫"""
        if 'app' in self.config:
            return self.config['app'].get('last_database', '')
        return ''
