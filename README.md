# HRMS (Python • Multi Backend)

> 以 **Python + PySide6** 重構的 HRMS（人資/員工管理）系統，支援多種資料存取後端（**`.csv` 檔案** 或 **Access Database**）。
> 特色：桌面 UI、CSV 儲存引擎（含檔案鎖與原子寫入）/Access 資料庫支援、匯出 Excel、（可選）FastAPI API、權限管理、多業務模組。

## 目錄

* [功能特色](#功能特色)
* [安裝 & 快速開始](#安裝--快速開始)
* [設定檔](#設定檔)
* [系統架構](#系統架構)
* [業務模組](#業務模組)
* [API 文件](#api-文件)
* [權限管理](#權限管理)
* [報表系統](#報表系統)
* [開發指引](#開發指引)
* [測試](#測試)
* [常見問題](#常見問題)
* [Roadmap](#roadmap)
* [授權](#授權)

---

## 功能特色

* **多後端支援**：支援 CSV 檔案或 Access 資料庫作為資料儲存後端。
* **桌面 UI（PySide6）**：提供員工基本資料（TE_BASIC）可操作範例：查詢、載入、**新增/更新（Upsert）**、刪除、匯出 Excel。
* **個人訊息管理**：支援員工個人訊息（生日、身分證字號、聯絡資訊等）的管理。
* **教育經歷管理**：支援員工教育經歷記錄的管理。
* **CSV 儲存引擎**：以 `pandas` 讀寫、`filelock` 檔案鎖、**寫臨時檔 → 原子改名**，降低檔案毀損風險。
* **Access 資料庫支援**：完整支援 Microsoft Access 資料庫，包含表格創建和資料遷移功能。
* **分層設計**：UI ↔ Service ↔ Repository ↔ Storage（CSV/Access Adapter），便於後續擴充其他表/畫面。
* **權限管理**：基於角色的訪問控制（RBAC），支援不同權限等級的操作。
* **資料驗證**：使用 Pydantic 進行完整的輸入資料驗證。
* **錯誤處理**：統一的異常處理和日誌記錄系統。
* **報表系統**：提供多種標準報表和自定義報表功能。
* **API 服務**：使用 FastAPI 提供完整的 RESTful API 服務。
* **可設定**：支援 `.env` 與 `config.py` 調整資料目錄與應用名稱。

---

## 安裝 & 快速開始

> 需要 Python 3.10+（建議使用虛擬環境）

```bash
# 1) 建立虛擬環境
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

# 2) 安裝套件
pip install -r requirements.txt

# 3) 建立設定檔
cp .env.example .env

# 4) 如果使用 Access 資料庫，可以將現有 CSV 資料遷移至 Access
python -m hrms.migrate_csv_to_access

# 5) 啟動桌面 App
python -m hrms.ui.qt.start_app

# 6) 或啟動 API 服務
uvicorn hrms.api.server:app --reload
```

執行後會看到主畫面，點選「**員工基本資料（TE_BASIC 範例）**」即可開啟 CRUD 與匯出功能。

## 設定檔

### `.env`

```ini
# App
APP_NAME=HRMS Multi-Backend

# 後端：csv 或 access
HRMS_DB_BACKEND=access

# CSV 設定（當使用 CSV 時）
HRMS_CSV_DATA_DIR=./data

# Access 資料庫路徑（當使用 Access 時）
ACCESS_DB_PATH=./hrms.mdb
```

系統現在使用 `config.py` 作為主要配置管理，支援環境變數配置。

> 修改 `.env` 後重啟應用生效。

---

## 系統架構

```
.
├─ README.md
├─ requirements.txt
├─ .env.example
├─ config.py                      # 配置管理（支援 CSV 和 Access）
├─ db.py                          # SQLAlchemy 配置（保留向後兼容）
├─ .env                           # 環境變數配置
├─ config/
├─ data/                          # ★ 所有 CSV 檔（資料表）放這裡
│  ├─ BASIC.csv                   # 員工主檔（已附範例資料）
│  ├─ L_Section.csv               # 部門對照
│  ├─ Area.csv                    # 區域對照
│  ├─ L_Job.csv                   # 職務對照
│  └─ VAC_Type.csv                # 假別對照
├─ hrms/
│  ├─ core/
│  │  ├─ config.py                # 讀取 .env 配置
│  │  ├─ utils/logger.py
│  │  ├─ db/
│  │  │  ├─ database.py           # DBAdapter 介面（抽象）
│  │  │  ├─ adapters/
│  │  │  │  ├─ csv_adapter.py     # CSVAdapter：list/get/upsert/delete/distinct
│  │  │  │  └─ access_adapter.py  # AccessAdapter：支援 Access 資料庫
│  │  │  ├─ repository.py         # BaseRepository
│  │  │  └─ unit_of_work.py       # UnitOfWork（支援 CSV 和 Access）
│  │  ├─ models.py                # Pydantic 數據模型定義
│  │  ├─ exceptions.py            # 自定義異常類別
│  │  └─ reporting/reports.py     # DataFrame → Excel 匯出
│  ├─ persons/
│  │  ├─ models.py                # BASIC 資料列 model（可擴充）
│  │  ├─ repository.py            # EmployeeRepository（支援 CSV 和 Access）
│  │  └─ service.py               # 封裝 repo（供 UI/API 使用）
│  ├─ personal_info/
│  │  └─ service.py               # 個人訊息管理服務
│  ├─ education/
│  │  ├─ models.py                # 教育經歷數據模型
│  │  └─ service.py               # 教育經歷管理服務
│  ├─ auth/
│  │  └─ service.py               # 認證授權服務
│  ├─ reports/
│  │  └─ service.py               # 報表生成服務
│  ├─ lookups/
│  │  └─ service.py               # 下拉選單資料（支援 CSV 和 Access）
│  ├─ ui/qt/
│  │  ├─ start_app.py             # 桌面版進入點
│  │  └─ windows/
│  │     ├─ start_page.py         # 主畫面（選單）
│  │     └─ basic_window.py       # TE_BASIC（員工基本資料）
│  ├─ api/
│  │  ├─ server.py                # FastAPI 主服務
│  │  ├─ auth_routes.py           # 認證相關路由
│  │  ├─ personal_info_routes.py  # 個人訊息相關路由
│  │  ├─ education_routes.py      # 教育經歷相關路由
│  │  └─ report_routes.py         # 報表相關路由
│  ├─ migrate_csv_to_access.py    # CSV 資料遷移至 Access 工具
│  └─ core/utils/
│     ├─ date_utils.py            # 日期處理工具
│     └─ logger.py                # 日誌記錄工具
├─ docs/                          # 文檔目錄
│  └─ FUNCTIONAL_UPDATES.md       # 功能完善總結
├─ openspec/                      # 專案規範文件
└─ tests/
   ├─ test_sanity.py
   ├─ test_employees_service.py   # 員工服務測試
   ├─ test_date_utils.py          # 日期工具測試
   ├─ test_exceptions.py          # 異常類別測試
   ├─ test_access_adapter.py      # Access 適配器測試
   └─ test_csv_adapter.py         # CSV 適配器測試
```

---

## 業務模組

### 員工基本資料 (TE_BASIC)
- 查詢、載入、新增/更新、刪除員工資料
- 匯出 Excel 功能

### 個人訊息管理
- 管理員工個人訊息（生日、身分證字號、聯絡資訊等）
- 完整的 CRUD 操作

### 教育經歷管理
- 管理員工教育經歷記錄
- 支援學校、科系、學歷等資訊

---

## API 文件

### 員工相關
- `GET /employees` - 獲取員工列表
- `GET /personal-info/` - 獲取個人訊息列表
- `GET /education/` - 獲取教育經歷列表

### 權限相關
- `GET /auth/users` - 獲取用戶列表
- `POST /auth/users` - 創建新用戶
- `GET /auth/permissions/{account}/{permission}` - 檢查用戶權限

### 報表相關
- `GET /reports/employee-summary` - 員工摘要報表
- `GET /reports/department-headcount` - 部門人數報表
- `GET /reports/service-length-analysis` - 年資分析報表

---

## 權限管理

系統實現了基於角色的訪問控制（RBAC），包含以下預設角色：
- `admin` (系統管理員) - 擁有所有權限
- `hr_manager` (人事經理) - 員工管理、報表查看等權限
- `hr_staff` (人事專員) - 基本員工管理權限
- `employee` (一般員工) - 僅查看權限

---

## 報表系統

系統提供多種標準報表和自定義報表功能：
- 員工摘要報表（可選擇是否包含個人訊息）
- 部門人數統計報表
- 按區域分類的員工報表
- 年資分析報表
- 自定義報表（可指定表格、過濾條件和列）

報表會自動匯出為 Excel 格式並返回文件路徑。

---

## 開發指引

* **選擇後端類型**

  1. 在 `.env` 中設定 `HRMS_DB_BACKEND=csv` 或 `HRMS_DB_BACKEND=access` 來選擇後端。
  2. 如使用 Access，可透過 `hrms.migrate_csv_to_access.py` 將現有 CSV 資料遷移至 Access 資料庫。

* **新增一張表**（CSV 或 Access，範例流程）

  1. 如使用 CSV：在 `data/` 建立對應的 `TABLE_NAME.csv`（先放表頭欄位）。
  2. 如使用 Access：直接在 Access 資料庫中建立對應表格。
  3. 建新的 Repository（參考 `persons/repository.py`）並指定表名/主鍵/欄位。
  4. 在 Service 層封裝方法（如 `list_* / get_* / upsert_* / delete_*`）。
  5. UI 透過 Service 呼叫，維持單向依賴。
* **測試**：

  ```bash
  pytest
  ```

---

## 測試

專案包含多個測試模組來確保功能的穩定性：
- `tests/test_employees_service.py` - 員工服務測試
- `tests/test_date_utils.py` - 日期工具測試
- `tests/test_exceptions.py` - 異常類別測試
- `tests/test_access_adapter.py` - Access 適配器測試
- `tests/test_csv_adapter.py` - CSV 適配器測試

執行所有測試：
```bash
pytest
```

---

## 常見問題

* **多人同時寫入會不會壞檔？**
  當使用 CSV 後端時，本專案寫入採用 **檔案鎖（filelock）** + **寫臨時檔後原子改名**，能降低風險；但 CSV 非資料庫，不具事務與鎖粒度控制。若有多人同時寫入或高併發，建議使用 Access 或其他資料庫後端。
* **如何從 CSV 遷移到 Access？**
  確保您的 Windows 系統已安裝 Microsoft Access Database Engine，然後更新 `.env` 中的設定為 `HRMS_DB_BACKEND=access`，運行 `python -m hrms.migrate_csv_to_access` 來將現有 CSV 資料遷移到 Access 資料庫。
* **Access 驅動程式支援情況？**
  Microsoft Access 驅動程式原生僅支援 Windows 系統。在 macOS 和 Linux 系統上，建議使用 CSV 後端或考慮其他資料庫（如 SQLite、PostgreSQL）。
* **日期/布林型別要怎麼處理？**
  系統內部統一使用字串格式處理日期，並提供專門的日期工具進行解析和格式化；布林值統一處理為 "true"/"false" 字串。

---

## Roadmap

* 擴展更多業務模組：證照記錄、考績管理、薪資管理等。
* 實現更細緻的權限控制（欄位級別權限）。
* 添加數據備份和恢復功能。
* 實現用戶界面的權限控制。
* 優化大型數據集的處理性能。
* 添加完整的審計日誌系統。

---

## 授權

本專案為範例代碼，可用於學習和參考。如需商業使用，請確保符合相關授權要求。