from .basic_csv_window import BasicCSVWindow, LookupSpec


class CertifyItemsWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        columns = [
            "Dept",
            "Certify_ID",
            "Certify_Type",
            "Certify_Name",
            "Certify_time",
            "Certify_Grade",
            "Remark",
            "Active",
            "Score",
        ]
        lookups = {
            "Dept": LookupSpec("L_Section.csv", "Dept_Code", ("Dept_Name",)),
            "Certify_Type": LookupSpec("CERTIFY_TYPE.csv", "Certify_Type"),
            "Certify_Name": LookupSpec("CERTIFY.csv", "Certify", ("Certify_Desc",)),
        }
        super().__init__("CERTIFY_ITEMS.csv", columns, parent, lookups=lookups)
        self.setWindowTitle("Certificate Item Management")
