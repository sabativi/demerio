from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from params import *

class CloudWidget(QWidget):

    pushed = pyqtSignal()

    def __init__(self, name, parent=None):
        super(CloudWidget, self).__init__(parent)
        self.ui = uic.loadUi(ui_full_path('cloud_view.ui'), self)
        self.ui.cloudName.setText(name)
        pixmap = QPixmap(":/images/" + name + ".png")
        self.ui.cloudImage.setPixmap(pixmap)
        self.ui.cloudImage.setMask(pixmap.mask())
        self.ui.cloudAction.clicked.connect(self.pushed)
        self.name = name