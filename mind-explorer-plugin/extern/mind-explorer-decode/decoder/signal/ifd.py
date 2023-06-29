#!/usr/bin/env python3
"""
@Description :   频域积分算法
@Author      :   冉星辰 (ran.xingchen@qq.com)
@Created     :   2023/06/09 11:10:52
"""
import numpy as np
import scipy.io as scio
import os

from numpy.fft import fft, fftshift, ifft, ifftshift


def fdomain_integration(y: np.ndarray, dt: float):
    """
    Computes integration of discrete time-signal in frequency domain by
    dividing spectrum with iw (w = cyclic frequency).

    Parameters
    ----------
    y: array_like
        The input array to do integration, it should be 1D array.
    dt : float
        Delta time.
    """
    N = y.size
    T = N * dt      # Calculate length of the time record.

    # Compute shifted FFT
    z = fftshift(fft(y))
    df = 1.0 / T

    # Check if N is even or odd
    L = np.arange(-N / 2, N / 2) if N % 2 == 0 else \
        np.arange(-(N - 1) / 2, (N - 1) / 2 + 1)
    f = np.squeeze(df * L)  # Make sure f is 1d array.
    # Get the cyclic frequency
    w = 2 * np.pi * f
    # Integrate in frequency domain by dividing spectrum with iomega
    inzero = w != 0
    z_new = np.zeros_like(z)
    z_new[inzero] = z[inzero] * (-1j) / w[inzero]
    # Compute inverse FFT.
    yp = ifft(ifftshift(z_new))
    return yp.real


if __name__ == "__main__":
    cur_path = os.path.split(os.path.abspath(__file__))[0]
    dat_path = os.path.join(cur_path, "..", "..", "data", "ExampleAcc.mat")
    data_dict = scio.loadmat(dat_path)
    acc = data_dict["acc"][:, 0]
    dt = float(data_dict["dt"])
    vel = fdomain_integration(acc, dt)

    save_path = os.path.join(cur_path, "..", "..", "out")
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    scio.savemat(os.path.join(save_path, "InteVel.mat"), {"py_vel": vel})
