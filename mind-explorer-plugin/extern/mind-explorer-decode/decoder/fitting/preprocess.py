#!/usr/bin/env python3
"""
@Description :   用于在线计算的神经/运动数据预处理
@Author      :   冉星辰 (ran.xingchen@qq.com)
@Created     :   2023/05/24 15:33:49
"""
from scipy import signal
from decoder.spectrogram import compute_amp_spectrum, pmtm
from decoder.signal import fdomain_integration
from spectrum import nextpow2
from numpy import ndarray

import numpy as np
import matplotlib.pyplot as plt


class NeuralPreprocessOnline:
    def __init__(self, fs, fnotch=[50], qnotch=[30], fband=[0.3, 500],
                 order=4, bad_chs=[]):
        """
        Preprocessing neural signale in online way.

        Parameters
        ----------
        fs : float
            Sampling rate of neural signal.
        fnotch : list
            Frequencies to be eliminated in notch filter.
        qnotch : list
            Quality factor of notch filter. Note the length of qnotch should
            be same with fnotch.
        fband : list
            Frequency ranges of bandpass filter the neural signal.
        order : int
            Filter order of the bandpass and lowpass filter (For LMP feature).
        bad_chs : list
            Bad channels to be removed before preprocessing.
        """
        self.fs = fs
        # Notch filter
        assert len(fnotch) == len(qnotch), \
            "The parameter length of notch filter should be same!"
        for i, (f, q) in enumerate(zip(fnotch, qnotch)):
            b0, a0 = signal.iirnotch(f, Q=q, fs=fs)
            b = b0 if i == 0 else np.convolve(b, b0)    # noqa: F821
            a = a0 if i == 0 else np.convolve(a, a0)    # noqa: F821
        self.ncoeff = (b, a)
        # Band pass filter
        self.bcoeff = signal.butter(order, fband, btype="bandpass", fs=fs)
        # Low pass filter, Used for <5Hz local motion potential.
        self.lcoeff = signal.butter(order, 5, btype="low", fs=fs)
        # The channels to be removing.
        self.bad_chs = bad_chs

    def preprocessing(self, raw_data, nw, flim, fres=1.0, car=True,
                      lmp=False) -> np.ndarray:
        # Removing the bad channels.
        neural = np.delete(raw_data, self.bad_chs, axis=-1)
        neural = np.asarray(neural, dtype=np.float64)
        nchs = neural.shape[1]
        nbands = len(flim)

        # Do common average reference if necessary.
        if car:
            neural -= np.mean(neural, axis=1, keepdims=True)
        # Notch filtering the raw neural data.
        b, a = self.ncoeff
        if not hasattr(self, "nzi"):
            zi = signal.lfilter_zi(b, a)
            self.nzi = zi[:, np.newaxis] * neural[0]
        data, self.nzi = signal.lfilter(b, a, neural, 0, zi=self.nzi)
        # Then do band pass filter.
        b, a = self.bcoeff
        if not hasattr(self, "bzi"):
            zi = signal.lfilter_zi(b, a)
            self.bzi = zi[:, np.newaxis] * data[0]
        data, self.bzi = signal.lfilter(b, a, data, 0, zi=self.bzi)

        # Power spectrogram estimation.
        nfft = 2 ** nextpow2(self.fs / fres)
        Pxx, f = pmtm(data, nw, nfft, self.fs)
        neural_feats = np.zeros((nchs, nbands), dtype=Pxx.dtype)
        for i, band in enumerate(flim):
            assert band[0] >= f[0] and band[1] < f[-1], \
                "Wrong parameter 'fmin' / 'fmax'!"
            indices = (f >= band[0]) & (f < band[1])
            neural_feats[:, i] = np.sum(Pxx[:, indices], axis=1)

        # Computing Local Motion Potential if necessary.
        if lmp:
            b, a = self.lcoeff
            if not hasattr(self, "lzi"):
                zi = signal.lfilter_zi(b, a)
                self.lzi = zi[:, np.newaxis] * neural[0]
            # Filter neural data to get LMP.
            lmp_dat, self.lzi = signal.lfilter(b, a, neural, 0, zi=self.lzi)
            lmp_dat = np.mean(lmp_dat, axis=0, keepdims=True)
            neural_feats = np.concatenate((lmp_dat.T, neural_feats), axis=-1)
        return neural_feats


