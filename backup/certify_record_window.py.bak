from .basic_csv_window import BasicCSVWindow, LookupSpec


class CertifyRecordWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        columns = ["\u8b58\u5225\u78bc", "EMP_ID", "Certify_NO", "Update_date", "Active", "Meno", "Type"]
        lookups = {
            "EMP_ID": LookupSpec("BASIC.csv", "EMP_ID", ("C_Name",)),
            "Certify_NO": LookupSpec("CERTIFY_ITEMS.csv", "Certify_ID", ("Certify_Name",)),
            "Type": LookupSpec("CERTIFY_TYPE.csv", "Certify_Type"),
        }
        super().__init__("CERTIFY_RECORD.csv", columns, parent, lookups=lookups)
        self.setWindowTitle("Certificate Record Management")
