#!/usr/bin/env python3
"""
@Description :   在线解码示例
@Author      :   冉星辰 (ran.xingchen@qq.com)
@Created     :   2023/05/30 18:04:46
"""
import os
import scipy.io as scio
import numpy as np
import matplotlib.pyplot as plt
import time

from decoder.fitting import NeuralPreprocessOnline, MotionPreprocess, Decoder


"""
注意——目前的在线解码流程需要注意以下几个部分：

 -必要参数项
    1. 坏道列表（bad_chs）：以0-index起始的一个列表，标明输入的原始神经数据中哪些通道异常数据不可用，将在处理过程中剔除这些指定的坏道。
    2. 滤波频段（band_freq）：对原始数据进行带通滤波的频率范围。
    3. 陷波频率（notch_freq）：需要去除的工频以及工频谐波。
    4. 运动数据滤波（use_filter）：对于类似IMU这种采集数据极度不平滑的数据，可开启运动数据滤波。
    4. 解码窗宽（bin_size）：通过多长的数据来进行功率谱的估计以及解码。
    5. 解码频段（flim）：通过list设定指定的频段进行功率谱估计。
    6. 训练数据时长：对应示例中nbins_train，通过给定训练数据时长，换算nbins2train。
    7. 解码特征数（ncomponents）：通过PCA对所有通道的所有特征进行降维时的维数。
    8. 输入运动数据类型：MotionPreprocess的参数之一，当前仅支持输入为"pos"。
    9. 解码目标类型（target_type）：可选"pos", "vel", "acc", 以及通过连字符接应的任意类型，如"pos-vel"。
 -解码工作流
    1. 设定必要的参数。
    2. 攒够bin_size时长的数据，分别调用NeuralPreprocess().preprocessing和
       MotionPreprocess().preprocessing对数据进行预处理
    3. 重复步骤2直到攒够训练数据时长的数据量，将所有的训练数据输入到Decoder.train()中进行训练。
    4. 攒够bin_size时长的数据，预处理后调用Decoder.predict()得到解码输出。
    5. ...
"""


def run_example():
    data_path = r"F:\Public Dataset\JoystickTrack"
    subject = "RH_Male_38_rHand"
    neural_file = "RawNeural.mat"
    motion_file = "RawMotion.mat"
    bad_chs = [12, 13, 14, 20, 21, 22, 23, 28, 29, 30, 31]

    neural_path = os.path.join(data_path, subject, neural_file)
    motion_path = os.path.join(data_path, subject, motion_file)

    # Neural data reading
    neural_dict = scio.loadmat(neural_path)
    neural: np.ndarray = neural_dict["data"]
    neural_fs = float(neural_dict["fs"])
    L, N = neural.shape         # Number of total samples of neural data.
    N -= len(bad_chs)
    # Motion data reading
    motion_dict = scio.loadmat(motion_path)
    motion_x: np.ndarray = motion_dict["CursorPosX"]
    motion_y: np.ndarray = motion_dict["CursorPosY"]
    motion_fs = float(motion_dict["fs"])
    motion = np.concatenate((motion_x, motion_y), axis=-1)
    # Check if the data is validate.
    if (neural_fs == motion_fs):
        fs = neural_fs
        print("Yeah~")
    else:
        print("WTF...")
        return

    # Note in this example data, motion are same lengh with neural.
    # This is the timestamp of both type of data idealy
    T = np.arange(0, L)[:, np.newaxis] / fs
    # Preprocessing parameters
    bin_size = 0.1
    overlap = 0.0
    step = int((bin_size - overlap) * fs)
    nbins = int(np.ceil(L / step))
    flim = [[70, 200]]
    use_car = N > 1

    # This raw data are in frequency of 0.15-200Hz, so we filter it up to 200.
    nprocessor = NeuralPreprocessOnline(
        fs, fnotch=[60], qnotch=[30], fband=[0.3, 200], order=4,
        bad_chs=bad_chs
    )
    # Do not filter the raw motion data here.
    mprocessor = MotionPreprocess(inp_type="pos", trg_type="pos-vel", fs=fs)
    # Simulate the online situation.
    ncomponents = 50
    decoder = Decoder(ncomponents)
    nbins_train = nbins // 5 * 4
    trainX = np.zeros((nbins_train, N * (len(flim) + 1)))
    bufferY = []        # To collect the training motion data.
    bufferT = []
    testY, predY = [], []
    count = 0
    t1 = time.time()
    for i in range(0, L, step):
        n = int(bin_size * fs)
        bin_neural = neural[i:i + n]
        bin_motion = motion[i:i + n]

        x = nprocessor.preprocessing(bin_neural, nw=2.5, flim=flim,
                                     car=use_car, fres=1, lmp=True)
        if count < nbins_train:
            trainX[count] = x.ravel(order="F")
            bufferY.append(bin_motion)  # Motion data of current bin
            bufferT.append(T[i:i + n])
        elif count == nbins_train:
            bufferY = np.concatenate(bufferY, axis=0)
            bufferT = np.concatenate(bufferT, axis=0)
            trainY = mprocessor.bin_data(bufferY, bufferT, bin_size)
            decoder.train(trainX, trainY, bias=True)
            print("\nTraining complete!\n")
            predY.append(decoder.predict(x.ravel(order="F")[np.newaxis, :]))
        else:
            predY.append(decoder.predict(x.ravel(order="F")[np.newaxis, :]))
        count += 1
        if count % 100 == 0:
            print(f"Average cost time: {(time.time() - t1) / 100}")
            t1 = time.time()

    # Computing CC and plot
    binned_motion_all = mprocessor.bin_data(motion, T, bin_size)
    testY = binned_motion_all[nbins_train:]     # Computing acutal test data.
    predY = np.concatenate(predY, axis=0)
    r_vx = np.corrcoef(predY[:, 0], testY[:, 0])[0, 1]
    r_vy = np.corrcoef(predY[:, 1], testY[:, 1])[0, 1]
    r_px = np.corrcoef(predY[:, 2], testY[:, 2])[0, 1]
    r_py = np.corrcoef(predY[:, 3], testY[:, 3])[0, 1]

    print(f"R_v=[{r_vx:.2f}, {r_vy:.2f}]\tR_p=[{r_px:.2f}, {r_py:.2f}]")
    print(f"R_average={(r_vx + r_vy + r_px + r_py) / 4:.2f}")

    plt.subplot(4, 1, 1)
    plt.plot(predY[:, 2])
    plt.plot(testY[:, 2])
    plt.ylabel("Position X")
    plt.subplot(4, 1, 2)
    plt.plot(predY[:, 3])
    plt.plot(testY[:, 3])
    plt.ylabel("Position Y")
    plt.subplot(4, 1, 3)
    plt.plot(predY[:, 0])
    plt.plot(testY[:, 0])
    plt.ylabel("Velocity X")
    plt.subplot(4, 1, 4)
    plt.plot(predY[:, 1])
    plt.plot(testY[:, 1])
    plt.ylabel("Velocity Y")
    plt.legend(["Decoded", "Actual"])
    plt.show()


if __name__ == "__main__":
    run_example()