class NeuralPreprocess:
    def __init__(self, fs: float, fnotch: list = [50], qnotch: list = [50],
                 fband: list = [0.3, 500], order: int = 2, bad_chs: list = []):
        """
        Preprocessing neural signale in offline way. Do not input stream data
        to this class.

        Parameters
        ----------
        fs : float
            Sampling rate of neural signal.
        fnotch : list
            Frequencies to be eliminated in notch filter.
        qnotch : list
            Quality factor of notch filter. Note the length of qnotch should
            be same with fnotch.
        fband : list
            Frequency ranges of bandpass filter the neural signal.
        order : int
            Filter order of the bandpass and lowpass filter (For LMP feature).
        bad_chs : list
            Bad channels to be removed before preprocessing.
        """
        self.fs = fs
        self.order = order
        # Notch filter
        assert len(fnotch) == len(qnotch), \
            "The parameter length of notch filter should be same!"
        for i, (f, q) in enumerate(zip(fnotch, qnotch)):
            b0, a0 = signal.iirnotch(f, Q=q, fs=fs)
            b = b0 if i == 0 else np.convolve(b, b0)    # noqa: F821
            a = a0 if i == 0 else np.convolve(a, a0)    # noqa: F821
        self.ncoeff = (b, a)
        # Band pass filter
        self.bcoeff = signal.butter(order, fband, btype="bandpass", fs=fs)
        # The channels to be removing.
        self.bad_chs = bad_chs

    def bin_data(self, raw_data, nw, flim, bin_size, fres=1.0, car=True,
                 lmp=False, fs_trg=None) -> np.ndarray:
        """
        Here the input raw_data should including multiple bins of samples.

        Parameters
        ----------
        fs_trg : float, optional
            Sampling rate of neural signals during preprocessing. Note that
            fs_trg < fs. If fs_trg=None, means no downsampling of neural
            signal.
        """
        # Removing the bad channels.
        neural = np.delete(raw_data, self.bad_chs, axis=-1)
        neural = np.asarray(neural, dtype=np.float64)
        nbands = len(flim)

        # Do common average reference if necessary.
        if car:
            neural -= np.mean(neural, axis=1, keepdims=True)
        # Notch filtering the raw neural data.
        b, a = self.ncoeff
        data = signal.filtfilt(b, a, neural, axis=0)
        # Then do band pass filter.
        b, a = self.bcoeff
        data = signal.filtfilt(b, a, data, axis=0)
        # Downsample the continuous neural signal
        fs = self.fs
        if fs_trg is not None:
            assert fs_trg < self.fs, "Sampling rate of preprocessing should " \
                                     "be smaller than raw data sampling rate."
            q = self.fs // fs_trg
            data = signal.decimate(data, q, axis=0)
            fs = fs_trg

        # Prepare to bin data
        L, C = data.shape
        duration = L / fs      # Total neural data recording time.
        nbins = int(np.ceil(duration / bin_size))   # Number of bins
        step = int(fs * bin_size)            # Number of samples in each bin.
        assert step * nbins == L, "STEP * NBINS != NEURAL_LEN"
        inp_data = np.reshape(data, (nbins, step, C))
        binned_data = np.zeros((nbins, C * nbands), dtype=data.dtype)
        # Power spectrogram estimation.
        nfft = 2 ** nextpow2(fs / fres)
        for i in range(nbins):
            Pxx, f = pmtm(inp_data[i], nw, nfft, fs)
            for j, band in enumerate(flim):
                assert band[0] >= f[0] and band[1] < f[-1], \
                    "Wrong parameter 'fmin' / 'fmax'!"
                indices = (f >= band[0]) & (f < band[1])
                P = np.sum(Pxx[:, indices], axis=1)
                binned_data[i, j * C:(j + 1) * C] = P
        # Computing Local Motion Potential if necessary.
        if lmp:
            # Low pass filter, Used for <5Hz local motion potential. Filter
            # coefficients computing here because 'fs' may changed here.
            b, a = signal.butter(self.order, 5, btype="low", fs=fs)
            # Filter neural data to get LMP.
            lmp_dat = signal.filtfilt(b, a, neural, axis=0)
            lmp_dat = np.reshape(lmp_dat, (nbins, step, C))
            lmp_dat = np.mean(lmp_dat, axis=1)
            binned_data = np.concatenate((lmp_dat, binned_data), axis=-1)
        return binned_data


