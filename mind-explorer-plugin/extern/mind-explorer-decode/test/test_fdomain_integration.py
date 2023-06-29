#!/usr/bin/env python3
"""
@Description :   Input a sine signal to see what happen.
@Author      :   冉星辰 (ran.xingchen@qq.com)
@Created     :   2023/06/10 10:47:34
"""

# Input is 15 Hz sinusoidal signal sampled at 200Hz.
# Compare frequency-domain integration with analytical solution


import numpy as np
import matplotlib.pyplot as plt

from decoder.signal import fdomain_integration

if __name__ == "__main__":
    n = 128         # Number of sample points
    fs = 200
    dt = 1 / fs
    t = np.arange(0, n) * dt    # Time range
    T = dt * n          # Total sampling time

    # Make a 15Hz sine wave
    y = np.sin(2 * np.pi * 15 * t / T)
    # Frequency domain integration
    z1 = fdomain_integration(y, dt)
    # Compare with the analytical results.
    z2 = -np.cos(2 * np.pi * 15 * t / T) / (2 * np.pi * 15 / T)

    # Check the results
    plt.subplot(2, 1, 1)
    plt.plot(t, z1, t, z2)
    plt.legend(["fdomain", "analytical"])
    plt.subplot(2, 1, 2)
    plt.plot(t, z2 - z1)
    plt.ylabel("Error")
    plt.show()
