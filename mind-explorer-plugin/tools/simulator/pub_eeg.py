import asyncio
import copy
import json
import math
import os.path
import time
# import aiofiles
import loguru
import win_precise_time
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication
import bson
import sys
import win_precise_time as wpt

from app.config.setting import setting
from imu_parse_service import ImuHeader, imu_parser_service
from sdk.py_librecord.record_read import RecordRead
from zmq_service import zmq_client
from me_worker.service.msg_service.topic import SUB_ZMQ_CC_HS_DATA

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# from app.config.settings import setting
# from app.service.nats_service.topic import *

class Pubdata(QtWidgets.QMainWindow):
    topic = SUB_ZMQ_CC_HS_DATA

    def __init__(self):
        super().__init__()
        # self.resize(200, 100)
        # self.setWindowTitle('pyqtgraph')
        # inp =  r"e:\data\local\2\origin\test_17-32-35_raw.bin"
        inp = r"D:\develop\py\mind-explorer-plugin\extern\mind-explorer-decode\test\data\Neural\subjects_1.exps_44.origin.20230606153559_365607.G2_Dog01_Day27_Treadmill-2.mex"
        self.record = RecordRead(inp)
        self.record.run()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.run_loop)
        self.timer.start(10)
        zmq_client.init("tcp://*:16480")

    def run_loop(self):
        # loguru.logger.debug("sddddd")
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.send_data())
        data_size = int(self.record.cerecube_info.sample_rate // 100)
        datalist = [self.topic.encode()]
        frame = self.record.get_frame()
        for each in range(data_size):
            data = next(frame)
            datalist.append(data + b'00')

        meta = {
            'datetime': wpt.time() * 1000,
            'rate': self.record.cerecube_info.sample_rate,
            'channels': self.record.cerecube_info.count_of_channels
        }
        datalist.append(json.dumps(meta).encode())
        zmq_client.pub_raw(datalist)





def main():
    app = QApplication(sys.argv)
    app.setApplicationName("eeg pub")
    print("start...")
    pub = Pubdata()
    # pub.run()
    pub.show()

    status = app.exec_()
    print(status)
    # time.sleep(1000000)


if __name__ == '__main__':
    # asyncio.run(main())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    main()