class MotionPreprocess:
    def __init__(self, inp_type, trg_type, fs, inp_filter=None, inp_fc=None,
                 trg_filter=None, trg_fc=None, order=4):
        """
        Be careful! Do not support stream data (Online preprocessing way).

        Parameters
        ----------
        inp_type : str
            The input motion data type. Either of "pos", "vel", or "acc".
        trg_type : str
            The target motion data type. Any combination of "pos", "vel" or
            "acc" is accepted.
        fs : float
            Samping frequency of motion data.
        inp_filter : str, optional
            The type of filter applied to raw motion data. Can be either of
            "low", "high", "bandpass" or None. Default: None.
        inp_fc : scalar or list
            The cutoff frequency of inp_filter. If the inp_filter is "low" or
            "high", the inp_fc should be a scalar. If the inp_filter is
            "bandpass", the inp_fc should be a list. Default: None.
        trg_filter : str, optional
            The type of filter applied to the target motion data. Can be either
            of "low", "high", "bandpass" or None. Default: None.
        trg_fc : scalar or list
            The cutoff frequency of trg_filter. If the trg_filter is "low" or
            "high", the trg_fc should be a scalar. If the trg_filter is
            "bandpass", the trg_fc should be a list. Default: None.
        order : int
            The order of the preprocessing filters.

        Note
        ----
        Input filter take effect only when inp_filter and inp_fc are both not
        None. Same with target filter.
        """
        self.inp_type = inp_type.lower()
        self.trg_type = trg_type.lower()
        self.fs = fs
        self.trg_order = []

        if inp_filter is not None and inp_fc is not None:
            self.inp_fcoeff = signal.butter(order, inp_fc, inp_filter, fs=fs)
        if trg_filter is not None and trg_fc is not None:
            self.trg_fcoeff = signal.butter(order, trg_fc, trg_filter, fs=fs)

    @property
    def target_order(self):
        return self.trg_order

    def bin_data(self, raw_data: ndarray, timestamp: ndarray, bin_size: float,
                 dim=None):
        """
        Processing the specified raw motion data to target data type then bin
        the preprocessed data.
        """
        assert raw_data.shape[0] == timestamp.shape[0], \
            "Mismatch of input data and timestamp."
        # Clear taregt order.
        self.trg_order = []

        # Only need the specified dimensions.
        data = raw_data[:, dim] if dim is not None else raw_data.copy()
        # Filter raw data first if necessary.
        if hasattr(self, "inp_fcoeff"):
            b, a = self.inp_fcoeff
            data = signal.filtfilt(b, a, data, axis=0)
        # Then get the target motion data.
        data, timestamp = self.compute_target_motion(data, timestamp)
        # Bin data
        _, D = data.shape     # (length, ndim)
        duration = timestamp[-1] - timestamp[0]   # Motion data recording time.
        nbins = int(np.ceil(duration / bin_size))   # Number of bins
        # Get a real start of the first bin.
        bin_start = timestamp[0] // bin_size * bin_size
        binned_data = np.zeros((nbins, D), data.dtype)   # Preallocate output.
        for i in range(nbins):
            indices = (timestamp >= bin_start) & \
                      (timestamp < bin_start + bin_size)
            indices = np.squeeze(indices)
            binned_data[i] = np.mean(data[indices], axis=0)
            # Update start time of next bin.
            bin_start += bin_size
        return binned_data

    def compute_target_motion(self, data: ndarray, time: ndarray):
        """
        Computing target motion from the raw data.

        Parameters
        ----------
        data : ndarray
            The input raw motion data, shape: [T, M], where T means number of
            samples, and M means number of movement degree.
        time : ndarray
            The timestamp of raw motion data, with shape of [T,]
        """
        assert data.shape[0] == time.shape[0], \
            "The input data and time have different number of samples."

        if self.inp_type == self.trg_type:
            return data

        # When input data type are different from target data type.
        if self.inp_type == "pos":      # When input is position.
            trg, time = self._pos_process(data, time)
        elif self.inp_type == "vel":
            # TODO: implement this
            ...
        elif self.inp_type == "acc":
            trg = self._acc_process(data, time)
        else:
            raise RuntimeError(f"Unknown data type: '{self.inp_type}'")
        return trg, time

    def _pos_process(self, pos: ndarray, timestamp: ndarray):
        """Processing when input data are position."""
        dt = timestamp[1:] - timestamp[:-1]       # Interval of sample time.
        vel = (pos[1:] - pos[:-1]) / dt

        trg = []
        if "acc" in self.trg_type:  # Computing and append acceleration.
            acc = (vel[1:] - vel[:-1]) / dt[:-1]
            trg.append(acc)
            self.trg_order.append("acc")
        if "vel" in self.trg_type:
            trg.append(vel)
            self.trg_order.append("vel")
        if "pos" in self.trg_type:
            trg.append(pos)
            self.trg_order.append("pos")

        # Make sure each type of target are the same length.
        maxlen = min(map(len, trg))
        trg_new = [t[:maxlen] for t in trg]
        timestamp = timestamp[:maxlen]
        return np.concatenate(trg_new, axis=-1), timestamp

    def _acc_process(self, acc: ndarray, timestamp: ndarray):
        """Processing when input data are acceleration."""
        dt = timestamp[1:] - timestamp[:-1]       # Interval of sample time.
        dt = np.mean(dt)    # Average sampling time for whole dataset.

        # No matter of what, computing velocity first.
        ndm = acc.shape[1]        # Number of dimensions of the motion
        vel = np.zeros_like(acc)
        for i in range(ndm):
            vel[:, i] = fdomain_integration(acc[:, i], dt)
        # Filter the velocity to remove drift.
        if hasattr(self, "trg_fcoeff"):
            b, a = self.trg_fcoeff
            vel = signal.filtfilt(b, a, vel, axis=0)

        trg = []
        if "acc" in self.trg_type:
            trg.append(acc)
            self.trg_order.append("acc")
        if "vel" in self.trg_type:
            trg.append(vel)
            self.trg_order.append("vel")
        if "pos" in self.trg_type:
            pos = np.zeros_like(acc)
            for i in range(ndm):
                pos[:, i] = fdomain_integration(vel[:, i], dt)
            # Filter the integration results to remove drift
            if hasattr(self, "trg_fcoeff"):
                pos = signal.filtfilt(b, a, pos, axis=0)
            trg.append(pos)
            self.trg_order.append("pos")
        return np.concatenate(trg, axis=-1)


