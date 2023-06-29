import os
import traceback

import loguru
import matplotlib
import numpy as np
import requests

from app.ui.bad_channel_ui import ChannelWidget
from app.utils.sys_tools import bind_cpu

matplotlib.use("Qt5Agg")  # 声明使用pyqt5
import pyqtgraph as pg

from app.services.dog_walk_decoder_service import DogWalkDecoderService
from app.utils.asyncqt5 import async_qt
from ui.eeg_decoder import Ui_MainWindow
from app.config.decoder_setting import DecoderSetting, NeuroSetting, BehaviorSetting, MotionInputTypeEnum, \
    TargetTypeEnum, DogWalkDecodeSetting


class DecoderService:
    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']

    def __init__(self):
        self.win: Ui_MainWindow = None
        self._engry_data = []
        self._decode = None
        self._decoding = False
        self.log_level = 1
        self._plots = [ "速度", "位置"]
        # self._filter_channel_widget = ChannelWidget()
        # self.init_bad_channel()
        self.data_length = 100
        self.sub_plots = []
        self._filter_channel_widget = None
        bind_cpu(0x0001)

    def init_bad_channel(self):
        self._filter_channel_widget = ChannelWidget()
        bad_chs = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
            16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
            30, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44,
            46, 47, 48, 49, 50, 51, 52, 54, 55, 56, 57, 58, 60, 61,
            62, 64, 65, 66, 68, 73, 74, 76, 81, 82, 83, 84, 86, 87,
            88, 89, 90, 91, 94, 96, 97, 98, 99, 100, 101, 102, 103, 104,
            105, 106, 107, 108, 109, 110, 112, 113, 114, 115, 116, 117, 118, 119,
            120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 132, 133, 134,
            135, 136, 137, 138, 140, 141, 143, 145, 146, 149, 150, 151, 152, 153,
            154, 156, 158, 159, 161, 162, 166, 168, 169, 170, 172, 173, 174, 175,
            176, 177, 178, 179, 180, 181, 185, 186, 187, 193, 194, 195, 196, 198,
            201, 202, 203, 204, 205, 207, 209, 210, 211, 212, 214, 216, 217, 218,
            219, 220, 222, 223, 224, 225, 226, 227, 229, 231, 232, 233, 234, 236,
            237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250,
            251, 252, 253, 254, 255, 256
        ]
        bad_chs = [_ - 1 for _ in bad_chs]
        self._filter_channel_widget.set_bad_channels(bad_chs)

    def get_eeg_impedances(self):
        try:
            host = "127.0.0.1:10800"
            host = os.environ.get("ME_HOST", host)
            loguru.logger.debug(f"http://{host}/api/v1/board/impedances?refresh=false")
            r = requests.get(f"http://{host}/api/v1/board/impedances?refresh=false", timeout=1.0)
            return r.json()['data']
        except Exception as e:
            loguru.logger.exception(e)
            return {}

    def console_log(self, text, level: int=0):
        if level > 4: level = 4
        if level < 0: level = 0
        color = {
            0: '#999999',  # trace
            1: '#666666',    # debug
            2: 'green',         # info
            3: '#FFCC00',      # warn
            4: 'red'        # error
        }
        html = f"- <span style='color: {color[level]}'>{text}</span>"
        if level >= self.log_level:
            self.win.logBrowser.append(html)
            my_cursor = self.win.logBrowser.textCursor()
            self.win.logBrowser.moveCursor(my_cursor.End)

    def set_ui(self, ui):
        self.win = ui
        self.init_bad_channel()

    def init_subplot(self):
        # self.win.plotWidget.addLegend()
        for i, each in enumerate(self._plots):
            sub_plot = self.win.plotWidget.addPlot(row=i, col=0, title=f"{each}")
            sub_plot.addLegend()
            timeline = [i for i in range(self.data_length)]
            sub_plot.setLabel("left", "运动幅度/m")
            sub_plot.setLabel("bottom", "时间")
            if i == 0:
                sub_plot.setYRange(min=-2,  # 最小值
                                   max=2)  # 最大值
            else:
                sub_plot.setYRange(min=-0.2,  # 最小值
                                   max=0.2)  # 最大值
            plot_curves = {}
            self.sub_plots.append({
                'sub_plot': sub_plot,
                'timeline': timeline,
                'plot_curves': plot_curves
            })

    def clear_plot(self):
        for subplot in self.sub_plots:
            subplot['timeline'] = [i for i in range(self.data_length)]
            plot_curves = subplot['plot_curves']
            for tag,v in plot_curves.items():
                curve, data = v
                for i in range(len(data)):
                    data[i] = 0
                curve.setData(subplot['timeline'], data)

    def init_graph(self):
        if not self.sub_plots:
            self.init_subplot()

            selected_devices = ['pred', 'real']

            for j, subplot in enumerate(self.sub_plots):
                sub_plot = subplot['sub_plot']
                plot_curves = subplot['plot_curves']
                for i, tag in enumerate(selected_devices):
                    curve = sub_plot.plot(
                        pen=pg.mkPen(self.colors[i], width=2), name=tag
                    )

                    plot_curves[tag] = curve, [0 for i in range(self.data_length)]
        else:
            self.clear_plot()



    def __update_data(self, data_array, num, timeline, curve):
        data_array.append(num)
        data_array.pop(0)
        curve.setData(timeline, data_array)

    def update_data(self, data:dict):
        # loguru.logger.debug(data)
        # self.console_log(f"{data}", level=2)
        timeline = self.sub_plots[0]['timeline']

        curve_speed_pred, data_speed_pred = self.sub_plots[0]['plot_curves']['pred']
        self.__update_data(data_speed_pred, data['pred'][0][0], timeline, curve_speed_pred)

        curve_pos_pred, data_pos_pred = self.sub_plots[1]['plot_curves']['pred']
        self.__update_data(data_pos_pred, data['pred'][0][1], timeline, curve_pos_pred)

        curve_speed_real, data_speed_real = self.sub_plots[0]['plot_curves']['real']
        self.__update_data(data_speed_real, data['motion'][0], timeline, curve_speed_real)

        curve_pos_real, data_pos_real = self.sub_plots[1]['plot_curves']['real']
        self.__update_data(data_pos_real, data['motion'][1], timeline, curve_pos_real)

        v_c = np.corrcoef(data_speed_pred, data_speed_real)
        p_c = np.corrcoef(data_pos_pred, data_pos_real)
        msg = f"cc=v={v_c[0][1]} p={p_c[0][1]} real={data['motion']}"
        self.console_log(msg, level=2)

    def start(self):
        if self._decoding is False:
            try:
                self.console_log(f"开始解码", 2)
                self.win.starDecode.setDisabled(True)
                self.decode()
                self.win.starDecode.setText("停止解码")
                self.win.starDecode.setDisabled(False)
                self._decoding = True
            except Exception as e:
                self.console_log(f"启动解码失败：{e}", 4)
                loguru.logger.exception(e)
                self._decoding = False
                self.win.starDecode.setDisabled(False)
                self.win.starDecode.setText("解码")
        else:
            self.console_log(f"停止解码", 2)
            self._decode.stop_decode()
            self._decoding = False
            self.win.starDecode.setText("解码")

    def msg_pull(self, *args):
        self.console_log(f"{args}", level=3)

    def decode(self):
        # neural_fs = 4000
        # bad_chs = [
        #     1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
        #     16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
        #     30, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44,
        #     46, 47, 48, 49, 50, 51, 52, 54, 55, 56, 57, 58, 60, 61,
        #     62, 64, 65, 66, 68, 73, 74, 76, 81, 82, 83, 84, 86, 87,
        #     88, 89, 90, 91, 94, 96, 97, 98, 99, 100, 101, 102, 103, 104,
        #     105, 106, 107, 108, 109, 110, 112, 113, 114, 115, 116, 117, 118, 119,
        #     120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 132, 133, 134,
        #     135, 136, 137, 138, 140, 141, 143, 145, 146, 149, 150, 151, 152, 153,
        #     154, 156, 158, 159, 161, 162, 166, 168, 169, 170, 172, 173, 174, 175,
        #     176, 177, 178, 179, 180, 181, 185, 186, 187, 193, 194, 195, 196, 198,
        #     201, 202, 203, 204, 205, 207, 209, 210, 211, 212, 214, 216, 217, 218,
        #     219, 220, 222, 223, 224, 225, 226, 227, 229, 231, 232, 233, 234, 236,
        #     237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250,
        #     251, 252, 253, 254, 255, 256
        # ]
        # bad_chs = [_ - 1 for _ in bad_chs]
        bad_chs = self._filter_channel_widget.get_bad_channels()
        neural_fbands = self.win.neuralFbands.toPlainText()
        neural_fbands = [F.strip().split('-') for F in neural_fbands.split('\n') if F.strip() ]
        loguru.logger.debug(neural_fbands)
        neuro_setting = NeuroSetting(
                                     neuro_bad_channels=bad_chs,
                                     neural_fbands=neural_fbands,
                                     )
        behavior_input_filter = self.win.behaviorInpFilter.currentText()
        behavior_target_type = self.win.behavioTargetType.currentText().split('-')
        behavior = BehaviorSetting(
                                   behavior_target_type=behavior_target_type,
                                   behavior_input_filter=behavior_input_filter if behavior_input_filter != 'none' else None
                                   )
        config = DecoderSetting(neuro=neuro_setting,
                                bin_size=self.win.binSizeDoubleSpinBox.value(),
                                behavior=behavior,
                                nbins_train=self.win.nbinsTrainSpinBox_2.value(),
                                ncomponents=self.win.ncomponentsSpinBox.value()
                                )
        dog_setting = DogWalkDecodeSetting(motion_field=self.win.behaviorField.currentText())
        self._decode = DogWalkDecoderService(config, dog_setting=dog_setting)
        self._decode.message_push_trigger.connect(self.update_data)
        self._decode.err_push_trigger.connect(self.msg_pull)
        async_qt.async_run(self._decode.decode(), errcall=self.connect_err_callback)
        self.init_graph()

    def connect_err_callback(self, e):
        loguru.logger.debug(traceback.format_exc())
        self.console_log(e, 4)

    def filter_channel(self):
        loguru.logger.info("filter channel")
        self._filter_channel_widget.show()



decoder_service = DecoderService()


class DecoderController:
    def __init__(self, ui:Ui_MainWindow, loop=None):
        self.ui:Ui_MainWindow = ui
        self.loop = loop
        self.init()

    def init(self):
        self.ui.plotWidget.setBackground('w')
        decoder_service.set_ui(self.ui)
        self.ui.starDecode.clicked.connect(decoder_service.start)
        self.ui.filterChannel.clicked.connect(decoder_service.filter_channel)

