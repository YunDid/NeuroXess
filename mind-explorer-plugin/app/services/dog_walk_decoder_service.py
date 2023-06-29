import asyncio
import json
import os
import time
import traceback
from asyncio import QueueEmpty

import bson
import loguru
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget

from app.config.decoder_setting import DecoderSetting, DogWalkDecodeSetting, NeuroSetting, BehaviorSetting, \
    MotionInputTypeEnum, TargetTypeEnum
from app.services.decoder_service import DecoderService
from app.services.imu_sub_service import IMURecordSubService
from app.services.eeg_sub_service import EEGSubService
from app.services.tcp_client import DogWorkerClient
from app.utils.run_in_loop import run_in_loop
from app.utils.sys_tools import bind_cpu


class DogWalkDecoderService(QObject):
    message_push_trigger = pyqtSignal(dict)
    err_push_trigger = pyqtSignal(list)

    def __init__(self, setting:DecoderSetting=None, dog_setting:DogWalkDecodeSetting=None):
        super().__init__(None)
        self._imu_sub = IMURecordSubService()
        self._eeg_sub = EEGSubService()
        self._imu_fs = None
        self._eeg_fs = None
        self._eeg_channels = None
        self._start_eeg_ms = None  # eeg第一帧时间
        self._decoder:DecoderService = None
        self._train_eeg_x = []
        self._train_imu_y = []
        self._train_imu_time = []
        self._bin_eeg_x = None
        self._bin_imu_y = []
        self._config:DecoderSetting = setting
        self._dog_setting = DogWalkDecodeSetting() if dog_setting is None else dog_setting
        self._eeg_length = None
        self._imu_old = None
        self._next_imu_data = []
        self.stop = False
        self._dog_tcp_client = DogWorkerClient()

    def decoder_bind_cpu(self):
        bind_cpu(0x0001)

    def err_call(self, e):
        loguru.logger.trace(e)

    def push_msg(self, *args):
        self.err_push_trigger.emit(list(args))

    def set_setting(self, setting: DecoderSetting):
        self._config = setting

    def set_dog_config(self, setting: DogWalkDecodeSetting):
        self._dog_setting = setting

    def impedances(self):
        """
        filter 1000 10e6
        :return:
        """
        ...

    async def init(self):
        # self.decoder_bind_cpu()
        await self._dog_tcp_client.init()
        await self._imu_sub.init(pending_msgs_limit=8, err_call=self.err_call)
        await self._eeg_sub.init(pending_msgs_limit=40, err_call=self.err_call)

    async def collect_eeg(self):
        eeg_buffer = b''
        timestemps = []
        if self._eeg_length is None:
            msg = await self._eeg_sub.sub.next_msg()
            *eeg, eeg_meta = msg.data
            eeg_meta = json.loads(eeg_meta)
            self._start_eeg_ms = int(eeg_meta['datetime'])
            self._eeg_fs = eeg_meta['rate']
            self._config.neuro.neuro_sample_rate = self._eeg_fs
            self._eeg_channels = eeg_meta['channels']
            self._eeg_length = self._eeg_fs * self._config.bin_size * 2 * (eeg_meta['channels'] + 1)
            loguru.logger.info(f"_eeg_fs={self._eeg_fs}-_start_eeg_ms={self._start_eeg_ms}-_eeg_channels={self._eeg_channels};_eeg_length={self._eeg_length}")
            eeg_buffer += b''.join(eeg)
            timestemps.append(0)

        while True:
            if len(eeg_buffer) >= self._eeg_length:
                width = self._eeg_channels + 1
                size = int(len(eeg_buffer) // (width * 2))
                eeg_bins = np.ndarray(shape=(size, width), dtype=np.int16, buffer=eeg_buffer)
                eeg_bins = eeg_bins[:, -257:-1] if width > 257 else eeg_bins[:, :-1]
                return eeg_bins, timestemps
            try:
                msg = await self._eeg_sub.sub.next_msg(0.1)
                *eeg, eeg_meta = msg.data
                eeg_meta = json.loads(eeg_meta)
                timestemps.append(int(eeg_meta['datetime']) - self._start_eeg_ms)
                eeg_buffer += b''.join(eeg)
            except asyncio.TimeoutError as e:
                await self._imu_sub.clear_msg()
                return await self.collect_eeg()

    async def collect_imu(self, start_ms: int, end_ms: int = None):
        end_ms = start_ms + self._config.bin_size * 1000 if end_ms is None else end_ms
        timestemps = []
        imu_bins = []
        if self._imu_fs is None:
            msg = await self._imu_sub.sub.next_msg(0.1)
            imu = msg.data
            imu_dict = bson.loads(imu[0])
            self._imu_fs = imu_dict.get('fs', self._config.behavior.behavior_sample_rate)
            loguru.logger.debug(f"imu sample rate = {self._imu_fs}")
            self._config.behavior.behavior_sample_rate = self._imu_fs
            imu_bins.append(imu_dict['record']['acceleration'][self._dog_setting.motion_field])
            timestemps.append(int(imu_dict['record']['sys_time'] * 10e-7) - self._start_eeg_ms)

        while True:
            if timestemps and (timestemps[-1] >= end_ms or len(timestemps) == int(self._config.bin_size * self._imu_fs)):
                return imu_bins, timestemps
            try:
                if timestemps:
                    timeout = (end_ms- timestemps[-1]) / 1000
                else:
                    timeout = 0.09

                # msg = await self._imu_sub.sub.next_msg(0.001)
                msg = self._imu_sub.sub._pending_queue.get_nowait()
                self._imu_sub.sub._pending_size -= len(msg.data)
                imu = msg.data
                imu_dict = bson.loads(imu[0])
                timp = int(imu_dict['record']['sys_time'] * 10e-7) - self._start_eeg_ms
                if timp+10 < start_ms:
                    loguru.logger.debug(f"{self._start_eeg_ms} {int(imu_dict['record']['sys_time'] * 10e-7)} small {start_ms} imu {timp}, drop")
                    continue
                # else:
                #     print(imu_dict['record']['sys_time'] * 10e-7, self._start_eeg_ms)

                imu_bins.append(imu_dict['record']['acceleration'][self._dog_setting.motion_field])
                timestemps.append(timp)
            except QueueEmpty:
                return imu_bins, timestemps
            except asyncio.TimeoutError:
                # loguru.logger.error(f"timeout {len(imu_bins)} - timeout={timeout}")
                return imu_bins, timestemps

    def stop_decode(self):
        self.stop = True

    async def decode(self):
        await self.init()

        train = False
        while True:
            if self.stop:
                loguru.logger.info("stop ...")
                break

            try:
                eeg_bins, eeg_timestemps = await self.collect_eeg()
                imu_bins, imu_timestemps = await self.collect_imu(eeg_timestemps[0], eeg_timestemps[-1] + 10) # 10ms 一个数据包
                if not imu_bins:
                    loguru.logger.error("imu is null")

                if not train:
                    # if not imu_bins:
                    #     loguru.logger.warning(f"null behavior imu_bins={imu_bins} imu_timestemps={imu_timestemps}")
                    #     continue
                    self._train_eeg_x.append(eeg_bins)
                    self._train_imu_y.append(imu_bins)
                    self._train_imu_time.extend(imu_timestemps)
                    if len(self._train_eeg_x) >= self._config.nbins_train:
                        loguru.logger.info("start train")
                        train = True
                        integ_length = int(os.environ.get("integ_length", "600"))
                        loguru.logger.info(f"integ_length={integ_length}")
                        await self.train()
                        await self._eeg_sub.clear_msg()
                        await self._imu_sub.clear_msg()
                else:
                    start = time.time()
                    predict = await self.predict(eeg_bins)
                    norm_motion = await self.acc2pos_norm(imu_bins, imu_timestemps)
                    loguru.logger.warning(f"decoder={time.time() - start}")
                    await self._dog_tcp_client.send(predict)
                    self.message_push_trigger.emit({'pred': predict, 'motion': norm_motion[-1, :]})
                    # self.push_msg()
                    await self._eeg_sub.drop_msg()
                    await self._imu_sub.drop_msg()

            except Exception as e:
                loguru.logger.exception(e)
                self.push_msg(f"{traceback.format_exc()}")
                raise e

    async def acc2pos_norm(self, acc_data, imu_timestemps):
        self._train_imu_y.append(acc_data)
        self._train_imu_y.pop(0)
        # print(len(self._train_imu_time))
        self._train_imu_time.extend(imu_timestemps)

        trainY = np.concatenate(self._train_imu_y, axis=0)
        trainY.resize((trainY.shape[0], 1))
        loguru.logger.debug(f"acc to pos shape={trainY.shape}")
        self._train_imu_time = self._train_imu_time[len(self._train_imu_time) - trainY.shape[0]:]
        # print(trainY.shape, len(self._train_imu_time))
        integ_length = int(os.environ.get("integ_length", "600"))
        future = run_in_loop(self._decoder.m_acc_preprocess, trainY[-integ_length:], np.array(self._train_imu_time[-integ_length:]))
        return await future

    async def train(self):
        if self._decoder is None:
            loguru.logger.info(f"decode config = {self._config} dog =  {self._dog_setting}")
            self._decoder = DecoderService(self._config)
        trainY = np.concatenate(self._train_imu_y, axis=0)
        trainY.resize((trainY.shape[0], 1))
        loguru.logger.info(f"start train train_shape={trainY.shape} x={len(self._train_eeg_x)}")
        future = run_in_loop(self._decoder.train, self._train_eeg_x, trainY, np.array(self._train_imu_time))
        return await future
        # self._decoder.train(self._train_eeg_x, trainY, np.array(self._train_imu_time))

    async def predict(self,eeg_bins):
        return self._decoder.predict(eeg_bins)

    async def test(self):
        await self.init()
        await self.decode()


if __name__ == '__main__':
    neural_fs = 4000
    bad_chs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
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
        251, 252, 253, 254, 255]
    neuro_setting = NeuroSetting(neuro_sample_rate=neural_fs,
                                 neuro_freq_notch_filter=[50, 100, 200],
                                 neuro_quality_notch_filter=[50, 35, 50],
                                 neuro_freq_bandpass_filter=[0.3, 500],
                                 neuro_order_bandp_lowp_filter=4,
                                 neuro_bad_channels=bad_chs,
                                 neuro_time_half_bandwidth=2.5,
                                 neural_fbands=[[70, 200]],
                                 neuro_car=True,
                                 neuro_lmp=True
                                 )

    behavior = BehaviorSetting(behavior_inp_type=MotionInputTypeEnum.acc,
                               behavior_target_type=[TargetTypeEnum.pos, TargetTypeEnum.vel],
                               behavior_sample_rate=40,
                               behavior_input_filter="bandpass",
                               behavior_freq_cutoff=[1, 5],
                               behavior_target_filter="high",
                               behavior_target_freq_cutoff=1,
                               behavior_order_filter=4
                               )
    config = DecoderSetting(neuro=neuro_setting,
                            bin_size=0.1,
                            behavior=behavior,
                            nbins_train=30,
                            cross_validation_kfold=5,
                            ncomponents=0
                            )
    dog_walk = DogWalkDecoderService(config)
    asyncio.run(dog_walk.test())