if __name__ == "__main__":
    a0 = 2
    a1 = 6.9
    a2 = 4.8
    a3 = 3.3
    a4 = 1.7
    f1 = 50
    f2 = 100
    f3 = 150
    f4 = 200
    fs = 4000

    T = np.linspace(0.0, 10.0, fs * 10)
    S = a0 + \
        a1 * np.cos(2 * np.pi * f1 * T) + \
        a2 * np.cos(2 * np.pi * f2 * T) + \
        a3 * np.cos(2 * np.pi * f3 * T) + \
        a4 * np.cos(2 * np.pi * f4 * T)
    S = S[:, np.newaxis]

    processor = NeuralPreprocessOnline(fs)

    bin_size = 0.1
    step = int(fs * bin_size)
    P = np.zeros((fs * 10 // step, 1))
    j = 0
    for i in range(0, fs * 10, step):
        P[j] = processor.preprocessing(S[i:i + step], nw=2.5, flim=[[70, 200]],
                                       car=False)
        j += 1

    f1, y1 = compute_amp_spectrum(S, fs)

    plt.subplot(3, 1, 1)
    plt.plot(T, S)
    plt.subplot(3, 1, 2)
    plt.plot(f1, y1)
    plt.subplot(3, 1, 3)
    plt.imshow(P.T)
    plt.clim(0, np.max(P))
    plt.show()
