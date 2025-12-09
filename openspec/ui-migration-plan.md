# HRMS UI 遷移策略與工作計畫

**文件版本**：1.0  
**制定日期**：2025-12-09  
**目標**：將現有 CSV-based UI 遷移至 SQLite + SQLAlchemy，同時改善使用者體驗

---

## 一、現狀分析

### 1.1 現有 UI 結構

```
現有 UI 類型：
├─ 自訂視窗（Custom Windows）
│  ├─ BasicWindow（員工基本資料）
│  ├─ CertifyRecordWindow（證照記錄）
│  └─ start_page.py（主選單）
│
└─ 通用視窗（Generic CSV Windows）
   └─ BasicCSVWindow（其他所有資料表）
      ├─ AreaWindow
      ├─ DeptWindow
      ├─ JobWindow
      ├─ VacTypeWindow
      ├─ TrainingRecordWindow
      ├─ ...等 10+ 個功能
```

### 1.2 現有技術
- **框架**：PySide6 (Qt for Python)
- **資料存取**：直接呼叫 `hrms.persons.service` 和 `hrms.lookups.service`
- **表格元件**：QTableWidget（適合小量資料，但不支援虛擬滾動）
- **表單驗證**：無（直接寫入 CSV）
- **資料綁定**：無（手動填入/讀取）

### 1.3 現有問題
1. **效能問題**：QTableWidget 載入大量資料（>500筆）時卡頓
2. **資料驗證**：前端無驗證，錯誤資料直接寫入檔案
3. **使用者體驗**：
   - 欄位名稱顯示英文（如 EMP_ID, Dept_Code）
   - 無搜尋/篩選功能
   - 無分頁功能
   - 日期格式不一致
4. **維護困難**：每個視窗資料存取邏輯分散
5. **無 Transaction**：失敗時無 Rollback 機制

---

## 二、遷移目標與原則

### 2.1 核心目標
1. **完整功能保留**：所有 VB 版本功能必須完整實現
2. **單機版作業**：保持桌面應用特性，無需網路
3. **資料完整性**：使用 SQLite Transaction 確保資料安全
4. **使用者體驗提升**：現代化介面，改善操作流暢度

### 2.2 設計原則

#### ✅ **應該做的**
- 使用 Repository Pattern 統一資料存取
- 實作資料驗證（必填欄位、格式檢查）
- 優化大量資料顯示（虛擬滾動或分頁）
- 提供搜尋與篩選功能
- 改善錯誤訊息（中文、友善）
- 保持操作習慣（與 VB 版本類似）
- 欄位顯示中文名稱

#### ❌ **不應該做的**
- 改變核心商業邏輯
- 移除必要欄位或功能
- 強迫使用者改變操作流程
- 過度複雜化架構
- 引入不必要的網路功能

---

## 三、技術架構設計

### 3.1 分層架構

```
UI 層（PySide6）
    ↓
Presentation Layer（ViewModels）
    ↓
Service Layer（Business Logic）
    ↓
Repository Layer（Data Access）
    ↓
SQLite Database（SQLAlchemy ORM）
```

### 3.2 新 UI 元件選擇

| 功能 | 現有元件 | 建議元件 | 原因 |
|------|---------|----------|------|
| 資料表格 | QTableWidget | **QTableView** + **QStandardItemModel** | 支援虛擬滾動，效能更好 |
| 下拉選單 | QComboBox | **QComboBox** + **QCompleter** | 保持不變，但加入自動完成 |
| 日期輸入 | QLineEdit | **QDateEdit** | 內建日期驗證與選擇器 |
| 表單佈局 | QFormLayout | **QFormLayout** + **QGroupBox** | 更好視覺分組 |
| 主視窗 | QDialog | **QMainWindow** + **QDockWidget** | 可視窗停靠，更靈活 |
| 資料篩選 | 無 | **QLineEdit** + **QSortFilterProxyModel** | 即時篩選 |
| 分頁 | 無 | **手動分頁** | 大量資料時提升效能 |

