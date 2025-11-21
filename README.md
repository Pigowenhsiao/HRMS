下面是一份可直接放到 GitHub 的 `README.md` 範本（已針對 **CSV 後端** 的 HRMS Python 專案撰寫）。你可以直接整份貼上，或依實際情況微調專案名稱與說明。

---

# HRMS (Python • Multi Backend)

> 以 **Python + PySide6** 重構的 HRMS（人資/員工管理）範例，支援多種資料存取後端（**`.csv` 檔案** 或 **Access Database**）。
> 特色：桌面 UI、CSV 儲存引擎（含檔案鎖與原子寫入）/Access 資料庫支援、匯出 Excel、（可選）FastAPI API。

## 目錄

* [功能特色](#功能特色)
* [專案結構](#專案結構)
* [安裝 & 快速開始](#安裝--快速開始)
* [設定檔](#設定檔)
* [CSV 資料表說明](#csv-資料表說明)
* [桌面操作說明](#桌面操作說明)
* [（可選）啟動 API](#可選啟動-api)
* [開發指引](#開發指引)
* [常見問題](#常見問題)
* [Roadmap](#roadmap)
* [授權](#授權)

---

## 功能特色

* **桌面 UI（PySide6）**：已提供 `TE_BASIC`（員工基本資料）可操作範例：查詢、載入、**新增/更新（Upsert）**、刪除、匯出 Excel。
* **CSV 儲存引擎**：以 `pandas` 讀寫、`filelock` 檔案鎖、**寫臨時檔 → 原子改名**，降低檔案毀損風險。
* **分層設計**：UI ↔ Service ↔ Repository ↔ Storage（CSV Adapter），便於後續擴充其他表/畫面。
* **可設定**：支援 `.env` 與 `config/settings.yaml` 調整資料目錄與應用名稱。
* **（可選）FastAPI API**：可從 CSV 讀資料回傳 JSON，便於日後轉 Web 或整合他系統。

---

## 專案結構

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
│  │  └─ reporting/reports.py     # DataFrame → Excel 匯出
│  ├─ persons/
│  │  ├─ models.py                # BASIC 資料列 dataclass（可擴充）
│  │  ├─ repository.py            # EmployeeRepository（支援 CSV 和 Access）
│  │  └─ service.py               # 封裝 repo（供 UI/API 使用）
│  ├─ lookups/
│  │  └─ service.py               # 下拉選單資料（支援 CSV 和 Access）
│  ├─ ui/qt/
│  │  ├─ start_app.py             # 桌面版進入點
│  │  └─ windows/
│  │     ├─ start_page.py         # 主畫面（選單）
│  │     └─ basic_window.py       # TE_BASIC（員工基本資料）
│  ├─ api/server.py               # FastAPI（可選）
│  └─ migrate_csv_to_access.py    # CSV 資料遷移至 Access 工具
├─ openspec/                      # 專案規範文件
└─ tests/
   └─ test_sanity.py
```

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
```

執行後會看到主畫面，點選「**員工基本資料（TE_BASIC 範例）**」即可開啟 CRUD 與匯出功能。

---

## 設定檔

### `.env`

```ini
# 應用名稱（UI 視窗標題等）
APP_NAME=HRMS Multi-Backend

# 後端：csv 或 access
HRMS_DB_BACKEND=access

# CSV 資料目錄（當使用 CSV 時）
HRMS_CSV_DATA_DIR=./data

# Access 資料庫路徑（當使用 Access 時）
ACCESS_DB_PATH=./hrms.mdb
```

### `config.py`

系統現在使用 `config.py` 作為主要配置管理，支援環境變數配置。

> 修改 `.env` 後重啟應用生效。

---

## CSV 資料表說明

### `data/BASIC.csv`（員工主檔）

**表頭欄位（示範專案已附樣本資料）：**

```
EMP_ID,Dept_Code,C_Name,Title,On_Board_Date,Shift,Area,Function,Meno,Active,VAC_ID,VAC_DESC,Start_date,End_date,AreaDate
```

* **主鍵**：`EMP_ID`
* **Active** 儲存為字串：`true` / `false`（UI 會自動對應選取）
* **日期欄位**（如 `On_Board_Date`）目前以字串表示（建議採 `YYYY-MM-DD` 或 `YYYY/MM/DD` 一致格式）。

### 其他對照表（節選）

* `L_Section.csv`：`Dept_Code,Dept_Name,Dept_Desc,Supervisor`
* `Area.csv`：`Area,Area_Desc,Active`
* `L_Job.csv`：`L_Job`
* `VAC_Type.csv`：`VAC_ID,VAC_DESC,Active`

> 需要更多表時，複製 `persons/repository.py` 的寫法另建 Repository + Service，UI 直接呼叫 Service，不必接觸 CSV 細節。

---

## 桌面操作說明

**路徑**：`hrms/ui/qt/windows/basic_window.py`

* **載入**：輸入 `EMP_ID` →「載入」
* **新增/更新（Upsert）**：填好欄位 →「新增/更新」
* **刪除**：輸入 `EMP_ID` →「刪除」
* **刷新清單**：更新下方表格（預設顯示前 500 筆）
* **匯出 Excel**：匯出清單至 `exports/` 目錄（使用 `openpyxl`）

---

## （可選）啟動 API

專案提供簡易 API（從 CSV 讀資料回傳 JSON），便於整合或日後轉 Web。

```bash
uvicorn hrms.api.server:app --reload
# 例：GET http://127.0.0.1:8000/employees
```

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

## 常見問題

* **多人同時寫入會不會壞檔？**
  本專案寫入採 **檔案鎖（filelock）** + **寫臨時檔後原子改名**，能降低風險；但 CSV 非資料庫，不具事務與鎖粒度控制。若有多人同時寫入或高併發，建議評估改用 SQLite / PostgreSQL。
* **日期/布林型別要怎麼處理？**
  CSV 皆以字串儲存：布林對外接受 `true/false`、`1/0`、`y/n`（不分大小寫），儲存時統一為 `true/false`；日期建議統一格式（`YYYY-MM-DD`）。
* **匯出 Excel 失敗？**
  確認 `exports/` 可寫入，且已安裝 `openpyxl`（在 `requirements.txt` 內）。

---

## Roadmap

* 搬遷更多畫面：`TE_Personal_INFO`、`TE_Education`、`CF_Certify_Record`…
* 報表集中化（pandas 聚合 + 匯出模組化）。
* 權限/角色模型（以 `Authority.csv` 擴充）。
* 可替換式儲存層：CSV ↔ SQLite/PG（保持 Service/Repository 介面不變）。

---




