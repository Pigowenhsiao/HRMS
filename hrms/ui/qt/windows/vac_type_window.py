from .basic_csv_window import BasicCSVWindow


class VacTypeWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        super().__init__("VAC_Type.csv", ["VAC_ID", "Active"], parent)
        self.setWindowTitle("Vacation Type Management")
