# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'me_eeg_origin_graph.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 480)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.start = QtWidgets.QPushButton(self.centralwidget)
        self.start.setGeometry(QtCore.QRect(20, 40, 121, 41))
        self.start.setObjectName("start")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 100, 571, 121))
        self.groupBox.setObjectName("groupBox")
        self.log = QtWidgets.QTextBrowser(self.groupBox)
        self.log.setGeometry(QtCore.QRect(10, 20, 551, 91))
        self.log.setObjectName("log")
        self.open_stat = QtWidgets.QPushButton(self.centralwidget)
        self.open_stat.setGeometry(QtCore.QRect(180, 40, 121, 41))
        self.open_stat.setObjectName("open_stat")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.start.setText(_translate("MainWindow", "collect"))
        self.groupBox.setTitle(_translate("MainWindow", "log"))
        self.open_stat.setText(_translate("MainWindow", "打开监控"))