### 3.3 資料綁定策略

**建議**：使用 **手動綁定**（不引入複雜的 ViewModel）

原因：
- 專案規模不大（<20 個視窗）
- 避免增加學習曲線
- PySide 的資料綁定不如 WPF 成熟
- 手動綁定更靈活，易於偵錯

---

## 四、遷移策略：分階段實施

### 📊 **階段 0：基礎建設（先決條件）**
**預估時間**：4-6 小時

```
完成 Repository 層和 Service 層
│
├─ 實作 BaseRepository（包含 CRUD）
├─ 為每個模型建立 Repository
├─ 實作 LookupService（對照表服務）
├─ 實作 EmployeeService（員工管理）
├─ 實作 CertificationService（證照管理）
└─ 實作 UnitOfWork（事務管理）
```

**重要性**：⭐⭐⭐⭐⭐（必須先完成）

---

### 🎯 **階段 1：核心功能（MVP）**
**預估時間**：8-12 小時

**目標**：實作最常用的核心功能，確保系統可用

```
1.1 員工基本資料管理（BASIC）
    ├─ 更新 BasicWindow 使用 SQLite
    ├─ 實作資料驗證（必填欄位）
    ├─ 實作搜尋功能（依 EMP_ID, C_Name）
    ├─ 實作分頁（每頁 50 筆）
    └─ 資料變動日誌（選擇性）

1.2 部門管理（L_Section）
    ├─ 更新 DeptWindow 使用 SQLite
    ├─ 實作外鍵檢查（刪除時檢查是否有員工）
    └─ 實作快速搜尋

1.3 區域管理（Area）
    ├─ 更新 AreaWindow 使用 SQLite
    └─ 實作 Active/Inactive 篩選

1.4 職務管理（L_Job）
    ├─ 更新 JobWindow 使用 SQLite
    └─ 簡單 CRUD 功能

1.5 系統設定與主選單
    ├─ 更新 start_page.py
    ├─ 資料庫連線設定
    └─ 顯示目前資料庫位置
```

**完成標準**：
- ✅ 可管理員工基本資料
- ✅ 可操作部門/區域/職務對照表
- ✅ 資料正確寫入 SQLite
- ✅ 可匯出 Excel

**優先級**：⭐⭐⭐⭐⭐（最高）

---

### 🎓 **階段 2：證照與訓練管理**
**預估時間**：6-8 小時

```
2.1 證照項目管理（CERTIFY_ITEMS）
    ├─ 更新 CertifyItemsWindow
    ├─ 依部門分類顯示
    └─ 實作證照分級（Grade）

2.2 證照記錄管理（TRAINING_RECORD）
    ├─ 更新 TrainingRecordWindow
    ├─ 依員工篩選證照
    ├─ 證照到期提醒（選擇性）
    └─ 實作批次匯入（選擇性）

2.3 證照工具對應（CERTIFY_TOOL_MAP）
    ├─ 更新 CertifyToolMapWindow
    └─ 顯示證照與工具關係

2.4 證照狀態對照（CERTIFY）
    ├─ 更新 CertifyWindow
    └─ 簡單 CRUD

2.5 證照類型對照（CERTIFY_TYPE）
    ├─ 更新 CertifyTypeWindow
    └─ 簡單 CRUD
```

**完成標準**：
- ✅ 可管理證照項目
- ✅ 可記錄員工證照
- ✅ 可維護證照工具對應

**優先級**：⭐⭐⭐⭐（高）- 證照是核心功能

---

### ⚙️ **階段 3：進階功能**
**預估時間**：4-6 小時

```
3.1 班別管理（SHIFT）
    ├─ 更新 ShiftWindow
    └─ 與部門關聯

3.2 工站管理（SHOP）
    ├─ 更新 ShopWindow
    └─ 簡單 CRUD

3.3 假別管理（VAC_Type）
    ├─ 更新 VacTypeWindow
    └─ 簡單 CRUD

3.4 必需工具（MUST_TOOL）
    ├─ 更新 MustToolWindow
    └─ 簡單 CRUD

3.5 軟體版本（SOFTWARE）
    └─ 更新 SoftwareWindow
```

