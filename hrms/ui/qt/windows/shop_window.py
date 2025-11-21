from .basic_csv_window import BasicCSVWindow


class ShopWindow(BasicCSVWindow):
    def __init__(self, parent=None):
        super().__init__("SHOP.csv", ["\u8b58\u5225\u78bc", "SHOP", "SHOP_DESC", "Active"], parent)
        self.setWindowTitle("Shop Management")
