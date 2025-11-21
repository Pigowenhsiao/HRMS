from .basic_csv_window import BasicCSVWindow, LookupSpec


class CertifyToolMapWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        columns = ["Certify_ID", "TOOL_ID", "Update_date", "Remark", "Active"]
        lookups = {
            "Certify_ID": LookupSpec("CERTIFY_ITEMS.csv", "Certify_ID", ("Certify_Name",)),
            "TOOL_ID": LookupSpec("MUST_TOOL.csv", "Tool_ID"),
        }
        super().__init__("CERTIFY_TOOL_MAP.csv", columns, parent, lookups=lookups)
        self.setWindowTitle("Certificate Tool Map Management")
