# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eeg_decoder.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1287, 595)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(20, 350, 351, 191))
        self.groupBox.setObjectName("groupBox")
        self.logBrowser = QtWidgets.QTextBrowser(self.groupBox)
        self.logBrowser.setGeometry(QtCore.QRect(10, 20, 331, 161))
        self.logBrowser.setObjectName("logBrowser")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 20, 351, 321))
        self.groupBox_2.setObjectName("groupBox_2")
        self.starDecode = QtWidgets.QPushButton(self.groupBox_2)
        self.starDecode.setGeometry(QtCore.QRect(10, 288, 75, 23))
        self.starDecode.setObjectName("starDecode")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(10, 22, 48, 16))
        self.label.setObjectName("label")
        self.binSizeDoubleSpinBox = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.binSizeDoubleSpinBox.setGeometry(QtCore.QRect(64, 22, 58, 20))
        self.binSizeDoubleSpinBox.setMaximum(60.0)
        self.binSizeDoubleSpinBox.setSingleStep(0.05)
        self.binSizeDoubleSpinBox.setProperty("value", 0.1)
        self.binSizeDoubleSpinBox.setObjectName("binSizeDoubleSpinBox")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(10, 96, 48, 16))
        self.label_3.setObjectName("label_3")
        self.behavioTargetType = QtWidgets.QComboBox(self.groupBox_2)
        self.behavioTargetType.setGeometry(QtCore.QRect(64, 96, 68, 20))
        self.behavioTargetType.setObjectName("behavioTargetType")
        self.behavioTargetType.addItem("")
        self.behavioTargetType.addItem("")
        self.behavioTargetType.addItem("")
        self.behavioTargetType.addItem("")
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setGeometry(QtCore.QRect(10, 122, 60, 16))
        self.label_4.setObjectName("label_4")
        self.ncomponentsSpinBox = QtWidgets.QSpinBox(self.groupBox_2)
        self.ncomponentsSpinBox.setGeometry(QtCore.QRect(113, 122, 46, 20))
        self.ncomponentsSpinBox.setMaximum(256)
        self.ncomponentsSpinBox.setProperty("value", 50)
        self.ncomponentsSpinBox.setObjectName("ncomponentsSpinBox")
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setGeometry(QtCore.QRect(10, 148, 72, 16))
        self.label_5.setObjectName("label_5")
        self.nbinsTrainSpinBox_2 = QtWidgets.QSpinBox(self.groupBox_2)
        self.nbinsTrainSpinBox_2.setGeometry(QtCore.QRect(113, 148, 64, 20))
        self.nbinsTrainSpinBox_2.setMaximum(100000)
        self.nbinsTrainSpinBox_2.setProperty("value", 1000)
        self.nbinsTrainSpinBox_2.setObjectName("nbinsTrainSpinBox_2")
        self.label_6 = QtWidgets.QLabel(self.groupBox_2)
        self.label_6.setGeometry(QtCore.QRect(10, 174, 48, 16))
        self.label_6.setObjectName("label_6")
        self.neuralFbands = QtWidgets.QTextEdit(self.groupBox_2)
        self.neuralFbands.setGeometry(QtCore.QRect(89, 174, 112, 51))
        self.neuralFbands.setObjectName("neuralFbands")
        self.label_7 = QtWidgets.QLabel(self.groupBox_2)
        self.label_7.setGeometry(QtCore.QRect(10, 50, 81, 16))
        self.label_7.setObjectName("label_7")
        self.behaviorInpFilter = QtWidgets.QComboBox(self.groupBox_2)
        self.behaviorInpFilter.setGeometry(QtCore.QRect(90, 50, 71, 20))
        self.behaviorInpFilter.setObjectName("behaviorInpFilter")
        self.behaviorInpFilter.addItem("")
        self.behaviorInpFilter.addItem("")
        self.behaviorInpFilter.addItem("")
        self.behaviorInpFilter.addItem("")
        self.label_8 = QtWidgets.QLabel(self.groupBox_2)
        self.label_8.setGeometry(QtCore.QRect(20, 240, 54, 12))
        self.label_8.setObjectName("label_8")
        self.behaviorField = QtWidgets.QComboBox(self.groupBox_2)
        self.behaviorField.setGeometry(QtCore.QRect(90, 240, 68, 20))
        self.behaviorField.setObjectName("behaviorField")
        self.behaviorField.addItem("")
        self.behaviorField.addItem("")
        self.behaviorField.addItem("")
        self.filterChannel = QtWidgets.QPushButton(self.groupBox_2)
        self.filterChannel.setGeometry(QtCore.QRect(100, 290, 75, 23))
        self.filterChannel.setObjectName("filterChannel")
        self.plotWidget = GraphicsLayoutWidget(self.centralwidget)
        self.plotWidget.setGeometry(QtCore.QRect(380, 30, 881, 511))
        self.plotWidget.setObjectName("plotWidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1287, 23))
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
        self.groupBox.setTitle(_translate("MainWindow", "工作日志"))
        self.groupBox_2.setTitle(_translate("MainWindow", "控制面板"))
        self.starDecode.setText(_translate("MainWindow", "开始解码"))
        self.label.setText(_translate("MainWindow", "解码窗宽"))
        self.label_3.setText(_translate("MainWindow", "目标类型"))
        self.behavioTargetType.setItemText(0, _translate("MainWindow", "pos-vel"))
        self.behavioTargetType.setItemText(1, _translate("MainWindow", "pos"))
        self.behavioTargetType.setItemText(2, _translate("MainWindow", "vel"))
        self.behavioTargetType.setItemText(3, _translate("MainWindow", "acc"))
        self.label_4.setText(_translate("MainWindow", "解码特征数"))
        self.label_5.setText(_translate("MainWindow", "训练数据时长"))
        self.label_6.setText(_translate("MainWindow", "解码频段"))
        self.neuralFbands.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">70-200</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.label_7.setText(_translate("MainWindow", "运动数据滤波"))
        self.behaviorInpFilter.setItemText(0, _translate("MainWindow", "bandpass"))
        self.behaviorInpFilter.setItemText(1, _translate("MainWindow", "low"))
        self.behaviorInpFilter.setItemText(2, _translate("MainWindow", "high"))
        self.behaviorInpFilter.setItemText(3, _translate("MainWindow", "none"))
        self.label_8.setText(_translate("MainWindow", "运动方向"))
        self.behaviorField.setItemText(0, _translate("MainWindow", "x"))
        self.behaviorField.setItemText(1, _translate("MainWindow", "y"))
        self.behaviorField.setItemText(2, _translate("MainWindow", "z"))
        self.filterChannel.setText(_translate("MainWindow", "过滤通道"))
from pyqtgraph import GraphicsLayoutWidget