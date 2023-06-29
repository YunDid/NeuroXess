import loguru
import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtGui
import pyqtgraph as pg
from app.ui.eeg_plot import Ui_Form

pg.ViewBox.suggestPadding = lambda *_: 0.0

class EEGPlotController:
    def __init__(self):
        self.win: EEGPlotWin = None
        self.sub_plots = []
        self._engry_data = []
        self._engry_plot = None
        self._max_plot_num = 15
        self.data_length = 40000
        self._start_channel = 0
        self._channel_change = False
        self.i1 = None
        self._win_show = False

    def init(self):
        self.win = EEGPlotWin(self.close_event)
        self.win.xyz_plot.setBackground('w')
        self.win.amp_submit.clicked.connect(self.change_y_amp)
        self.win.channel_submit_2.clicked.connect(self.change_start_channel)

    def change_start_channel(self):
        self._start_channel = self.win.start_channel_spinBox.value()
        self._channel_change = True

    def change_y_amp(self):
        try:
            self.win.amp_submit.setDisabled(True)
            max_ = self.win.amp_x.value()
            min_ = self.win.amp_y.value()
            for subplot in self.sub_plots:
                sub_plot = subplot['sub_plot']
                sub_plot.setYRange(min=min_,  # 最小值
                                   max=max_)  # 最大值
        finally:
            self.win.amp_submit.setDisabled(False)

    def close_event(self):
        loguru.logger.debug("close.....")

    def init_engry_graph(self, channels=32):
        self.win.engry_plot.setBackground('w')
        self._engry_plot = self.win.engry_plot.addPlot(row=0, col=0)
        # self._engry_plot.setXRange(0, 4000, padding=0)
        # self._engry_plot.setYRange(0, 256, padding=0)
        # self._engry_plot.setRange(padding=0)
        self._engry_data = [[0 for j in range(100)] for i in range(channels)]
        self.i1 = pg.ImageItem(image=np.array(self._engry_data).T)
        self._engry_plot.addItem(self.i1)
        colors = [
            (0, 0, 0),
            (45, 5, 61),
            (84, 42, 55),
            (150, 87, 60),
            (208, 171, 141),
            (255, 255, 255)
        ]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=colors, )
        self.bar = self._engry_plot.addColorBar(self.i1, colorMap="CET-D1A")


    def init_graph(self, channel_num):
        if self.sub_plots: return
        plots_num = min(channel_num, self._max_plot_num)

        for i in range(plots_num):
            sub_plot = self.win.xyz_plot.addPlot(row=i//3, col=i%3, title=f"{i}")
            sub_plot.showGrid(x=True, y=True)
            timeline = [i for i in range(self.data_length)]
            sub_plot.setLabel("left", "振幅")
            sub_plot.setLabel("bottom", "频率")
            curve = sub_plot.plot(
                pen=pg.mkPen('b', width=1)
            )
            # plot_curves[tag] = curve, [0 for i in range(self.data_length)]
            plot_curves = {
                "0": [curve, [0 for i in range(self.data_length)]]
            }
            self.sub_plots.append({
                'sub_plot': sub_plot,
                'timeline': timeline,
                'plot_curves': plot_curves
            })
        self.init_engry_graph(channel_num)

    def start(self, channel_num=32):
        loguru.logger.debug(channel_num)
        if self.win is None:
            self.init()

        if not self.sub_plots:
            # loguru.logger.debug(odata[1].shape)
            self.init_graph(channel_num)

        self.win.show()
        self._win_show = True

    def update_data(self, odata:list):
        if not self._win_show: return


        # loguru.logger.debug(odata[1])
        data = odata[0]
        start_num = min(len(data) - self._max_plot_num, self._start_channel)
        loguru.logger.debug(f"start {start_num} l{len(data[0])}")
        if self._channel_change:
            change_title = True
            self._channel_change = False
            self.win.start_channel_spinBox.setValue(start_num)
        else:
            change_title = False

        # loguru.logger.debug(len(data))
        for i,subplot in enumerate(self.sub_plots):
            d_length = len(data[i+start_num])
            # loguru.logger.debug(d_length)
            # if change_title: subplot['plot_curves']["0"][0].setTitle(f"{i+start_num}")
            subplot['plot_curves']["0"][0].setData([i for i in range(d_length)], data[i+start_num])

        if self.i1:
            self.bar.values = (0,10)
            for i,each in enumerate(odata[1]):
                # print(each.shape)
                cur_data = each.tolist()
                self._engry_data[i].extend(cur_data)
                self._engry_data[i] = self._engry_data[i][len(cur_data):]
            self.i1.setImage(np.array(self._engry_data).T)


class EEGPlotWin(QWidget, Ui_Form):
    """
    主窗口，父类1：QtWidgets.QWidget；父类2：Qtdisigner创建的窗口和控件类 Ui_Form
    """

    def __init__(self, close_event=None):
        super().__init__()
        self.setupUi(self)
        # self.setWindowTitle("窗口标题")
        # self.showMaximized()  # 窗口最大化
        # icon = QtGui.QIcon(os.getcwd() + "/resource/image/logo.png")  # 设置窗口图标
        # self.setWindowIcon(icon)
        self.close_event = close_event

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """
        重写QWidget类的closrEvent方法，在窗口被关闭的时候自动触发
        """
        super().closeEvent(a0)  # 先添加父类的方法，以免导致覆盖父类方法（这是重点！！！）
        if self.close_event:
            self.close_event()