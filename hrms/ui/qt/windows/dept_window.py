from .basic_csv_window import BasicCSVWindow


class DeptWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        super().__init__("L_Section.csv", ["Dept_Code", "Dept_Name", "Dept_Desc"], parent)
        self.setWindowTitle("Department Management")
