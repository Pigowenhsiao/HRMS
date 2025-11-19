## Access → CSV 匯出與檢核（scripts）

### 匯出 Access 資料表為 CSV
```bash
# 方式一：指定 .mdb/.accdb 路徑
python scripts/access_to_csv_export.py --mdb "C:\path\HRMS.mdb" --out ./data

# 方式二：指定 DSN（需先在 ODBC 管理員建立）
python scripts/access_to_csv_export.py --dsn MyAccessDSN --out ./data

# 只匯出特定表
python scripts/access_to_csv_export.py --mdb "C:\path\HRMS.mdb" --tables BASIC,Person_Info
```
> 可透過 `config/access_csv_mapping.yaml` 控制表名與欄位對應/順序。

### 檢核 CSV 欄位
```bash
python scripts/csv_schema_check.py --data ./data --spec config/csv_schema.yaml
```
> 若有缺欄/多欄/主鍵空白，腳本會回報並以非 0 退出碼結束（可用於 CI）。