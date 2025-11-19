from dataclasses import dataclass

@dataclass
class BasicRow:
    EMP_ID: str
    Dept_Code: str | None = None
    C_Name: str | None = None
    Title: str | None = None
    On_Board_Date: str | None = None
    Shift: str | None = None
    Area: str | None = None
    Function: str | None = None
    Meno: str | None = None
    Active: str | None = "true"  # 'true' / 'false'
    VAC_ID: str | None = None
    VAC_DESC: str | None = None
    Start_date: str | None = None
    End_date: str | None = None
    AreaDate: str | None = None
