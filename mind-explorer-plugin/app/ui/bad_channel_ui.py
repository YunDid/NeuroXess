import json
import os
from typing import List

import loguru
import requests
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QCheckBox, QApplication, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
import sys


from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
# from Pyqt5.widgets.components.ui_types import ButtonType, ButtonSize, BorderStyle
# from widgets.components.styles.button_style import ButtonStyle

class BaseCheckBox(QCheckBox):
    """
    基础的StyleSheet
    """
    def __init__(self, *args):
        super(BaseCheckBox, self).__init__(*args)
        self.__init_style() # 设置样式


    def __init_style(self):
        checkbox_style = '''
        QCheckBox {
        border: none;
        border-radius: 1px;
     
        }
        QCheckBox::indicator{
    background-color: rgb(42, 45, 66);
    border: 0.5px solid #b1b1b1;
   width: 35px;
   height: 35px;
   border-radius: 1px;
   }

QCheckBox:enabled:checked{
   color: rgb(255, 255, 255);
}
QCheckBox:enabled:!checked{
   color: rgb(255, 255, 255);
}

QCheckBox::indicator:checked {
        background-color: rgb(255, 97, 0);
}


QCheckBox::indicator:unchecked {
background-color: rgb(61, 145, 64);
}
        '''
        self.setStyleSheet(self.styleSheet() + checkbox_style)


    def mousePressEvent(self, *args, **kwargs):
        return super(BaseCheckBox, self).mousePressEvent(*args, **kwargs)

    def mouseReleaseEvent(self, *args, **kwargs):
        return super(BaseCheckBox, self).mouseReleaseEvent(*args, **kwargs)

    def paintEvent(self, pa : QPaintEvent):
        super(BaseCheckBox, self).paintEvent(pa)
        if self.isChecked():
            painter = QPainter(self)
            painter.setPen(Qt.white)
            painter.setBrush(Qt.white)
            painter.drawText(self.rect(), Qt.AlignCenter, self.text())
            # painter.drawEllipse(24, 4, 18, 18)
        else:
            painter = QPainter(self)
            painter.setPen(Qt.white)
            painter.setBrush(Qt.white)
            painter.drawText(self.rect(), Qt.AlignCenter, self.text())
            # painter.drawEllipse(5, 4, 18, 18)


class ChannelWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("过滤通道")
        self._channels:List[QCheckBox] = []
        self.initUI()


    def initUI(self):
        t = []
        self.resize(40 * 17, 40 * 17)
        self.btn = QPushButton("文件过滤", self)
        self.btn.setGeometry(QtCore.QRect(10, 10, 80, 20))
        self.btn.clicked.connect(self.load_from_file)

        self.btn_am = QPushButton("阻抗过滤", self)
        self.btn_am.setGeometry(QtCore.QRect(100, 10, 80, 20))
        self.btn_am.clicked.connect(self.filter_impdance)

        for i in range(0,16):
            for j in range(0,16):
                a = BaseCheckBox(f"{i*16 + j}", self)
                a.setGeometry(QtCore.QRect(40*j+20, 40*i+30, 40, 40))
                # a.setLayout()
                # a.isChecked()
                t.append(a)
        self._channels = t
        # self.show()

    def filter_impdance(self):
        channels = self.get_eeg_impedances()
        bad = []
        for i,each_ch in enumerate(channels):
            if each_ch['magnitude'] < 1000 or each_ch['magnitude'] > 1000000:
                bad.append(i)
        if bad:
            loguru.logger.info(f"bad={bad}")
            self.set_bad_channels(bad)

    def get_eeg_impedances(self):
        try:
            host = "127.0.0.1:10800"
            host = os.environ.get("ME_HOST", host)
            loguru.logger.debug(f"http://{host}/api/v1/board/impedances?refresh=false")
            r = requests.get(f"http://{host}/api/v1/board/impedances?refresh=false", timeout=1.0)
            return r.json()['data']['impedances']
        except Exception as e:
            loguru.logger.exception(e)
            return []

    def load_from_file(self):
        with open("c:/bad_channel.json", 'r') as f:
            bad_channels = json.load(f)
        loguru.logger.info(f"bad={bad_channels}")
        self.set_bad_channels(bad_channels)

    def set_bad_channels(self, channels):
        for each in channels:
            self._channels[each].setChecked(True)

    def get_bad_channels(self):
        loguru.logger.debug("get bad channel")
        ls = []

        for i, each in enumerate(self._channels):
            # print(i, each)
            if each.isChecked():
                ls.append(i)
        # print(ls)
        return ls





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChannelWidget()
    sys.exit(app.exec_())