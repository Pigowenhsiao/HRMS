from .basic_csv_window import BasicCSVWindow


class CertifyTypeWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        super().__init__("CERTIFY_TYPE.csv", ["Certify_Type", "Active"], parent)
        self.setWindowTitle("Certificate Type Management")