**完成標準**：
- ✅ 所有對照表可維護
- ✅ 系統功能完整

**優先級**：⭐⭐⭐（中）- 對照表相對簡單

---

### 🔐 **階段 4：權限與安全**
**預估時間**：3-4 小時

```
4.1 使用者權限（Authority）
    ├─ 更新 AuthorityWindow
    ├─ Auth_type 01=Admin, 02=User
    └─ 實作角色檢查

4.2 刪除權限（DEL_AUTHORITY）
    ├─ 更新 DelAuthorityWindow
    └─ 控制刪除權限

4.3 登入介面（選擇性）
    ├─ 簡單登入視窗
    └─ 紀錄目前使用者
```

**完成標準**：
- ✅ 可管理使用者權限
- ✅ 刪除操作受權限控制

**優先級**：⭐⭐（低）- 單機版可後期再加入

---

### 🧪 **階段 5：測試與優化**
**預估時間**：4-6 小時

```
5.1 功能測試
    ├─ 測試所有 CRUD 操作
    ├─ 測試外鍵約束
    └─ 測試資料驗證

5.2 效能測試
    ├─ 載入 10,000+ 筆資料測試
    ├─ 測試搜尋/篩選速度
    └─ 測試同時開啟多視窗

5.3 使用者測試
    ├─ 與 VB 版本操作比較
    ├─ 收集使用者回饋
    └─ 修正易用性問題

5.4 最終優化
    ├─ 調整 UI 佈局
    ├─ 改善錯誤訊息
    └─ 增加快速鍵
```

**優先級**：⭐⭐⭐⭐（高）- 確保品質

---

## 五、UI 現代化建議

### 5.1 視窗佈局優化

**目前**：所有視窗都是獨立 QDialog

**建議**：
- 主視窗使用 **QMainWindow**
- 功能改為 **QDockWidget** 或可切換的 Central Widget
- 提供 **Tab 頁籤** 同時開啟多個功能
- 增加 **ToolBar** 快速工具列

**優點**：
- 使用者可同時查看多個資料表
- 更符合現代桌面應用習慣
- 提升操作效率

### 5.2 資料表格優化

**目前**：QTableWidget 手動填入

**建議**：
```python
# 使用 QTableView + Model
self.table_view = QTableView()
self.model = QStandardItemModel()
self.proxy_model = QSortFilterProxyModel()
self.proxy_model.setSourceModel(self.model)
self.table_view.setModel(self.proxy_model)

# 優點：
# - 虛擬滾動，效能更好
# - 內建排序
# - 支援篩選
# - 資料與顯示分離
```

### 5.3 搜尋與篩選

**建議實作**：
- **即時搜尋**：QLineEdit + QSortFilterProxyModel
- **進階篩選**：多條件組合（部門 + 狀態 + 日期範圍）
- **快速篩選**：常用條件設為按鈕（如：僅顯示在職）

### 5.4 資料驗證

**必填欄位檢查**：
```python
def validate_form(self):
    errors = []
    if not self.emp_id.text().strip():
        errors.append("員工編號不可空白")
    if not self.name.text().strip():
        errors.append("姓名不可空白")
    # ...其他驗證

    if errors:
        QMessageBox.warning(self, "資料驗證失敗", "\n".join(errors))
        return False
    return True
```

**格式驗證**：
- 日期格式（YYYY-MM-DD）
- 員工編號格式
- 電話格式（選擇性）

### 5.5 欄位顯示優化

**中文欄位名稱對映**：
```python
COLUMN_LABELS = {
    "EMP_ID": "員工編號",
    "Dept_Code": "部門代碼",
    "C_Name": "姓名",
    "Title": "職稱",
    "On_Board_Date": "到職日",
    "Shift": "班別",
    "Area": "區域",
    "Function": "職務",
    "Active": "在職"
}
```

