from PyQt5.QtWidgets import QTextEdit

class DetailsView(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("路线详情将在此显示")

    def update_details(self, details):
        self.setText(details)