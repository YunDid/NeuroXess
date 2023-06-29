import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from app.controller.decoder_controller import DecoderController
from app.utils.qt_main_window import RQMainWindow
from app.ui.eeg_decoder import Ui_MainWindow

def start():
    import logging
    LOGFORMAT = ' %(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'

    sys._excepthook = sys.excepthook
    logging.basicConfig(level=logging.DEBUG, format=LOGFORMAT, datefmt='%H:%M:%S')

    def my_exception_hook(exctype, value, traceback):
        # Print the error and traceback
        print(exctype, value, traceback)
        # Call the normal Exception hook after
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)


    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QApplication(sys.argv)
    # loop = QEventLoop(app)
    loop = None
    # asyncio.set_event_loop(loop)

    MainWindow = RQMainWindow()

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    controller = DecoderController(ui, loop)

    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    start()