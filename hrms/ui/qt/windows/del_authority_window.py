from .basic_csv_window import BasicCSVWindow, LookupSpec


class DelAuthorityWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        lookups = {"Account_ID": LookupSpec("Authority.csv", "S_Account")}
        super().__init__("DEL_AUTHORITY.csv", ["Account_ID", "Active"], parent, lookups=lookups)
        self.setWindowTitle("Delete Authority Management")
