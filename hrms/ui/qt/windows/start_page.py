from .basic_csv_window import BasicCSVWindow, LookupSpec
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


def make_csv_window(csv_name, columns, lookups=None):
    def _factory(parent):
        return BasicCSVWindow(csv_name, columns, parent, lookups=dict(lookups or {}))

    return _factory


LOOKUP_DEPT = LookupSpec("L_Section.csv", "Dept_Code", ("Dept_Name",))
LOOKUP_AREA = LookupSpec("Area.csv", "Area", ("Area_Desc",))
LOOKUP_JOB = LookupSpec("L_Job.csv", "L_Job")
LOOKUP_SHOP = LookupSpec("SHOP.csv", "SHOP", ("SHOP_DESC",))
LOOKUP_VAC = LookupSpec("VAC_Type.csv", "VAC_ID")
LOOKUP_SHIFT = LookupSpec("SHIFT.csv", "Shift", ("Shift_Desc",))
LOOKUP_EMP = LookupSpec("BASIC.csv", "EMP_ID", ("C_Name",))
LOOKUP_CERTIFY_TYPE = LookupSpec("CERTIFY_TYPE.csv", "Certify_Type")
LOOKUP_CERTIFY_ITEM = LookupSpec("CERTIFY_ITEMS.csv", "Certify_ID", ("Certify_Name",))
LOOKUP_CERTIFY_NAME = LookupSpec("CERTIFY.csv", "Certify", ("Certify_Desc",))


class StartPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HRMS CSV - Start Page")
        cw = QWidget(self)
        lay = QVBoxLayout(cw)

        lay.addWidget(QLabel("HRMS（CSV 後端）/ HRMS (CSV Backend)"))

        # 所有 CSV 檔案與對應視窗
        # CSV definitions for each legacy form
        basic_columns = [
            "EMP_ID",
            "Dept_Code",
            "C_Name",
            "Title",
            "On_Board_date",
            "SHIFT",
            "Shop",
            "Meno",
            "Update_Date",
            "Active",
            "Function",
            "Area",
            "Trans_out_date",
            "Area_date",
            "Start_Date",
            "End_Date",
            "Vac_type",
            "On_Board_Date_2",
            "Certify_Area",
            "Work_Stage",
            "On_Board_Date",
            "Shift",
            "VAC_ID",
        ]
        basic_lookups = {
            "Dept_Code": LOOKUP_DEPT,
            "SHIFT": LOOKUP_SHIFT,
            "Shift": LOOKUP_SHIFT,
            "Shop": LOOKUP_SHOP,
            "Function": LOOKUP_JOB,
            "Area": LOOKUP_AREA,
            "Certify_Area": LOOKUP_AREA,
            "Vac_type": LOOKUP_VAC,
            "VAC_ID": LOOKUP_VAC,
        }
        basic2_columns = [
            "EMP_ID",
            "Dept_Code",
            "C_Name",
            "Title",
            "On_Board_date",
            "SHIFT",
            "Shop",
            "Meno",
            "Update_Date",
            "Function",
            "Area",
            "Certify_Group",
            "Active",
        ]
        basic2_lookups = {
            "Dept_Code": LOOKUP_DEPT,
            "SHIFT": LOOKUP_SHIFT,
            "Shop": LOOKUP_SHOP,
            "Function": LOOKUP_JOB,
            "Area": LOOKUP_AREA,
        }
        basic_backup_columns = [
            "NO_ID",
            "EMP_ID",
            "Dept_Code",
            "C_Name",
            "Title",
            "On_Board_date",
            "SHIFT",
            "Meno",
            "Update_Date",
            "Function",
            "Area",
            "Certify_Group",
            "Active",
            "updater",
            "Vac_type",
            "Start_date",
            "End_date",
        ]
        basic_backup_lookups = {
            "Dept_Code": LOOKUP_DEPT,
            "SHIFT": LOOKUP_SHIFT,
            "Function": LOOKUP_JOB,
            "Area": LOOKUP_AREA,
            "Vac_type": LOOKUP_VAC,
        }
        person_info_columns = [
            "EMP_ID",
            "Sex",
            "Birthday",
            "Personal_ID",
            "address",
            "Person_Phone",
            "EMG_NAME1",
            "EMG_Phone1",
            "EMG_Releasion1",
            "EMG_NAME2",
            "EMG_Phone2",
            "EMG_Releasion2",
            "Living_place",
            "Perf_year",
            "excomp_year",
            "Update_Date",
            "Meno",
            "Active",
            "Home_phone",
            "Current_phone",
            "Cell_phone",
            "Living_Place2",
            "ex_compy_type",
            "Updater_Date",
            "Updater",
            "CUR_PHONE",
        ]
        person_info_backup_columns = [
            "NO_ID",
            "EMP_ID",
            "Sex",
            "Birthday",
            "Personal_ID",
            "Home_Phone",
            "Current_Phone",
            "Cell_Phone",
            "address",
            "Person_Phone",
            "EMG_NAME1",
            "EMG_Phone1",
            "EMG_Releasion1",
            "EMG_NAME2",
            "EMG_Phone2",
            "EMG_Releasion2",
            "Living_place",
            "Living_Place2",
            "Perf_year",
            "excomp_year",
            "ex_compy_type",
            "Update_Date",
            "Meno",
            "Active",
        ]
        shift_columns = ["\u8b58\u5225\u78bc", "Shift", "L_Section", "Shift_Desc", "Active", "Supervisor"]
        self.csv_windows = {
            "TE_BASIC.csv": ("Employee Basic Info (TE_BASIC)", BasicWindow),
            "Area.csv": ("Area (Area)", AreaWindow),
            "L_Section.csv": ("Department (L_Section)", DeptWindow),
            "L_Job.csv": ("Job (L_Job)", JobWindow),
            "VAC_Type.csv": ("Vacation Type (VAC_Type)", VacTypeWindow),
            "TRAINING_RECORD.csv": ("Training Record (TRAINING_RECORD)", TrainingRecordWindow),
            "SHOP.csv": ("Shop (SHOP)", ShopWindow),
            "SOFTWARE.csv": ("Software (SOFTWARE)", SoftwareWindow),
            "CERTIFY.csv": ("Certificate (CERTIFY)", CertifyWindow),
            "CERTIFY_ITEMS.csv": ("Certificate Item (CERTIFY_ITEMS)", CertifyItemsWindow),
            "CERTIFY_RECORD.csv": ("Certificate Record (CERTIFY_RECORD)", CertifyRecordWindow),
            "CERTIFY_TOOL_MAP.csv": ("Certificate Tool Map (CERTIFY_TOOL_MAP)", CertifyToolMapWindow),
            "CERTIFY_TYPE.csv": ("Certificate Type (CERTIFY_TYPE)", CertifyTypeWindow),
            "DEL_AUTHORITY.csv": ("Delete Authority (DEL_AUTHORITY)", DelAuthorityWindow),
            "Authority.csv": ("Authority (Authority)", AuthorityWindow),
            "BASIC.csv": ("Employee Basic Info (BASIC)", make_csv_window("BASIC.csv", basic_columns, basic_lookups)),
            "BASIC2.csv": ("Employee Basic Info 2 (BASIC2)", make_csv_window("BASIC2.csv", basic2_columns, basic2_lookups)),
            "BASIC_BACKUP.csv": ("Employee Basic Info Backup (BASIC_BACKUP)", make_csv_window("BASIC_BACKUP.csv", basic_backup_columns, basic_backup_lookups)),
            "PERSON_INFO.csv": ("Employee Info (PERSON_INFO)", make_csv_window("PERSON_INFO.csv", person_info_columns, {"EMP_ID": LOOKUP_EMP})),
            "PERSON_INFO_BACKUP.csv": ("Employee Info Backup (PERSON_INFO_BACKUP)", make_csv_window("PERSON_INFO_BACKUP.csv", person_info_backup_columns, {"EMP_ID": LOOKUP_EMP})),
            "SHIFT.csv": ("Shift (SHIFT)", make_csv_window("SHIFT.csv", shift_columns, {"L_Section": LOOKUP_DEPT})),
            "MUST_TOOL.csv": ("Must Tool (MUST_TOOL)", MustToolWindow),
            "TE_EDU.csv": ("Education (TE_EDU)", make_csv_window("TE_EDU.csv", ["EMP_ID","Education","G_School","Major"], {"EMP_ID": LOOKUP_EMP})),
            "TE_LOCATION.csv": ("Location (TE_LOCATION)", make_csv_window("TE_LOCATION.csv", ["EMP_ID","Certify_Area","Active"], {"EMP_ID": LOOKUP_EMP, "Certify_Area": LOOKUP_AREA})),
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
