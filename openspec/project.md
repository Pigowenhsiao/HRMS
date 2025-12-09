# Project Context

## Purpose
HRMS (Human Resource Management System) 是一個單機版桌面應用程式，從原有的 VB.NET + Access 系統遷移至 Python + SQLite 資料庫，並使用 PySide6 作為 UI 框架。本專案旨在完整複製原有 Visual Basic 程式的所有功能與設定，提供穩定可靠的單機人資管理解決方案，避免多人同時使用造成的資料衝突問題。

**核心設計目標：**
- **單機版作業**：專為單機環境設計，無需網路伺服器即可運行
- **SQLite 資料庫**：取代 CSV 檔案儲存，提供 ACID 事務、資料完整性與鎖定機制，避免多人使用衝突
- **完整功能複製**：完整重現原有 VB 程式的所有功能模組與操作邏輯
- **完整的設定功能**：包含所有系統參數、權限設定、對照表維護等設定功能
- **桌面 UI 體驗**：使用 PySide6 提供直覺的視窗操作介面，保持使用者習慣
- **資料匯出功能**：支援 Excel 匯出以便產生報表
- **模組化架構**：保持分層設計以便未來擴充或整合

## Tech Stack

### Core Technologies
- **Python 3.10+** - Primary language
- **PySide6** - Qt-based desktop UI framework
- **Pandas** - Data manipulation and CSV operations
- **FastAPI + Uvicorn** - Optional REST API server

### Storage & Data
- **SQLite Database** - Primary data storage with full ACID transaction support
- **SQLAlchemy** - ORM for database operations (提升開發效率與安全性)
- **Python-dotenv** - Environment configuration
- **PyYAML** - YAML configuration files

### Export & Reporting
- **Openpyxl** - Excel file generation
- **Pandas ExcelWriter** - DataFrame to Excel export

### Development & Testing
- **Pytest** - Testing framework (minimal implementation)
- **Pydantic v2** - Data validation

## Project Conventions

### Code Style
- **Python Version**: 3.10+ with type hints
- **Imports**: Standard library first, then third-party, then local modules
- **Naming**: 
  - Classes: PascalCase (e.g., `EmployeeRepositoryCSV`)
  - Functions/Methods: snake_case (e.g., `list_employees`)
  - Constants: UPPER_SNAKE_CASE (e.g., `TABLE = "BASIC"`)
- **String Formatting**: UTF-8 encoding throughout
- **Type Hints**: Required for all public methods and functions
- **Line Length**: Follow PEP 8 guidelines (88 characters recommended)

### Architecture Patterns

**分層架構 (SQLite 版本):**
```
UI 層 (PySide6 Windows)
    ↓
服務層 (hrms/persons/service.py, hrms/lookups/service.py 等)
    ↓
儲存庫層 (hrms/persons/repository.py, hrms/departments/repository.py 等)
    ↓
資料庫層 (使用 SQLAlchemy ORM 或原生 SQLite)
    ↓
SQLite 資料庫檔案 (hrms.db)
```

**關鍵設計模式:**
1. **Repository Pattern**: 抽象化資料存取，每個主要資料表都有對應的 Repository
2. **Service Layer**: 封裝商業邏輯，提供 UI 和 API 呼叫的一致介面
3. **ORM 整合**: 使用 SQLAlchemy 簡化資料庫操作並防止 SQL 注入
4. **Transaction Management**: SQLite 提供完整的 ACID 事務支援
5. **模組化設計**: 每個功能模組獨立（人事、部門、權限、證照等）

**模組組織 (擴充後):**
- `hrms/core/` - 核心基礎設施（config、database、utils）
- `hrms/persons/` - 員工管理（models、repository、service、ui）
- `hrms/departments/` - 部門管理
- `hrms/authorities/` - 權限管理
- `hrms/certifications/` - 證照管理
- `hrms/training/` - 訓練記錄管理
- `hrms/lookups/` - 下拉選單對照資料
- `hrms/ui/qt/` - 桌面 UI 元件（各功能視窗）
- `hrms/api/` - REST API 端點

### Testing Strategy
- **Current State**: Minimal test coverage (sanity test only)
- **Recommended Approach**:
  - Unit tests for adapters and services
  - Integration tests for CSV operations with temp files
  - UI tests (optional) using Qt Test framework
