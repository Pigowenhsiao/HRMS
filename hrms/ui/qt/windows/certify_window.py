from .basic_csv_window import BasicCSVWindow


class CertifyWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        super().__init__("CERTIFY.csv", ["\u8b58\u5225\u78bc", "Certify", "Certify_Desc", "Active"], parent)
        self.setWindowTitle("Certificate Management")
