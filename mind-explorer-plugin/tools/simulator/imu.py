import asyncio
import copy
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

from imu_parse_service import ImuHeader, imu_parser_service
from zmq_service import zmq_client

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# from app.config.settings import setting
# from app.service.nats_service.topic import *

class Pubdata(QtWidgets.QMainWindow):
    topic = "D.CC.RAW.RT"

    def __init__(self):
        super().__init__()
        # self.resize(200, 100)
        # self.setWindowTitle('pyqtgraph')
        # inp =  r"e:\data\local\2\origin\test_17-32-35_raw.bin"
        inp = r"D:\develop\py\Flappy-bird-python\test\data\0606.imu"
        self._fd = open(inp, 'rb')
        h_data = self._fd.read(16)
        self._header = ImuHeader.parse_bytes(h_data)
        self.nch = 1
        self.sample_rate =  self._header.sample_rate
        self.read_times = 10  # 10ms
        self._read_time_num = 0
        self.sample_rate_per_ms = int(self.sample_rate / 1000)
        self.size_ = int(self.nch * 2 * self.sample_rate_per_ms * self.read_times)
        self.nc = None
        zmq_client.init("tcp://*:16490")
        # self.timer = None
        self.timer = QtCore.QTimer()

        self.timer.timeout.connect(self.run_loop)
        self.timer.start(10)
        self.i = 0



    def read_data(self):
        # d = self._fd.read(1)
        new_buffer = self._fd.read(73+8)


        if len(new_buffer) < self.size_ + 2 * self.sample_rate_per_ms * self.read_times:
            print("new")
            self._fd.seek(14)
            self._read_time_num = 0
            return self.read_data()

        return imu_parser_service.parse_imu(bytearray(new_buffer))

    def run(self):
        # ...
        print("runi")
        self.i+=1
        if self.i % 2 == 0: return
        if self.i % 9 == 0: return
        self.timer = QtCore.QTimer(self)

        self.timer.timeout.connect(self.run_loop)
        self.timer.start(25)


    def run_loop(self):
        # loguru.logger.debug("imu")
        # loguru.logger.debug("sddddd")
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.send_data())
        self.i += 1
        if self.i % 2 == 0: return
        if self.i % 9 == 0: return
        record = self.read_data()
        record.sys_time = win_precise_time.time_ns()
        # print(int(record.sys_time // 10e5))
        zmq_client.pub_data("D.CC.IMU.RT", {"tag": "test", "record": record.dict(), 'fs': self.sample_rate})


    async def send_data(self):
        loguru.logger.debug("start...")
        # print(len(new_buffer))
        if self.nc is None:
            await self.init()

        # print(len(new_buffer), len(x))
        new_buffer = self.read_data()
        data = {
            "channels": self.nch,
            "time": self._read_time_num,
            "buffer": new_buffer,
            "precision": 2,
            "sample_rate": self.sample_rate
        }
        resp = await self.nc.publish(self.topic, bson.dumps(data))


def main():
    app = QApplication(sys.argv)
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