**日期顯示**：
- 儲存：保持 YYYY-MM-DD 字串
- 顯示：格式化為 "YYYY年MM月DD日"

### 5.6 效能優化

**大量資料處理**：
- 使用 LIMIT 分頁載入
- 避免一次載入所有資料
- 實作「更多...」按鈕或滾動載入

**建議分頁邏輯**：
```python
PAGE_SIZE = 50
current_page = 1

def load_page(self, page):
    offset = (page - 1) * PAGE_SIZE
    rows = employee_repo.list(offset=offset, limit=PAGE_SIZE)
    self.populate_table(rows)
```

---

## 六、詳細工作分解（WBS）

### 📋 **工作 0：基礎建設（Repository 層）**
**預估工時**：4-6 小時

#### 0.1 建立 Repository 基礎類別
- [ ] 設計 BaseRepository 介面（2 小時）
  - list(filters, limit, offset)
  - get_by_pk(pk)
  - upsert(data)
  - delete(pk)
  - count(filters)
  - exists(pk)

- [ ] 實作 BaseRepositorySQLAlchemy（2 小時）
  - 使用 SQLAlchemy Session
  - 實現通用 CRUD 邏輯
  - 處理例外狀況

#### 0.2 建立各模型 Repository
- [ ] BasicRepository（0.5 小時）
  - 實作員工查詢（依部門、狀態篩選）
  - 支援模糊搜尋（姓名）

- [ ] PersonInfoRepository（0.5 小時）
  - 一對一關係處理

- [ ] LookupRepository（1 小時）
  - SectionRepository
  - AreaRepository
  - JobRepository
  - VacTypeRepository
  - ShiftRepository
  - ShopRepository

- [ ] CertificationRepository（1 小時）
  - CertifyItemRepository
  - TrainingRecordRepository
  - 證照記錄查詢（依員工、日期）

- [ ] AuthorityRepository（0.5 小時）
  - AuthorityRepository
  - DelAuthorityRepository

#### 0.3 Service 層實作
- [ ] LookupService（0.5 小時）
  - 提供下拉選單資料
  - 快取對照表（提升效能）

- [ ] EmployeeService（1 小時）
  - 封裝員工相關操作
  - 處理 BASIC + PERSON_INFO 關聯

- [ ] CertificationService（1 小時）
  - 證照記錄管理
  - 證照項目維護

#### 0.4 UnitOfWork 實作
- [ ] 建立 UnitOfWork（0.5 小時）
  - Session 管理
  - Transaction 控制
  - 自動 Rollback

---

### 🎨 **工作 1：核心 UI 遷移**
**預估工時**：8-12 小時

#### 1.1 更新 BasicWindow（員工管理）
**工時**：4-5 小時

- [ ] 1.1.1 更新資料存取邏輯（1 小時）
  - 從 CSV Service 改為 EmployeeRepository
  - 修改 load/save/delete 方法

- [ ] 1.1.2 實作資料驗證（1 小時）
  - EMP_ID 必填檢查
  - C_Name 必填檢查
  - 日期格式驗證（On_Board_Date）

- [ ] 1.1.3 新增搜尋功能（1 小時）
  - 依 EMP_ID 精確搜尋
  - 依 C_Name 模糊搜尋
  - 依部門篩選

- [ ] 1.1.4 實作分頁（1 小時）
  - 每頁 50 筆資料
  - 上一頁/下一頁按鈕
  - 跳轉到指定頁碼

- [ ] 1.1.5 UI 優化（0.5 小時）
  - 欄位顯示中文名稱
  - 改善錯誤訊息

- [ ] 1.1.6 測試（0.5 小時）
  - CRUD 操作測試
  - 驗證邏輯測試
  - 分頁功能測試

#### 1.2 更新 DeptWindow（部門管理）
**工時**：1-1.5 小時

