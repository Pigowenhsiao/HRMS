from .basic_csv_window import BasicCSVWindow


class AreaWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        super().__init__("Area.csv", ["Area", "Area_Desc", "Active"], parent)
        self.setWindowTitle("Area Management")
