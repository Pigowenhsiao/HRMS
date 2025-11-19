import pandas as pd
from pathlib import Path
from datetime import datetime

def df_to_excel(df: pd.DataFrame, out_dir: str = "exports", prefix: str = "report") -> str:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(out_dir) / f"{prefix}_{ts}.xlsx"
    df.to_excel(path, index=False)
    return str(path)