- [ ] 1.2.1 更新資料存取（0.5 小時）
  - 改用 SectionRepository

- [ ] 1.2.2 實作外鍵檢查（0.5 小時）
  - 刪除時檢查 BASIC.Dept_Code
  - 若仍有員工，禁止刪除

- [ ] 1.2.3 新增快速搜尋（0.5 小時）
  - 依部門代碼搜尋
  - 依部門名稱搜尋

#### 1.3 更新 AreaWindow（區域管理）
**工時**：1 小時

- [ ] 1.3.1 更新資料存取（0.5 小時）
  - 改用 AreaRepository

- [ ] 1.3.2 新增狀態篩選（0.5 小時）
  - 僅顯示 Active 的區域
  - 顯示全部/僅顯示停用

#### 1.4 更新 JobWindow（職務管理）
**工時**：0.5 小時

- [ ] 1.4.1 更新資料存取（0.5 小時）
  - 改用 JobRepository
  - CRUD 功能測試

#### 1.5 更新主選單
**工時**：1 小時

- [ ] 1.5.1 更新 start_page.py（0.5 小時）
  - 移除 CSV 後端相關程式碼
  - 改為顯示 SQLite 資料庫位置

- [ ] 1.5.2 改善佈局（0.5 小時）
  - 按功能分組（員工、證照、對照表、權限）
  - 關閉視窗時刷新列表

#### 1.6 整合測試
**工時**：1-2 小時

- [ ] 1.6.1 功能測試（1 小時）
  - 確保所有 CRUD 操作正常
  - 確認外鍵約束有效

- [ ] 1.6.2 使用性測試（0.5 小時）
  - 確認操作流程順暢

---

### 🎓 **工作 2：證照管理 UI 遷移**
**預估工時**：6-8 小時

#### 2.1 更新 CertifyItemsWindow（證照項目）
**工時**：2 小時

- [ ] 2.1.1 更新資料存取（0.5 小時）
  - 改用 CertifyItemRepository

- [ ] 2.1.2 依部門分類顯示（1 小時）
  - 左側：部門樹狀清單
  - 右側：該部門的證照項目

- [ ] 2.1.3 顯示證照分級（0.5 小時）
  - Certify_Grade 顏色標示

#### 2.2 更新 TrainingRecordWindow（證照記錄）
**工時**：3-4 小時

- [ ] 2.2.1 更新資料存取（1 小時）
  - 改用 TrainingRecordRepository
  - 支援依員工篩選
  - 支援依日期範圍篩選

- [ ] 2.2.2 實作進階篩選（1 小時）
  - 員工篩選（下拉選單）
  - 證照類型篩選
  - 證照日期範圍

- [ ] 2.2.3 證照到期提醒（1 小時，選擇性）
  - 計算到期日（Certify_date + Certify_time）
  - 30 天內到期標示紅色

- [ ] 2.2.4 批次操作（1 小時，選擇性）
  - 批次新增證照
  - 批次更新狀態

#### 2.3 更新 CertifyToolMapWindow（證照工具對應）
**工時**：1 小時

- [ ] 2.3.1 更新資料存取（0.5 小時）
  - 改用 CertifyToolMapRepository

- [ ] 2.3.2 顯示關聯關係（0.5 小時）
  - 證照名稱 + 工具名稱

#### 2.4 更新 CertifyTypeWindow
**工時**：0.5 小時

- [ ] 2.4.1 更新資料存取（0.5 小時）
  - 改用 CertifyTypeRepository

#### 2.5 測試
**工時**：1 小時

- [ ] 2.5.1 功能測試（1 小時）
  - 證照項目 CRUD
  - 證照記錄 CRUD
  - 篩選功能測試

---

### ⚙️ **工作 3：進階功能 UI 遷移**
**預估工時**：4-6 小時

#### 3.1 更新 ShiftWindow（班別）
**工時**：1 小時

- [ ] 3.1.1 更新資料存取（0.5 小時）
  - 改用 ShiftRepository

