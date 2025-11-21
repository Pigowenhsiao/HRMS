from .basic_csv_window import BasicCSVWindow


class MustToolWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        super().__init__("MUST_TOOL.csv", ["Tool_ID", "Active"], parent)
        self.setWindowTitle("Must Tool Management")
