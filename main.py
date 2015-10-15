import sys
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon
from demerio_gui.main_window import MainWindow
from demerio_gui.version import get_versions
from demerio_gui.params import *

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(0, QCoreApplication.translate(trad_context, "Demerio"),
                             QCoreApplication.translate(trad_context, "I couldn't detect any system tray on this system."))
        sys.exit(1)
    QApplication.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/images/demerio.png"))
    app.setApplicationVersion(get_versions()["version"])
    main_window = MainWindow()
    main_window.show()
    main_window.setWindowTitle("Demerio")
    sys.exit(app.exec_())

