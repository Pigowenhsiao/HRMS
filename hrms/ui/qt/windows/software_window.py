from .basic_csv_window import BasicCSVWindow


class SoftwareWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        super().__init__("SOFTWARE.csv", ["S_Ver", "Meno", "Update_Date", "Active"], parent)
        self.setWindowTitle("Software Management")
