import loguru

from app.controller.eeg_plot_controller import EEGPlotController
from app.plugins.eeg_origin_graph_plugin import EEGRAwDataPlugin
from app.ui.me_eeg_origin_graph import Ui_MainWindow
from app.utils.asyncqt5 import async_qt


class EEGRawGraphService:
    def __init__(self):
        self.ui:Ui_MainWindow = None
        self.log_level = 2
        self.eeg_plot_controller:EEGPlotController = None
        self._eeg_pluin = EEGRAwDataPlugin(callback=self.eeg_call)
        self._channel_num = None

    def set_ui(self, ui: Ui_MainWindow):
        self.ui = ui
        try:
            self.eeg_plot_controller = EEGPlotController()
        except Exception as e:
            loguru.logger.exception(e)
            raise e

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
        html = f"<span style='color: {color[level]}'>{text}</span>"
        if level >= self.log_level:
            self.ui.log.append(html)
            my_cursor = self.ui.log.textCursor()
            self.ui.log.moveCursor(my_cursor.End)

    def eeg_call(self, data):
        # print(data)
        # loguru.logger.debug(len(data))
        # data = data.tolist()
        loguru.logger.debug("call....")
        self._channel_num = data[1].shape[0]
        try:
            self.eeg_plot_controller.update_data(data)
        except Exception as e:
            loguru.logger.exception(e)

    def err_call(self, *args):
        print(args)
        self.ui.start.setDisabled(False)

    def start_submit(self, *args, **kwargs):
        self.ui.start.setDisabled(True)
        self.console_log("开始采集", level=2)
        try:
            # async_qt.async_run(self._eeg_pluin.init())
            async_qt.async_run(self._eeg_pluin.subscibe_loop(), errcall=self.err_call, callback=self.err_call)
            # self.eeg_plot_controller.start()
        except Exception as e:
            loguru.logger.exception(e)
        # self.eeg_plot_controller.start()

    def open_graph_win(self):
        self.eeg_plot_controller.start(self._channel_num)



eeg_service = EEGRawGraphService()