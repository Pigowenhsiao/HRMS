from .basic_csv_window import BasicCSVWindow


class JobWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        super().__init__("L_Job.csv", ["L_Job"], parent)
        self.setWindowTitle("Job Management")
