from .basic_csv_window import BasicCSVWindow, LookupSpec


class TrainingRecordWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        columns = [
            "Certify_No",
            "EMP_ID",
            "Certify_ID",
            "Certify_date",
            "Certify_type",
            "update_date",
            "Active",
            "Remark",
            "updater",
            "Cer_type",
        ]
        lookups = {
            "EMP_ID": LookupSpec("BASIC.csv", "EMP_ID", ("C_Name",)),
            "Certify_ID": LookupSpec("CERTIFY_ITEMS.csv", "Certify_ID", ("Certify_Name",)),
            "Certify_type": LookupSpec("CERTIFY_TYPE.csv", "Certify_Type"),
            "Cer_type": LookupSpec("CERTIFY_TYPE.csv", "Certify_Type"),
        }
        super().__init__("TRAINING_RECORD.csv", columns, parent, lookups=lookups)
        self.setWindowTitle("Training Record Management")
