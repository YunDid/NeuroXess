#!/usr/bin/env python3
"""
@Description  :   对给定的神经/运动数据对进行解码。
@Author       :   冉星辰 (ran.xingchen@qq.com)
@Created      :   2023/05/30 17:35:25
@Last Modified:   2023/06/12 09:48:03
"""
from sklearn.decomposition import PCA
from decoder.core import KalmanFilter

import numpy as np


class Decoder:
    def __init__(self, ncomponents, method="KF"):
        self.ncomponents = ncomponents
        self.pca = PCA(ncomponents, whiten=False) if ncomponents > 0 else None

        if method.upper() == "KF":
            self.decoder = KalmanFilter()

    def train(self, neural_data, motion_data, bias=True):
        # Normalize and take principal components of the neural data
        self.mu_neural = np.mean(neural_data, axis=0, keepdims=True)
        self.sd_neural = np.std(neural_data, axis=0, keepdims=True)
        Z = (neural_data - self.mu_neural) / self.sd_neural
        if self.pca is not None:
            Z = self.pca.fit_transform(Z)

        # Normalize the motion data
        self.mu_motion = np.mean(motion_data, axis=0, keepdims=True)
        self.sd_motion = np.std(motion_data, axis=0, keepdims=True)
        X = (motion_data - self.mu_motion) / self.sd_motion
        # Add bias to the motion data
        if bias:
            X = np.concatenate((X, np.ones((X.shape[0], 1))), axis=-1)

        # x0 is the initial target for some decoding method to
        # predict current target.
        self.x0 = X[-1]

        self.decoder.train(Z, X)

    def predict(self, neural_data):
        # Normalize and take principal components of the neural data
        Z = (neural_data - self.mu_neural) / self.sd_neural
        if self.pca is not None:
            Z = self.pca.transform(Z)

        pred = self.decoder.predict(Z, self.x0)
        # Update x0
        self.x0 = pred[-1]
        # Convert the scale back
        ndim = self.sd_motion.shape[-1]
        pred = pred[:, :ndim] * self.sd_motion + self.mu_motion
        return pred


def greedy_search_channels(train_x, train_y, test_x, test_y, tot_chs, tot_dim):
    # Initialize metrics
    best_ch = 0
    best_cc = -np.inf

    best_chs = []
    for _ in range(tot_chs):
        found_best = False

        decoder = Decoder(0)
        for i in range(tot_chs):
            if np.any(i == np.array(best_chs)):
                continue
            current_chs = np.asarray([*best_chs, i])
            Z0 = np.concatenate((train_x[:, current_chs],
                                 train_x[:, current_chs + tot_chs]), axis=1)
            Z1 = np.concatenate((test_x[:, current_chs],
                                 test_x[:, current_chs + tot_chs]), axis=1)
            decoder.train(Z0, train_y, bias=True)
            pred = decoder.predict(Z1)
            cc = 0
            for n in range(tot_dim):
                r = np.corrcoef(pred[:, n], test_y[:, n])
                cc += r[0, 1]
            cc /= tot_dim
            if cc > best_cc:
                best_cc = cc
                best_ch = i
                found_best = True

        if not found_best:
            break
        best_chs.append(best_ch)
    return best_chs, best_cc
