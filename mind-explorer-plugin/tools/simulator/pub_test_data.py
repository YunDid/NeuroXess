import json
import os
import sys
import time

import bson
import h5py
import loguru
import numpy as np
import win_precise_time
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication
from zmq_service import ZmqClient
from me_worker.service.msg_service.topic import SUB_ZMQ_CC_HS_DATA, SUB_IMU

def _reading_mat_v7_3(data_path):
    data_dict = {}
    with h5py.File(data_path) as f:
        for k, v in f.items():
            data_dict[k] = np.asarray(v) if v.size > 1 else np.squeeze(v)
    return data_dict


class Pubdata(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.imu = ZmqClient()
        self.imu.init("tcp://*:16490")
        self.eeg_client = ZmqClient()
        self.eeg_client.init("tcp://*:16480" )
        #"tcp://*:16480"
        self.i = 0
        self.init_data()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.run_eeg)
        self.timer.start(10)

        self.imu_ts = None
        self.sys_ts = None
        self.timer_imu = QtCore.QTimer()
        self.timer_imu.timeout.connect(self.run_imu)
        self.timer_imu.start(10)

    def init_data(self):
        data_path = r"D:\develop\py\mind-explorer-plugin\extern\mind-explorer-decode"
        # subject = "RH_Male_38_rHand"
        neural_file = "test/data/Neural/AlignedTestNeural.mat"
        motion_file = "test/data/Motion/AlignedTestMotion.mat"

        neural_path = os.path.join(data_path, neural_file)
        motion_path = os.path.join(data_path, motion_file)

        self.neural_dict = _reading_mat_v7_3(neural_path)
        self.neural_data: np.ndarray = self.neural_dict["neural"].T  # (C, T) -> (T, C)
        self.neural_fs = self.neural_dict["neural_fs"]

        self.motion_dict = _reading_mat_v7_3(motion_path)
        self.motion_data: np.ndarray = self.motion_dict["motion"].T  # (D, T) -> (T, D)
        self.motion_fs = self.motion_dict["motion_fs"]
        self.motion_ts: np.ndarray = np.squeeze(self.motion_dict["motion_ts"])
        self._motion_index = 0
        self._neuro_index = 0

    def run_eeg(self):
        loguru.logger.debug("run eeg")
        # motion_bin = motion_data[int(i * 4):int((i + 1) * 4), :]
        # neuro_bin = neural_data[int(i * bin_size):int((i + 1) * bin_size), :]
        bin_size = 40
        # for i in range(bin_size):
        neuro_bin = self.neural_data[int(self._neuro_index * bin_size):int((self._neuro_index + 1) * bin_size), :]
        din2 = np.zeros((40, 1))
        neuro_bin = np.hstack((neuro_bin, din2))
        neuro_bin = neuro_bin.astype(dtype=np.int16)
        meta = {
            'datetime': win_precise_time.time() * 1000,
            'rate': 4000,
            'channels': 256
        }
        self.eeg_client.pub_raw([SUB_ZMQ_CC_HS_DATA.encode(), neuro_bin.tobytes(), json.dumps(meta).encode()])
        self._neuro_index += 1
        if self._neuro_index * 40 >= self.neural_data.shape[0]:
            self._motion_index = 0
            self._neuro_index = 0

    def run_imu(self):
        try:
            # self.i += 1
            # if self.i % 2 == 0: return
            # if self.i % 9 == 0: return
            # loguru.logger.debug("run imu")

            t = self.motion_ts[self._motion_index]
            current_ms = int(t * 10)
            ws = win_precise_time.time_ns()

            # print(self.imu_ts, current_ms)
            # print(self.sys_ts, int(ws * 10e-9))
            if self.imu_ts and self.sys_ts and self.imu_ts != current_ms and self.sys_ts == int(ws * 10e-9):
                # self.sys_ts = ws
                return

            self.imu_ts = current_ms
            self.sys_ts = int(ws * 10e-9)


            data = self.motion_data[self._motion_index]

            d = {"tag": "ddd", "record": {'acceleration': {'x': data[0]}, 'sys_time': ws},
                 'fs': 40}
            # print(d)
            self.imu.pub_data("D.CC.IMU.RT", d)
            self._motion_index += 1

            # t = t * 10
            current_ms = int(t * 10)
            # for i in range(1, 5):
            #     # time.sleep(0.02)
            #     t = self.motion_ts[self._motion_index]
            #     ms = int(t * 10)
            #     if current_ms != ms:
            #         break
            #     data = self.motion_data[self._motion_index]
            #     d = {"tag": "ddd", "record": {'acceleration': {'x': data[0]}, 'sys_time': win_precise_time.time_ns()}, 'fs': 40}
            #     # print(d)
            #     self.imu.pub_data("D.CC.IMU.RT", d)
            #     self._motion_index += 1


            if self._motion_index == self.motion_data.shape[0]:
                self._motion_index = 0
                self._neuro_index = 0
        except Exception as e:
            loguru.logger.exception(e)
            raise e

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






