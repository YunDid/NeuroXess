import sys

from PyQt5.QtWidgets import QMainWindow, QMessageBox


class RQMainWindow(QMainWindow):
    def __init__(self, parent=None, close_call=None):
        self.close_call = close_call
        super(RQMainWindow, self).__init__(parent)

    # def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
    #     loguru.logger.debug(f"{a0.key()} {a0.nativeScanCode()} {a0.spontaneous()}")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示',
                                     "是否要关闭所有窗口?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            if self.close_call:
                self.close_call()
            sys.exit(0)  # 退出程序
        else:
            event.ignore()
