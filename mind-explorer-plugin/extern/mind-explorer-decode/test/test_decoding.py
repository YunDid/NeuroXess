#!/usr/bin/env python3
# flake8: noqa
"""
@Description  :   使用Kalman滤波对神经信号进行解码示例。
@Author       :   冉星辰 (ran.xingchen@qq.com)
@Created      :   2023/05/26 15:02:02
@Last Modified:   2023/06/12 10:57:52
"""
import argparse
import os
import numpy as np
import scipy.io as scio
import matplotlib.pyplot as plt

from decoder.fitting import NeuralPreprocess, MotionPreprocess
from decoder.core import KalmanFilter
from sklearn.decomposition import PCA


def main(data_path, session_name, neural_file, motion_file, bad_chs=[], neural_components=50):
    neural_path = os.path.join(data_path, session_name, neural_file)
    motion_path = os.path.join(data_path, session_name, motion_file)

    # Neural data reading
    neural_dict = scio.loadmat(neural_path)
    neural: np.ndarray = neural_dict["data"]
    neural_fs = float(neural_dict["fs"])
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
    bin_size = 0.1
    flim = [[70, 200]]
    # Preprocessing the raw data.
    step = int(bin_size * fs)
    if neural.shape[0] % step != 0:
        L1 = int(neural.shape[0] // step * step)
        neural = neural[:L1]
        motion = motion[:L1]
    # Timestamp of both type of data idealy
    T = np.arange(0, neural.shape[0])[:, np.newaxis] / fs
    
    # This raw neural data are in frequency of 0.15-200Hz, so we filter it up to 200.
    neural_processor = NeuralPreprocess(fs, fnotch=[60], qnotch=[30], fband=[0.3, 200], order=4, bad_chs=bad_chs)
    # Do not filter the raw motion data here.
    motion_processor = MotionPreprocess(inp_type="pos", trg_type="pos-vel", fs=fs)
    X = neural_processor.bin_data(neural, nw=2.5, flim=flim, bin_size=bin_size, lmp=True)
    Y = motion_processor.bin_data(motion, T, bin_size)

    kfold = 5       # 5 fold cross validation.
    test_length = X.shape[0] // kfold
    R = []
    for k in range(kfold):
        test_X = X[k * test_length:(k + 1) * test_length]
        test_Y = Y[k * test_length:(k + 1) * test_length]
        train_X = np.concatenate((X[:k * test_length], X[(k + 1) * test_length:]), axis=0)
        train_Y = np.concatenate((Y[:k * test_length], Y[(k + 1) * test_length:]), axis=0)
        # Normalize the data
        mu_X = np.mean(train_X, axis=0, keepdims=True)
        sigma_X = np.std(train_X, axis=0, keepdims=True)
        mu_Y = np.mean(train_Y, axis=0, keepdims=True)
        sigma_Y = np.std(train_Y, axis=0, keepdims=True)
        train_X = (train_X - mu_X) / sigma_X
        train_Y = (train_Y - mu_Y) / sigma_Y
        test_X = (test_X - mu_X) / sigma_X
        test_Y = (test_Y - mu_Y) / sigma_Y
        # Do dimensionality reduction.
        if neural_components > 0:
            pca = PCA(neural_components)
            train_X = pca.fit_transform(train_X)
            test_X = pca.transform(test_X)
        # Add bias to motion data
        train_Y = np.concatenate((train_Y, np.ones((train_Y.shape[0], 1))), axis=1)
        test_Y = np.concatenate((test_Y, np.ones((test_Y.shape[0], 1))), axis=1)
        # Get the initial state of motion
        y0 = test_Y[0] if k == 0 else train_Y[k * test_length - 1]

        # Initialize Kalman filter.
        kf = KalmanFilter()
        kf.train(train_X, train_Y)
        pred = kf.predict(test_X, y0)

        r_vx = np.corrcoef(pred[:, 0], test_Y[:, 0])[0, 1]
        r_vy = np.corrcoef(pred[:, 1], test_Y[:, 1])[0, 1]
        r_px = np.corrcoef(pred[:, 2], test_Y[:, 2])[0, 1]
        r_py = np.corrcoef(pred[:, 3], test_Y[:, 3])[0, 1]
        R.append(np.array([r_vx, r_vy, r_px, r_py]))

    R = np.stack(R, axis=0)
    print(f"R_vx in all {kfold} fold: {R[:, 0]}, median={np.median(R[:, 0]):.2f}")
    print(f"R_vy in all {kfold} fold: {R[:, 1]}, median={np.median(R[:, 1]):.2f}")
    print(f"R_px in all {kfold} fold: {R[:, 2]}, median={np.median(R[:, 2]):.2f}")
    print(f"R_py in all {kfold} fold: {R[:, 3]}, median={np.median(R[:, 3]):.2f}")
    print(f"\nAverage R={np.mean(R):.2f}")

    plt.subplot(4, 1, 1)
    plt.plot(pred[:, 2])
    plt.plot(test_Y[:, 2])
    plt.ylabel("Position X")
    plt.subplot(4, 1, 2)
    plt.plot(pred[:, 3])
    plt.plot(test_Y[:, 3])
    plt.ylabel("Position Y")
    plt.subplot(4, 1, 3)
    plt.plot(pred[:, 0])
    plt.plot(test_Y[:, 0])
    plt.ylabel("Velocity X")
    plt.subplot(4, 1, 4)
    plt.plot(pred[:, 1])
    plt.plot(test_Y[:, 1])
    plt.ylabel("Velocity Y")
    plt.legend(["Decoded", "Actual"])
    plt.show()


def run_test1(data_path):
    subject = "RH_Male_38_rHand"
    neural_file = "RawNeural.mat"
    motion_file = "RawMotion.mat"
    bad_chs = [12, 13, 14, 20, 21, 22, 23, 28, 29, 30, 31]
    main(data_path, subject, neural_file, motion_file, bad_chs, neural_components=50)

def run_test2(data_path):
    subject = "FP_Male_23_rHand"
    neural_file = "RawNeural.mat"
    motion_file = "RawMotion.mat"
    bad_chs = [2, 4, 11, 12]
    main(data_path, subject, neural_file, motion_file, bad_chs, neural_components=90)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Example of BCI data preprocessing.")
    parser.add_argument("-r", type=str, default="test1", help="Which test to run.")
    args = parser.parse_args()

    test_id: str = args.r

    cur_path = os.path.split(os.path.abspath(__file__))[0]
    data_path = os.path.join(cur_path, "..", "data", "PublicDataset", "JoystickTrack")
    if test_id.lower() == "test1":
        run_test1(data_path)
    elif test_id.lower() == "test2":
        run_test2(data_path)
