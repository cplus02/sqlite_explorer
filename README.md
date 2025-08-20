# SQLite Explorer

SQLite Explorer 是一個用 Python 和 PyQt5 開發的現代化 SQLite 資料庫管理工具，提供直觀的圖形界面來瀏覽、編輯和查詢 SQLite 資料庫。

![SQLite Explorer](icons/AppIcon-512.png)

## 功能特色

- 🔍 **資料庫瀏覽**: 樹狀結構顯示資料庫、表格和欄位
- 📊 **資料檢視**: 支援分頁的資料表格顯示
- ✏️ **記錄編輯**: 直接在介面中新增、編輯、刪除記錄
- 🔎 **智慧搜尋**: 支援全文搜尋和進階過濾
- 💾 **連線管理**: 儲存和管理多個資料庫連線
- 📝 **SQL 查詢**: 內建 SQL 編輯器支援語法高亮
- 📈 **Schema 檢視**: 顯示表格結構和關聯性
- 🎨 **現代化介面**: 支援 macOS 原生外觀和深色模式

## 系統需求

- **作業系統**: macOS 10.14 或更新版本
- **Python**: 3.8+ (僅開發環境需要)

## 安裝方式

### 下載預編譯應用程式 (推薦)

1. 從 [Releases](../../releases) 頁面下載最新版本的 `SQLite Explorer.app`
2. 將應用程式拖拽到 `/Applications` 資料夾
3. 首次開啟時可能需要在「系統偏好設定 > 安全性與隱私權」中允許執行

### 從原始碼執行

```bash
# 複製專案
git clone https://github.com/your-username/sqlite-explorer.git
cd sqlite-explorer

# 安裝依賴
pip install -r requirements.txt

# 執行應用程式
python main.py
```

## 開發環境

### 建置應用程式包

```bash
# 建立 macOS 應用程式包
pyinstaller sqlite_explorer.spec

# 應用程式會產生在 dist/SQLite Explorer.app
```

### 專案結構

```
sqlite_explorer/
├── main.py                 # 主應用程式
├── db_handler.py           # 資料庫操作模組
├── config.py               # 設定管理
├── dialogs.py              # 對話框組件
├── sqlite_explorer.spec    # PyInstaller 配置
├── requirements.txt        # Python 依賴
├── icons/                  # 應用程式圖示
├── tests/                  # 單元測試
└── README.md               # 專案說明
```

## 使用說明

1. **連線資料庫**: 點選工具列的「Connect」按鈕選擇 SQLite 檔案
2. **瀏覽資料**: 左側樹狀結構顯示所有表格，點選表格名稱檢視資料
3. **編輯記錄**: 雙擊資料列即可編輯，支援新增和刪除功能
4. **執行查詢**: 使用「Query」頁籤執行自訂 SQL 查詢
5. **搜尋資料**: 使用頂部搜尋欄進行全文搜尋

## 技術特色

- **原生 macOS 體驗**: 使用 PyQt5 打造符合 macOS 設計規範的介面
- **高效能**: 支援大型資料庫的分頁載入和即時搜尋
- **安全性**: 使用參數化查詢防止 SQL 注入攻擊
- **可擴展**: 模組化架構便於添加新功能

## 貢獻

歡迎提交 Issue 和 Pull Request 來改善這個專案。

## 授權

MIT License - 詳見 [LICENSE](LICENSE) 檔案。