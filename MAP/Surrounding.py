# -*- coding: utf-8 -*-
# @Time    : 2025/1/1 10:50
# @Author  : Li Xinran
# @Software: PyCharm 
# @Comment :
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton

class SurroundingInfoWindow(QDialog):
    def __init__(self, start_info, end_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle('周边信息')
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(start_info + end_info)

        close_button = QPushButton('关闭', self)
        close_button.clicked.connect(self.accept)

        layout.addWidget(self.text_edit)
        layout.addWidget(close_button)

        self.setLayout(layout)