- [ ] 3.1.2 顯示部門關聯（0.5 小時）
  - 顯示 L_Section.Dept_Name

#### 3.2 更新 ShopWindow（工站）
**工時**：0.5 小時

- [ ] 3.2.1 更新資料存取（0.5 小時）
  - 改用 ShopRepository

#### 3.3 更新 VacTypeWindow（假別）
**工時**：0.5 小時

- [ ] 3.3.1 更新資料存取（0.5 小時）
  - 改用 VacTypeRepository

#### 3.4 更新 MustToolWindow
**工時**：0.5 小時

- [ ] 3.4.1 更新資料存取（0.5 小時）
  - 改用 MustToolRepository

#### 3.5 更新 SoftwareWindow
**工時**：0.5 小時

- [ ] 3.5.1 更新資料存取（0.5 小時）
  - 改用 SoftwareRepository

#### 3.6 整合測試
**工時**：2 小時

- [ ] 3.6.1 所有對照表測試（2 小時）
  - CRUD 操作
  - 外鍵檢查

---

### 🔐 **工作 4：權限管理 UI 遷移**
**預估工時**：3-4 小時

#### 4.1 更新 AuthorityWindow
**工時**：1.5 小時

- [ ] 4.1.1 更新資料存取（0.5 小時）
  - 改用 AuthorityRepository

- [ ] 4.1.2 角色管理（1 小時）
  - Auth_type 01=Admin, 02=User
  - 不同角色可見功能不同

#### 4.2 更新 DelAuthorityWindow
**工時**：1 小時

- [ ] 4.2.1 更新資料存取（0.5 小時）
  - 改用 DelAuthorityRepository

- [ ] 4.2.2 刪除權限檢查（0.5 小時）
  - 在刪除操作前檢查權限
  - 無權限時禁用刪除按鈕

#### 4.3 登入介面（選擇性）
**工時**：1.5 小時

- [ ] 4.3.1 建立 LoginDialog（1 小時）
  - 帳號密碼輸入
  - 驗證Authority.Active

- [ ] 4.3.2 整合到啟動流程（0.5 小時）
  - 登入成功後顯示主選單

---

### 🧪 **工作 5：測試與優化**
**預估工時**：4-6 小時

#### 5.1 功能測試
**工時**：2 小時

- [ ] 5.1.1 測試所有 CRUD 操作（1 小時）
  - 新增、讀取、更新、刪除
  - 確認資料正確寫入 SQLite

- [ ] 5.1.2 測試外鍵約束（1 小時）
  - 刪除部門時檢查員工
  - 刪除證照項目時檢查記錄

#### 5.2 效能測試
**工時**：2 小時

- [ ] 5.2.1 大量資料測試（1 小時）
  - 載入 10,000 筆證照記錄
  - 測試分頁功能
  - 測試篩選速度

- [ ] 5.2.2 同時操作測試（1 小時）
  - 開啟多個視窗
  - 同時進行 CRUD 操作

#### 5.3 使用者測試（可選）
**工時**：1-2 小時

- [ ] 5.3.1 實際操作測試（1 小時）
  - 邀請實際使用者測試
  - 比較與 VB 版本的操作流暢度

#### 5.4 最終優化
**工時**：1 小時

- [ ] 5.4.1 改善錯誤訊息（0.5 小時）
  - 中文錯誤訊息
  - 友善提示

- [ ] 5.4.2 增加快速鍵（0.5 小時）
  - Ctrl+S 儲存
  - Ctrl+N 新增
  - Ctrl+F 搜尋

---

## 七、總工作量預估

| 階段 | 工作項目 | 預估工時 |
|------|---------|----------|
| 0 | Repository 基礎建設 | 4-6 小時 |
| 1 | 核心功能 UI 遷移 | 8-12 小時 |
| 2 | 證照管理 UI 遷移 | 6-8 小時 |
| 3 | 進階功能 UI 遷移 | 4-6 小時 |
| 4 | 權限管理 UI 遷移 | 3-4 小時 |
| 5 | 測試與優化 | 4-6 小時 |
| **總計** | **全部完成** | **29-42 小時** |

