import time
from typing import List

import loguru
import numpy as np
from decoder.fitting import NeuralPreprocessOnline, MotionPreprocess, Decoder, greedy_search_channels
from me_worker.errors.my_errors import BaseError

from app.config.decoder_setting import DecoderSetting, TargetTypeEnum, NeuroSetting, BehaviorSetting, \
    MotionInputTypeEnum


class DecoderErr(BaseError):
    message = "解码错误"


class DecoderTrianInputErr(DecoderErr):
    message = "输入的训练数据不足"


class DecoderService:
    def __init__(self, decode_conf: DecoderSetting):
        self._decode_conf = decode_conf
        self.decoder = Decoder(self._decode_conf.ncomponents)
        self.nprocessor = NeuralPreprocessOnline(np.array(self._decode_conf.neuro.neuro_sample_rate),
                                                 fnotch=self._decode_conf.neuro.neuro_freq_notch_filter,
                                                 qnotch=self._decode_conf.neuro.neuro_quality_notch_filter,
                                                 fband=self._decode_conf.neuro.neuro_freq_bandpass_filter,
                                                 order=self._decode_conf.neuro.neuro_order_bandp_lowp_filter,
                                                 bad_chs=self._decode_conf.neuro.neuro_bad_channels)
        # Do not filter the raw motion data here.
        self.mprocessor: MotionPreprocess = MotionPreprocess(inp_type=self._decode_conf.behavior.behavior_inp_type.value,
                                                             trg_type="-".join(self._decode_conf.behavior.behavior_target_type),
                                                             fs=np.array(self._decode_conf.behavior.behavior_sample_rate),
                                                             inp_filter=self._decode_conf.behavior.behavior_input_filter,
                                                             inp_fc=self._decode_conf.behavior.behavior_freq_cutoff,
                                                             trg_filter=self._decode_conf.behavior.behavior_target_filter,
                                                             trg_fc=self._decode_conf.behavior.behavior_target_freq_cutoff,
                                                             order=self._decode_conf.behavior.behavior_order_filter
                                                             )
        self.good_channels = np.array([], dtype=np.int32)

    def m_acc_preprocess(self, bin_motion_acc, time_stamp):
        """
        加速度转速度和位置
        :param bin_motion:
        :param time_stamp:
        :return:
        """
        acc = np.concatenate((bin_motion_acc, np.zeros_like(bin_motion_acc)))
        timestamp = np.concatenate((time_stamp, np.arange(time_stamp[-1] + 100, time_stamp[-1] + (time_stamp.shape[0] + 1) * 100, 100)))
        y = self.mprocessor.bin_data(acc, timestamp / 1000, bin_size=self._decode_conf.bin_size, dim=[0])
        return y[:int(np.ceil((time_stamp[-1] - time_stamp[0]) / 100))]

    def train(self, bin_neurals: List[np.ndarray], bin_motions: np.ndarray, time_stamp: np.ndarray, bias=True):
        """

        :param bin_neural: np.ndarray, shape=(x, neural_channel_num)
        :param bin_motion: np.ndarray, shape=(x, motion_channel_num)
        :param time_stamp: np.ndarray, shape=(x, 1)
        :param bias:
        :return: None
        """
        if len(bin_neurals) < self._decode_conf.nbins_train:
            raise DecoderTrianInputErr(message="脑电数据小于训练的最小要求")

        if len(bin_motions) < self._decode_conf.nbins_train:
            raise DecoderTrianInputErr(message="运动数据小于训练的最小要求")

        bbins_train = min(len(bin_neurals), len(bin_motions))

        L, neural_chs = bin_neurals[0].shape  # Number of total samples of neural data.
        neural_chid = np.arange(neural_chs)  # Neural channel id.
        neural_chid = np.delete(neural_chid, self._decode_conf.neuro.neuro_bad_channels)
        self.good_chs = neural_chid

        neural_chs -= len(self._decode_conf.neuro.neuro_bad_channels)
        use_car = neural_chs > 1

        neural_nfeats = len(self._decode_conf.neuro.neural_fbands) + self._decode_conf.neuro.neuro_lmp
        neural_nfeats *= neural_chs
        # train_val_neural = np.zeros((train_val_size, neural_nfeats))
        trainX = np.zeros((bbins_train, neural_chs * (len(self._decode_conf.neuro.neural_fbands) + 1)))
        # trainY = np.zeros((bbins_train, 4))
        trainY = self.m_acc_preprocess(bin_motions, time_stamp)

        # neural_chid = np.arange(neural_chs)  # Neural channel id.
        # neural_chs -= len(self._decode_conf.neuro.neuro_bad_channels)


        for i in range(bbins_train):
            # loguru.logger.debug(f"start loop {i}")
            bin_neural = bin_neurals[i]
            x = self.nprocessor.preprocessing(bin_neural, nw=self._decode_conf.neuro.neuro_time_half_bandwidth,
                                              flim=self._decode_conf.neuro.neural_fbands,
                                              car=use_car,
                                              fres=1.0,
                                              lmp=self._decode_conf.neuro.neuro_lmp)
            trainX[i] = x.ravel(order="F")

        self.cross_validation(self._decode_conf.nbins_train, trainX, trainY[:trainX.shape[0], :], neural_chid)
        # Training the decoder with whole training dataset.
        Z0 = np.concatenate((trainX[:, self.good_chs],
                             trainX[:, self.good_chs + neural_chs]), axis=1)  # noqa: E501
        self.decoder.train(Z0, trainY[:trainX.shape[0], :], bias=bias)

    def cross_validation(self, train_val_size, train_neuraldata, train_val, neural_chid):
        # Do K-fold cross validation
        val_size = train_val_size // self._decode_conf.cross_validation_kfold
        all_good_chs = np.array([], dtype=np.int32)  # Save good channels
        all_best_ccs = np.zeros((self._decode_conf.cross_validation_kfold,))  # Save best cc
        neural_chs = neural_chid.shape[0]
        motion_nmd = len(self._decode_conf.behavior.behavior_target_type)
        for k in range(self._decode_conf.cross_validation_kfold):
            loguru.logger.info(f"\nRunning fold {k + 1}...")
            # Indices of current fold's test data.
            ibeg_val = k * val_size
            iend_val = ibeg_val + val_size
            # Train data
            train_neural = np.concatenate((train_neuraldata[:ibeg_val],
                                           train_neuraldata[iend_val:]))
            train_motion = np.concatenate((train_val[:ibeg_val],
                                           train_val[iend_val:]))
            # Validation data
            val_neural = train_neuraldata[ibeg_val:iend_val]
            val_motion = train_val[ibeg_val:iend_val]
            # Searching the best channels in this fold.
            good_chs, best_cc = greedy_search_channels(
                train_neural, train_motion, val_neural, val_motion,
                neural_chs, motion_nmd
            )
            all_good_chs = np.append(all_good_chs,
                                     np.array(good_chs, dtype=np.int32))
            all_best_ccs[k] = best_cc

            loguru.logger.info(f"Found good channles: {neural_chid[good_chs]}")
            loguru.logger.info(f"Average CC of this fold: {best_cc:.4f}")

        self.good_chs = np.unique(all_good_chs)
        return self.good_chs


    def predict(self, bin_neural: np.ndarray):
        """

        :param bin_neural: np.ndarray, shape=(x, neural_channel_num)
        :return: np.ndarray, shape=(1, N)
        """
        start = time.time()
        L, N = bin_neural.shape  # Number of total samples of neural data.
        N -= len(self._decode_conf.neuro.neuro_bad_channels)
        use_car = N > 1
        x = self.nprocessor.preprocessing(bin_neural, nw=self._decode_conf.neuro.neuro_time_half_bandwidth,
                                          flim=self._decode_conf.neuro.neural_fbands,
                                          car=use_car,
                                          fres=1.0,
                                          lmp=self._decode_conf.neuro.neuro_lmp)
        Z1 = x[self.good_chs].ravel(order="F")
        pred = self.decoder.predict(Z1)
        loguru.logger.warning(f"time={time.time() - start}")
        return pred