- **Test Structure**: Mirror source structure in `tests/` directory
- **CI/CD**: None currently implemented

### Git Workflow
- **Branching**: Feature branches from main
- **Commits**: Descriptive messages (English recommended for consistency)
- **Main Branch**: Stable, deployable code
- **Pull Requests**: Not enforced but recommended for collaboration
- **No Conventional Commits**: Currently no strict commit format

## Domain Context

### HRMS Entities
- **BASIC** - Employee master data (EMP_ID as primary key)
- **L_Section** - Department/section lookup
- **Area** - Geographic/work area lookup  
- **L_Job** - Job function/title lookup
- **VAC_Type** - Vacation/absence type lookup

### Key Fields & Data Types
- **EMP_ID**: String, unique employee identifier
- **Active**: Boolean stored as "true"/"false" string in CSV
- **Dates**: String format (YYYY-MM-DD or YYYY/MM/DD recommended)
- **Departments**: Code-based (e.g., L2104C) with description lookup
- **Job Functions**: Text-based roles (DL, Leader, etc.)

### Data Constraints
- CSV files must have headers
- Primary keys are string-based (EMP_ID, Dept_Code, etc.)
- Boolean fields use string representation
- No referential integrity enforced at database level
- File locking prevents concurrent write corruption

## Important Constraints

### Technical Constraints (SQLite 版本)
1. **單機部署**: SQLite 為檔案型資料庫，適合單機或區域網路環境
2. **並行存取**: SQLite 支援多人讀取，但寫入時會鎖定整個資料庫檔案
3. **資料量限制**: 適合中小型組織（建議 < 10GB 資料量）
4. **備份簡單**: 只需複製 .db 檔案即可備份
5. **型別安全**: SQLite 動態型別系統，需在應用層確保資料完整性

### Business Constraints
1. **單機/區域網路**: 適合單機或小型辦公室環境
2. **手動備份**: 需建立定期備份機制（可透過腳本自動化）
3. **無內建驗證**: 桌面應用假設在信任環境中使用
4. **Windows 為主**: 路徑處理和啟動腳本以 Windows 為主要平台
5. **功能完整複製**: 必須確保所有 VB 版本的功能都被實現

### Regulatory Considerations
- **Data Privacy**: Employee PII stored in plain text CSV files
- **Access Control**: File system permissions only
- **Audit Trail**: No built-in logging of data changes

## External Dependencies

### Runtime Dependencies
- **PySide6** - Qt for Python (LGPL v3)
- **SQLAlchemy** - MIT licensed (ORM for SQLite)
- **FastAPI/Uvicorn** - MIT licensed (可選 API 功能)
- **Pandas** - BSD licensed (資料分析與匯出)
- **Openpyxl** - MIT licensed (Excel 匯出)
- **Python-dotenv** - BSD licensed (環境設定)

### Data Interoperability
- **Excel Export**: Generated `.xlsx` files compatible with Microsoft Excel, Google Sheets, LibreOffice
- **CSV Format**: UTF-8 encoded, comma-separated, with headers
- **API Output**: JSON format from FastAPI endpoints

### Optional Integrations
- **FastAPI Swagger UI**: Auto-generated at `/docs` when API running
- **FastAPI ReDoc**: Alternative API docs at `/redoc`

## Migration Notes

**從 VB.NET + Access 遷移：**
- 完整分析原有 Access 資料庫結構
- 將所有資料表和關聯轉移到 SQLite 資料庫
- 重構 UI 使用 PySide6，保持原有操作邏輯與介面佈局
- 將 VB 商業邏輯轉換為 Python 服務層
- 完整複製所有功能模組（人事、部門、權限、證照等）

**從 CSV 版本升級到 SQLite：**
- 將現有 CSV 資料匯入 SQLite 資料庫
- 更新 Repository 層使用 SQLAlchemy 或直接 SQL
- 移除 FileLock 相關程式碼（SQLite 內建鎖定機制）
- 利用 SQLite 事務確保資料完整性
- 可透過設定切換資料庫路徑

**SQLite 版本優勢：**
- 支援 ACID 事務，資料更安全
- 支援資料庫層級的關聯完整性
- 效能優於 CSV 處理大量資料
- 支援 SQL 查詢，操作更靈活
- 單一 .db 檔案，易於備份與移植
