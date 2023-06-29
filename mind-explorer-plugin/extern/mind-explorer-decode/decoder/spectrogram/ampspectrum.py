#!/usr/bin/env python3
"""
@Description :   计算指定频率范围内的功率谱
@Author      :   冉星辰 (ran.xingchen@qq.com)
@Created     :   2023/05/24 15:41:43
"""
import numpy as np
import matplotlib.pyplot as plt

from scipy.fft import fft


def compute_amp_spectrum(X: np.ndarray, fs: float, fmin: float = 0.0,
                         fmax: float = 250.0):
    L, _ = X.shape
    f = fs * np.arange(0, L // 2 + 1) / L
    Y = fft(X, axis=0)
    P2 = np.abs(Y / L)
    P1 = P2[:L // 2 + 1]
    P1[1:-1] *= 2.0

    assert fmin >= f[0] and fmax <= f[-1], "Wrong parameter 'fmin' / 'fmax'!"

    indices = (f >= fmin) & (f < fmax)
    x = f[indices]
    y = P1[indices]
    return x, y


if __name__ == "__main__":
    a0 = 2
    a1 = 3
    a2 = 1.5
    a3 = 4.8
    f1 = 50
    f2 = 75
    f3 = 160
    fs = 4000
    p1 = -30
    p2 = 90
    p3 = 45

    T = np.linspace(0.0, 10.0, fs * 10)
    S = a0 + \
        a1 * np.cos(2 * np.pi * f1 * T + np.pi * p1 / 180) + \
        a2 * np.cos(2 * np.pi * f2 * T + np.pi * p2 / 180) + \
        a3 * np.cos(2 * np.pi * f3 * T + np.pi * p3 / 180)
    S = S[:, np.newaxis]
    x, y = compute_amp_spectrum(S, fs)

    plt.subplot(2, 1, 1)
    plt.plot(T, S)
    plt.subplot(2, 1, 2)
    plt.plot(x, y)
    plt.show()
