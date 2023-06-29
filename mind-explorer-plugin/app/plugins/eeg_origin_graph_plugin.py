import queue
import time
from scipy.fft import fft

import loguru
import numpy as np
import bson as bson

from app.utils.asyncqt5 import async_qt
from app.utils.run_in_loop import run_in_loop
from me_worker.model.data_cc_raw_model import CollectRawDataSubModel
from me_worker.service.msg_service.service import Service
from me_worker.service.msg_service.topic import *
from decoder.preprocess.preprocess import NeuralPreprocess


async def cul_spectrum():
    ...


async def fft_run(eeg_data_channgels, callback):
    Ys = []
    ps_list = []

    for eeg_data in eeg_data_channgels:
        Y = fft(eeg_data)
        ps = Y ** 2 / len(Y)
        Y = Y[:200]
        Ys.append(np.abs(Y).tolist())
        ps_list.append(ps)

    ps_list = np.array(ps_list).T
    ps_list = np.log10(ps_list) * 5
    # ps_list = ps_list * (1 + 0.2 * np.random.random(ps_list.shape))
    # print(np.max(ps_list), np.min(ps_list))

    if callback:
        callback((Ys, ps_list))


class EEGRAwDataPlugin(Service):
    topic = SUB_DATA_CC_RAW_RT
    start = False
    msg_queue: queue.Queue = None
    num = 0

    def __init__(self, callback=None):
        self._cache_buffer = b''
        self._cache_ms = 1000
        self._band_freq = [0.3, 500]
        self._neuro_preprocess:NeuralPreprocess = None
        self.pending_task_num = setting.rt_pending_num
        self._callbck = callback
        super().__init__()

    async def init_preprocess(self, sample_rate):
        self._neuro_preprocess = NeuralPreprocess(sample_rate, band_freq=self._band_freq)

    async def err_call(self, e, *args, **kwargs):
        if self.sub:
            loguru.logger.warning(f"{e}-{self.sub.pending_msgs}-{self.sub._pending_msgs_limit}-{self.sub.pending_bytes // (1024 * 1024)}")
        else:
            loguru.logger.warning(f"{e}")

    async def drop_msg(self):
        drop_size = 0
        if self.sub.pending_msgs > setting.rt_pending_num // 2:
            drop_size = int(setting.rt_pending_num * 0.1)
        elif self.sub.pending_bytes > setting.rt_pending_bytes // 2:
            drop_size = int(self.sub.pending_msgs * 0.5)
        if drop_size > 0:
            loguru.logger.error(f"pending msg is {self.sub.pending_msgs}, drop {drop_size}")
            for i in range(drop_size):
                try:
                    msg = self.sub._pending_queue.get_nowait()
                    self.sub._pending_size -= len(msg.data)
                except Exception as e:
                    loguru.logger.error(e)

    def neuro_preprocess(self, eeg_data,):
        Ys = []
        try:
            t = time.time()
            eeg_data = eeg_data[:, :-1]
            eeg_data_channgels = eeg_data.T
            for eeg_data_ in eeg_data_channgels:
                Y = fft(eeg_data_)

                Y = Y[:200]
                Ys.append(np.abs(Y).tolist())
            loguru.logger.error(f"time={time.time() - t}")
                # ps = Y ** 2 / len(Y)
            # loguru.logger.info(f"shape={eeg_data.shape}")
            ps_list = np.zeros((eeg_data.shape[1], int(self._cache_ms // 100)))
            for i in range(int(self._cache_ms // 100)):
                ps = self._neuro_preprocess.preprocessing(eeg_data[i:(i+1)*100, :], nw=2.5, use_car=False)
                ps_list[:, i] = ps[:, 0]

            loguru.logger.error(f"time={time.time() - t},shape={ps_list.shape}")
        except Exception as e:
            loguru.logger.exception(e)
            raise e

        if self._callbck:
            loguru.logger.error("neuro_preprocess run")
            self._callbck((Ys, ps_list))

    async def async_neuro_preprocess(self, eeg_data):
        return await run_in_loop(self.neuro_preprocess, eeg_data)

    async def sub_callback(self, msg):
        buffer = msg.data
        d_bson = bson.loads(buffer)
        model = CollectRawDataSubModel.parse_obj(d_bson)
        self._cache_buffer += model.buffer
        channel = model.channels + 1
        if self._neuro_preprocess is None:
            await self.init_preprocess(model.sample_rate)

        if len(self._cache_buffer) >= self._cache_ms * (model.sample_rate // 1000) * 2 * (channel):
            size = int(len(self._cache_buffer) // channel // 2)
            eeg_data = np.ndarray((size, channel), buffer=self._cache_buffer, dtype=np.int16)
            # async_qt.async_run(self.neuro_preprocess(eeg_data))
            await self.async_neuro_preprocess(eeg_data)
            self.reset_buffer()
            await self.drop_msg()

    def cul_fft(self, eeg_data_channgels):
        Ys = []
        for eeg_data in eeg_data_channgels:
            Y = fft(eeg_data)
            Ys.append(np.abs(Y).tolist())
        return Ys


    def reset_buffer(self):
        self._cache_buffer = b''