### 時間分配建議
- **連續開發**：約 5-6 個工作日（每天 8 小時）
- **兼職開發**：約 2-3 週（每天 4 小時）

---

## 八、風險與因應措施

### 風險 1：外鍵約束導致的操作失敗
**風險**：刪除部門時因有員工參考而失敗

**因應**：
- 刪除前檢查關聯資料
- 提供清晰的錯誤訊息
- 建議先處理關聯資料

### 風險 2：資料驗證過於嚴格
**風險**：舊有資料不符合新規則，導致無法儲存

**因應**：
- 分階段實施驗證
- 先警告，後禁止
- 提供資料清理工具

### 風險 3：效能問題
**風險**：TRAINING_RECORD（9,605筆）載入慢

**因應**：
- 強制分頁（每頁 50 筆）
- 使用 QTableView 取代 QTableWidget
- 實作虛擬滾動

### 風險 4：使用者抗拒改變
**風險**：使用者習慣 VB 介面，不願改變

**因應**：
- 保持操作邏輯一致
- 提供操作手冊
- 保留舊系統作為備份

---

## 九、成功標準

### 功能完整性
- [ ] 所有 20+ 個功能模組正常運作
- [ ] CRUD 操作無錯誤
- [ ] 外鍵約束有效運作
- [ ] 資料驗證正常運作

### 資料正確性
- [ ] 所有 10,868 筆資料正確遷移
- [ ] 關聯關係正確無誤
- [ ] 資料查詢結果正確

### 使用者體驗
- [ ] 操作流暢，無卡頓
- [ ] 錯誤訊息清晰易懂
- [ ] 操作流程符合預期

### 系統穩定性
- [ ] 連續操作 1 小時無當機
- [ ] 同時開啟 5+ 視窗正常
- [ ] 資料庫連線穩定

---

## 十、建議的開發順序

### 階段 0：基礎建設（必須先完成）
**時間點**：立即開始
**重要性**：⭐⭐⭐⭐⭐

### 階段 1：核心功能（MVP）
**時間點**：Repository 完成後
**重要性**：⭐⭐⭐⭐⭐
**建議**：1-2 個工作日完成

### 階段 2：證照管理（高優先）
**時間點**：核心功能完成後
**重要性**：⭐⭐⭐⭐
**建議**：1 個工作日完成

### 階段 3-4：進階功能與權限
**時間點**：證照完成後
**重要性**：⭐⭐⭐
**建議**：2-3 個工作日完成

### 階段 5：測試與優化
**時間點**：所有功能完成後
**重要性**：⭐⭐⭐⭐
**建議**：1 個工作日完成

---

## 十一、交付成果

### 程式碼
- [ ] 完整的 Repository 層（8+ 個 Repository）
- [ ] 完整的 Service 層（3+ 個 Services）
- [ ] 更新的 UI 層（17+ 個視窗）
- [ ] 資料庫執行檔（hrms.db）

### 文件
- [ ] UI 操作手冊
- [ ] 資料庫結構說明
- [ ] 部署指南

### 測試
- [ ] 功能測試報告
- [ ] 效能測試報告
- [ ] 使用者測試回饋

---

## 十二、結論

**UI 遷移是從 CSV 轉向 SQLite 的關鍵步驟**，建議採用分階段實施策略，優先完成核心功能（員工管理、部門/區域/職務對照表），再逐步擴展到證照管理和其他功能。

**關鍵成功因素**：
1. 先完成穩固的 Repository 層
2. 保持操作邏輯與 VB 版本一致
3. 重視資料驗證與錯誤處理
4. 充分測試，特別是外鍵約束

**預估總工時**：29-42 小時  
**預估完成時間**：5-6 個工作日（全職）或 2-3 週（兼職）

---

**文件制定**：2025-12-09  
**制定者**：HRMS 開發團隊
