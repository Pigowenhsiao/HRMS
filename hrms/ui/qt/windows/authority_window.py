from .basic_csv_window import BasicCSVWindow


class AuthorityWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        super().__init__("Authority.csv", ["S_Account", "Active", "Update_Date", "Auth_type"], parent)
        self.setWindowTitle("Authority Management")
