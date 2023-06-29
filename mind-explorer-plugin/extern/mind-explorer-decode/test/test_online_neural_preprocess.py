#!/usr/bin/env python3
# flake8: noqa
"""
@Description :   BCI神经数据预处理示例。
@Author      :   冉星辰 (ran.xingchen@qq.com)
@Created     :   2023/05/25 14:00:53
"""
import argparse
import os
import scipy.io as scio
import numpy as np
import matplotlib.pyplot as plt

from decoder.fitting import NeuralPreprocessOnline
from time import time


plt.ion()


def main(data_path, session_name, file_name, prnt=False, plot=True):
    file_path = os.path.join(data_path, session_name, file_name)
    data_dict = scio.loadmat(file_path)
    neural: np.ndarray = data_dict["data"]
    fs = float(data_dict["fs"])
    # To removing bad channels
    bad_chs = [12, 13, 14, 20, 21, 22, 23, 28, 29, 30, 31]

    # Parameters setting.
    nsamps, _ = neural.shape
    bin_size = 0.1      # Seconds
    overlap = 0.0
    step = int((bin_size - overlap) * fs)
    time2plot = 20      # Seconds
    bins2plot = int(time2plot / bin_size)
    
    # Feed the data in stream.
    t1 = time()

    online_processor = NeuralPreprocessOnline(
        fs, fnotch=[60], qnotch=[30], fband=[0.3, 200], order=4, bad_chs=bad_chs
    )

    P_list = []
    bin_count = 0
    for i in range(0, nsamps, step):
        n = int(bin_size * fs)
        current_neural = neural[i:i + n, :]
        P = online_processor.preprocessing(current_neural, nw=2.5, flim=[[70, 200]])[:, np.newaxis]

        bin_count += 1
        if (prnt and bin_count % 100 == 0):
            print(f"Average cost time of 100 iteration:{(time() - t1) / 100}")
            t1 = time()
        
        if plot:
            P_list.append(P)
            if len(P_list) > bins2plot:
                P_list = P_list[1:]
            Parray = np.concatenate(P_list, axis=1)
            plt.cla()
            plt.imshow(Parray)
            plt.xlim(0, bins2plot)        # 10 seconds
            plt.clim([0, 8000])
            plt.draw()
            plt.pause(0.01)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Example of BCI data preprocessing.")
    parser.add_argument("-d",
                        type=str,
                        default=r"F:\Public Dataset\JoystickTrack",
                        help="Target folder where the data located.")
    parser.add_argument("-s",
                        type=str,
                        default="RH_Male_38_rHand",
                        help="Which session of the data to be processed,")
    parser.add_argument("-f",
                        type=str,
                        default="RawNeural.mat")
    args = parser.parse_args()

    data_path = args.d
    session_name = args.s
    file_name = args.f

    main(data_path, session_name, file_name, plot=True, prnt=False)
