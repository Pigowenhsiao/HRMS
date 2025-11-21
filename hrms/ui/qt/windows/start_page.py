from .basic_csv_window import BasicCSVWindow
from .certify_type_window import CertifyTypeWindow
from .del_authority_window import DelAuthorityWindow
from .certify_record_window import CertifyRecordWindow
from .certify_tool_map_window import CertifyToolMapWindow
from .certify_window import CertifyWindow
from .certify_items_window import CertifyItemsWindow
from .shop_window import ShopWindow
from .software_window import SoftwareWindow
from .vac_type_window import VacTypeWindow
from .training_record_window import TrainingRecordWindow
from .job_window import JobWindow
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from .authority_window import AuthorityWindow
from .must_tool_window import MustToolWindow
from .basic_window import BasicWindow
from .area_window import AreaWindow
from .dept_window import DeptWindow

class StartPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HRMS CSV - Start Page")
        cw = QWidget(self)
        lay = QVBoxLayout(cw)

        lay.addWidget(QLabel("HRMS（CSV 後端）"))

        # 所有 CSV 檔案與對應視窗
        self.csv_windows = {
            "TE_BASIC.csv": ("員工基本資料（TE_BASIC）", BasicWindow),
            "Area.csv": ("區域（Area）", AreaWindow),
            "L_Section.csv": ("部門（L_Section）", DeptWindow),
            "L_Job.csv": ("職務（L_Job）", JobWindow),
            "VAC_Type.csv": ("假別（VAC_Type）", VacTypeWindow),
            "TRAINING_RECORD.csv": ("培訓紀錄（TRAINING_RECORD）", TrainingRecordWindow),
            "SHOP.csv": ("廠區（SHOP）", ShopWindow),
            "SOFTWARE.csv": ("軟體（SOFTWARE）", SoftwareWindow),
            "CERTIFY.csv": ("證照（CERTIFY）", CertifyWindow),
            "CERTIFY_ITEMS.csv": ("證照項目（CERTIFY_ITEMS）", CertifyItemsWindow),
            "CERTIFY_RECORD.csv": ("證照紀錄（CERTIFY_RECORD）", CertifyRecordWindow),
            "CERTIFY_TOOL_MAP.csv": ("證照工具對應（CERTIFY_TOOL_MAP）", CertifyToolMapWindow),
            "CERTIFY_TYPE.csv": ("證照類型（CERTIFY_TYPE）", CertifyTypeWindow),
            "DEL_AUTHORITY.csv": ("刪除權限（DEL_AUTHORITY）", DelAuthorityWindow),
            "Authority.csv": ("權限（Authority）", AuthorityWindow),
            "BASIC.csv": ("人員基本資料（BASIC）", lambda parent: BasicCSVWindow("BASIC.csv", ["EMP_ID","Dept_Code","C_Name","Title","On_Board_date","SHIFT","Shop","Meno","Update_Date","Active","Function","Area","Trans_out_date","Area_date","Start_Date","End_Date","Vac_type","On_Board_Date_2","Certify_Area","Work_Stage","On_Board_Date","Shift","VAC_ID"], parent)),
            "BASIC2.csv": ("人員基本資料2（BASIC2）", lambda parent: BasicCSVWindow("BASIC2.csv", ["EMP_ID","Dept_Code","C_Name","Title","On_Board_date","SHIFT","Shop","Meno","Update_Date","Function","Area","Certify_Group","Active"], parent)),
            "BASIC_BACKUP.csv": ("人員基本資料備份（BASIC_BACKUP）", lambda parent: BasicCSVWindow("BASIC_BACKUP.csv", ["NO_ID","EMP_ID","Dept_Code","C_Name","Title","On_Board_date","SHIFT","Meno","Update_Date","Function","Area","Certify_Group","Active","updater","Vac_type","Start_date","End_date"], parent)),
            "PERSON_INFO.csv": ("人員資訊（PERSON_INFO）", lambda parent: BasicCSVWindow("PERSON_INFO.csv", ["EMP_ID","Sex","Birthday","Personal_ID","address","Person_Phone","EMG_NAME1","EMG_Phone1","EMG_Releasion1","EMG_NAME2","EMG_Phone2","EMG_Releasion2","Living_place","Perf_year","excomp_year","Update_Date","Meno","Active","Home_phone","Current_phone","Cell_phone","Living_Place2","ex_compy_type","Updater_Date","Updater","CUR_PHONE"], parent)),
            "PERSON_INFO_BACKUP.csv": ("人員資訊備份（PERSON_INFO_BACKUP）", lambda parent: BasicCSVWindow("PERSON_INFO_BACKUP.csv", ["NO_ID","EMP_ID","Sex","Birthday","Personal_ID","Home_Phone","Current_Phone","Cell_Phone","address","Person_Phone","EMG_NAME1","EMG_Phone1","EMG_Releasion1","EMG_NAME2","EMG_Phone2","EMG_Releasion2","Living_place","Living_Place2","Perf_year","excomp_year","ex_compy_type","Update_Date","Meno","Active"], parent)),
            "SHIFT.csv": ("班別（SHIFT）", lambda parent: BasicCSVWindow("SHIFT.csv", ["識別碼","Shift","L_Section","Shift_Desc","Active","Supervisor"], parent)),
            "MUST_TOOL.csv": ("必備工具（MUST_TOOL）", MustToolWindow),
            "TE_EDU.csv": ("教育訓練（TE_EDU）", lambda parent: BasicCSVWindow("TE_EDU.csv", ["EMP_ID","Education","G_School","Major"], parent)),
            "TE_LOCATION.csv": ("地點（TE_LOCATION）", lambda parent: BasicCSVWindow("TE_LOCATION.csv", ["EMP_ID","Certify_Area","Active"], parent)),
        }

        for fname, (label, wincls) in self.csv_windows.items():
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, f=fname, w=wincls: self.open_window(f, w))
            lay.addWidget(btn)

        cw.setLayout(lay)
        self.setCentralWidget(cw)

    def open_window(self, fname, wincls):
        if wincls is not None:
            dlg = wincls(self)
            dlg.exec()
        else:
            from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout
            dlg = QDialog(self)
            dlg.setWindowTitle(f"{fname} 管理介面（尚未實作）")
            lay = QVBoxLayout(dlg)
            lay.addWidget(QLabel(f"{fname} 管理介面尚未實作，請稍後。"))
            dlg.setLayout(lay)
            dlg.exec()