class DecoderServiceMock:
    def __init__(self, *args, **kwargs):
        ...

    def train(self, *args, **kwargs):
        ...

    def predict(self, *args, **kwargs):
        ...


def test_decoder_service():
    import matplotlib.pyplot as plt
    import os
    import h5py

    def __reading_mat_v7_3(data_path):
        data_dict = {}
        with h5py.File(data_path) as f:
            for k, v in f.items():
                data_dict[k] = np.asarray(v) if v.size > 1 else np.squeeze(v)
        return data_dict

    data_path = r"D:\develop\py\mind-explorer-plugin\extern\mind-explorer-decode"
    # subject = "RH_Male_38_rHand"
    neural_file = "test/data/Neural/AlignedTestNeural.mat"
    motion_file = "test/data/Motion/AlignedTestMotion.mat"

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

    neural_path = os.path.join(data_path, neural_file)
    motion_path = os.path.join(data_path, motion_file)

    # Neural data reading
    neural_dict = __reading_mat_v7_3(neural_path)
    neural_data: np.ndarray = neural_dict["neural"].T  # (C, T) -> (T, C)
    neural_fs = neural_dict["neural_fs"]

    motion_dict = __reading_mat_v7_3(motion_path)
    motion_data: np.ndarray = motion_dict["motion"].T  # (D, T) -> (T, D)
    motion_fs = motion_dict["motion_fs"]
    motion_ts: np.ndarray = np.squeeze(motion_dict["motion_ts"]) * 1000

    target_type = [TargetTypeEnum.pos, TargetTypeEnum.vel]

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
                               behavior_sample_rate=motion_fs,
                               behavior_input_filter="bandpass",
                               behavior_freq_cutoff=[1, 5],
                               behavior_target_filter="high",
                               behavior_target_freq_cutoff=1,
                               behavior_order_filter=4
                               )
    config = DecoderSetting(neuro=neuro_setting,
                            bin_size=0.1,
                            behavior=behavior,
                            nbins_train=3000,
                            cross_validation_kfold=5,
                            ncomponents=0
                            )

    # bin_size = int(neural_fs * config.bin_size)

    trainX = []
    trainY = []
    motion_time_buffer = []
    trained = False

    print(config)
    decoder_service = DecoderService(config)

    plt.ion()  # 开启一个画图的窗口进入交互模式，用于实时更新数据
    # plt.rcParams['savefig.dpi'] = 200 #图片像素
    # plt.rcParams['figure.dpi'] = 200 #分辨率
    plt.rcParams['figure.figsize'] = (10, 10)  # 图像显示大小
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 防止中文标签乱码，还有通过导入字体文件的方法
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['lines.linewidth'] = 0.5  # 设置曲线线条宽度

    plt.suptitle("总标题", fontsize=30)

    pX = [0 for i in range(100)]
    pY = [0 for i in range(100)]

    tX = [0 for i in range(100)]
    tY = [0 for i in range(100)]
    #
    # T = np.arange(0, bin_size)[:, np.newaxis] / neural_fs
    bin_size = 4000 * config.bin_size

    size = int(neural_data.shape[0] // bin_size)

    for i in range(0, size):
        neuro_bin = neural_data[int(i*bin_size):int((i+1)*bin_size), :]
        motion_bin = motion_data[int(i * 4):int((i + 1)*4), :]
        if len(neuro_bin) < bin_size or len(motion_bin) < 4:
            break

        if trained is False:
            trainX.append(neuro_bin)
            trainY.append(motion_bin)
            motion_time_buffer.append(motion_ts[int(i * 4):int((i + 1)*4)])
            if len(trainX) == config.nbins_train:
                trained = True
                y = np.concatenate(trainY, axis=0)
                motion_time_buffer_np = np.concatenate(motion_time_buffer, axis=0)
                decoder_service.train(bin_motions=y, bin_neurals=trainX, time_stamp=motion_time_buffer_np)
        else:
            plt.clf()  # 清除刷新前的图表，防止数据量过大消耗内存
            pred = decoder_service.predict(neuro_bin)[0]
            y = motion_data[int(i * 4):int((i + 1)*4), :]
            trainY.append(y)
            trainY.pop(0)
            motion_time_buffer.append(motion_ts[int(i * 4):int((i + 1)*4)])
            motion_time_buffer.pop(0)
            binned_motion = decoder_service.m_acc_preprocess( np.concatenate(trainY, axis=0),
                                                              np.concatenate(motion_time_buffer, axis=0))

            tX.append(binned_motion[-1][0])
            tX.pop(0)
            tY.append(binned_motion[-1][1])
            tY.pop(0)
            pX.append(pred[0])
            pX.pop(0)
            pY.append(pred[1])
            pY.pop(0)
            vX = plt.subplot(2, 1, 1)
            plt.ylabel("Velocity")
            plt.plot(tX)
            plt.plot(pX)
            vY = plt.subplot(2, 1, 2)
            plt.ylabel("pos")
            plt.plot(tY)
            plt.plot(pY)
            plt.legend(["Actual", "Decoded"])
            plt.pause(0.4)
            v_c = np.corrcoef(tX, pX)
            p_c = np.corrcoef(tY, pY)
            loguru.logger.debug(f"current_pred={pred};cc={v_c[0][1]} {p_c[0][1]}")
            # loguru.logger.info(pred)

    plt.ioff()  # 关闭画图的窗口，即关闭交互模式
    plt.show()  # 显示图片，防止闪退


if __name__ == '__main__':
    test_decoder_service()
