#!/usr/bin/env python3
"""
@Description :   狗跑步在线解码示例代码
@Author      :   冉星辰 (ran.xingchen@qq.com)
@Created     :   2023/06/09 09:46:35
"""
import os
import h5py
import numpy as np
import scipy.io as scio
import matplotlib.pyplot as plt

from time import time
from decoder.fitting import NeuralPreprocessOnline, MotionPreprocess, Decoder, greedy_search_channels       # noqa: E501


def __reading_mat_v7_3(data_path):
    data_dict = {}
    with h5py.File(data_path) as f:
        for k, v in f.items():
            data_dict[k] = np.asarray(v) if v.size > 1 else np.squeeze(v)
    return data_dict


def run_dog_walking(root_path, neural_file, motion_file, params, save_path):
    neural_path = os.path.join(root_path, neural_file)
    motion_path = os.path.join(root_path, motion_file)

    # Reading the raw neural data
    neural_dict = __reading_mat_v7_3(neural_path)
    neural_data: np.ndarray = neural_dict["neural"].T    # (C, T) -> (T, C)
    # neural_data = neural_data[:5000, :]
    neural_fs = neural_dict["neural_fs"]
    neural_ts: np.ndarray = np.squeeze(neural_dict["neural_ts"])
    # Reading the raw motion data
    motion_dict = __reading_mat_v7_3(motion_path)
    motion_data: np.ndarray = motion_dict["motion"].T    # (D, T) -> (T, D)
    # motion_data = motion_data[:5000, :]
    motion_fs = motion_dict["motion_fs"]
    motion_ts: np.ndarray = np.squeeze(motion_dict["motion_ts"])
    # motion_ts = motion_ts[:5000]

    # Initialize Neural Preprocessor
    nprocessor = NeuralPreprocessOnline(
        neural_fs, params["neural_nfreq"], params["neural_nQ"],
        params["neural_bfreq"], params["neural_filtorder"],
        params["neural_badchs"]
    )
    # Initialize Motion Preprocessor. Be aware, preprocessing of motion data
    # are different with neural, motion data only required during training
    # stage, so we can preprocess it in manner of offline.
    mprocessor = MotionPreprocess(
        params["motion_inptype"], params["motion_trgtype"], motion_fs,
        params["motion_inpfilt"], params["motion_inpfc"],
        params["motion_trgfilt"], params["motion_trgfc"],
        params["motion_filtorder"]
    )

    # Decoding preparation
    bin_size = params["decode_binsize"]
    neural_step = int(bin_size * neural_fs)
    # !Both neural step and motion step should be integer, otherwith the
    # !processing have problems.
    assert neural_step / bin_size == neural_fs
    # Computing number of bins.
    neural_len, neural_chs = neural_data.shape
    neural_duration = neural_len / neural_fs   # Duration of neural recordings.
    neural_bins = int(np.ceil(neural_duration / bin_size))
    neural_chid = np.arange(neural_chs)         # Neural channel id.
    neural_chs -= params["neural_badchs"].size  # Real number of channels.
    neural_chid = np.delete(neural_chid, params["neural_badchs"])
    motion_len, motion_nmd = motion_data.shape
    motion_duration = motion_len / motion_fs   # Duration of motion recordings.
    motion_bins = int(np.ceil(motion_duration / bin_size))
    motion_nmd = len(params["motion_trgtype"].split("-"))  # Real number.
    # !Number of neural bins should be the same with number of motion bins.
    assert neural_bins == motion_bins
    # Preallocate the training dataset. Validation dataset are included in it.
    nbins = neural_bins
    # nbins = 500
    train_val_size = int(params["decode_train_size"] / bin_size)
    # For neural data
    neural_nfeats = len(params["neural_fbands"]) + params["neural_lmp"]
    neural_nfeats *= neural_chs
    train_val_neural = np.zeros((train_val_size, neural_nfeats))
    # For motion data, we collecting entire streamed dataflow to perform
    # offline preprocessing.
    motion_data_buffer = []
    motion_time_buffer = []
    # Initialize decoder.
    decoder = Decoder(params["decode_ncomponents"])

    # Simulating online situation here.
    pred = []
    t1 = time()
    neural_bin_start = int(neural_ts[0] / bin_size) * bin_size
    motion_bin_start = int(motion_ts[0] / bin_size) * bin_size
    for i in range(nbins):
        # For online situation, collect one bin data first.
        neural_indices = (neural_ts >= neural_bin_start) & \
                         (neural_ts < neural_bin_start + bin_size)
        motion_indices = (motion_ts >= motion_bin_start) & \
                         (motion_ts < motion_bin_start + bin_size)
        bin_neural = neural_data[neural_indices]
        bin_motion = motion_data[motion_indices]
        # Preprocessing the neural data in a online way.
        x = nprocessor.preprocessing(
            bin_neural, params["neural_nw"], params["neural_fbands"],
            car=params["neural_car"], lmp=params["neural_lmp"]
        )
        if i < train_val_size:
            # Collect training data.
            train_val_neural[i] = x.ravel(order="F")
            motion_data_buffer.append(bin_motion)
            motion_time_buffer.append(motion_ts[motion_indices])
        elif i == train_val_size:
            # End of training data collection.
            print(f"Training data collection cost time: {time() - t1}")
            motion_data_buffer = np.concatenate(motion_data_buffer, axis=0)
            motion_time_buffer = np.concatenate(motion_time_buffer, axis=0)
            train_val_motion = mprocessor.bin_data(
                motion_data_buffer, motion_time_buffer, bin_size,
                params["motion_axis"]
            )
            # Do K-fold cross validation
            val_size = train_val_size // params["decode_kfold"]
            all_good_chs = np.array([], dtype=np.int32)    # Save good channels
            all_best_ccs = np.zeros((params["decode_kfold"],))   # Save best cc
            for k in range(params["decode_kfold"]):
                print(f"\nRunning fold {k + 1}...")
                # Indices of current fold's test data.
                ibeg_val = k * val_size
                iend_val = ibeg_val + val_size
                # Train data
                train_neural = np.concatenate((train_val_neural[:ibeg_val],
                                               train_val_neural[iend_val:]))
                train_motion = np.concatenate((train_val_motion[:ibeg_val],
                                               train_val_motion[iend_val:]))
                # Validation data
                val_neural = train_val_neural[ibeg_val:iend_val]
                val_motion = train_val_motion[ibeg_val:iend_val]
                # Searching the best channels in this fold.
                good_chs, best_cc = greedy_search_channels(
                    train_neural, train_motion, val_neural, val_motion,
                    neural_chs, motion_nmd
                )
                all_good_chs = np.append(all_good_chs,
                                         np.array(good_chs, dtype=np.int32))
                all_best_ccs[k] = best_cc

                print(f"Found good channles: {neural_chid[good_chs]}")
                print(f"Average CC of this fold: {best_cc:.4f}")
            # End of good channels' searching.
            good_chs = np.unique(all_good_chs)
            # Training the decoder with whole training dataset.
            Z0 = np.concatenate((train_val_neural[:, good_chs],
                                 train_val_neural[:, good_chs + neural_chs]), axis=1)   # noqa: E501
            decoder.train(Z0, train_val_motion)
            # Start to do prediction
            t1 = time()     # Time recording
            Z1 = x[good_chs].ravel(order="F")
            pred.append(decoder.predict(Z1))
        else:
            Z1 = x[good_chs].ravel(order="F")
            pred.append(decoder.predict(Z1))
        # Move forward the bin start index.
        neural_bin_start += bin_size
        motion_bin_start += bin_size
    print(f"Prediction cost time: {time() - t1}")

    # Bin whole motion data to evaluate the prediction.
    pred = np.concatenate(pred, axis=0)
    binned_motion = mprocessor.bin_data(motion_data[-3600:, :], motion_ts[-3600:], bin_size,
                                        params["motion_axis"])
    test_motion = binned_motion[-800:]
    CC = np.zeros((motion_nmd,))
    trg_order = mprocessor.target_order
    for i in range(motion_nmd):
        r = np.corrcoef(pred[:, i], test_motion[:, i])
        CC[i] = r[0, 1]
    print(f"\nCorrelation coefficient of prediction {trg_order}: {CC}")
    # Saving the decoding results.
    scio.savemat(os.path.join(save_path, "DogWalkingPrediction.mat"),
                 {'prediction': pred, "actual": test_motion})
    # Plot prediction and actual data.
    t = np.arange(pred.shape[0]) * bin_size
    for i in range(motion_nmd):
        plt.subplot(motion_nmd, 1, i + 1)
        plt.plot(t, test_motion[:, i], t, pred[:, i])
        plt.legend(["Actual", "Prediction"])
        plt.xlabel("Time (s)")
        plt.ylabel(trg_order[i].upper())
        plt.title(f"Correlation coefficient={CC[i]:.3f}")
    plt.show()


if __name__ == "__main__":
    params = {}
    # ===1. Neural data parameter setting
    params["neural_nfreq"] = [50, 100, 200]     # Notch frequencies
    params["neural_nQ"] = [50, 35, 50]          # Notch Quality factor
    params["neural_bfreq"] = [0.3, 500]         # Bandbass frequency range
    params["neural_filtorder"] = 4              # Filter order.
    # Bad channels to be removing
    params["neural_badchs"] = [
        1,   2,   3,   4,   5,   6,   7,   8,   9,   10,  11,  12,  13,  14,
        16,  17,  18,  19,  20,  21,  22,  23,  24,  25,  26,  27,  28,  29,
        30,  32,  33,  34,  35,  36,  37,  38,  39,  40,  41,  42,  43,  44,
        46,  47,  48,  49,  50,  51,  52,  54,  55,  56,  57,  58,  60,  61,
        62,  64,  65,  66,  68,  73,  74,  76,  81,  82,  83,  84,  86,  87,
        88,  89,  90,  91,  94,  96,  97,  98,  99,  100, 101, 102, 103, 104,
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
    params["neural_badchs"] = np.array(params["neural_badchs"]) - 1  # 0-index
    params["neural_nw"] = 2.5   # Time half bandwidth parameter for pmtm
    # Target frequency bands of neural data
    params["neural_fbands"] = [[70, 200]]
    params["neural_car"] = True     # Do CAR or not
    # Computing LMP as one of neural feature or not
    params["neural_lmp"] = True

    # ===2. Motion data parameter setting
    params["motion_inptype"] = "acc"    # Either of "acc", "vel", "pos".
    # Any combination of "pos", "vel", or "acc".
    params["motion_trgtype"] = "pos-vel"
    # Input is IMU acceleration, bandpass raw motion data from 1-5Hz.
    params["motion_inpfilt"] = "bandpass"
    params["motion_inpfc"] = [1, 5]
    params["motion_trgfilt"] = "high"     # "low", "high", or "bandpass"
    params["motion_trgfc"] = 1     # Cutoff frequency of motion target.
    params["motion_filtorder"] = 4
    params["motion_axis"] = [0]           # Which axis of the IMU to be used.

    # ===3. Decoding parameter setting
    params["decode_ncomponents"] = 0    # 0 components means no PCA performed.
    params["decode_binsize"] = 0.1          # Seconds
    params["decode_train_size"] = 300       # Seconds
    params["decode_kfold"] = 5     # k-Fold cross validation

    # Let's go
    cur_path = os.path.split(os.path.abspath(__file__))[0]
    data_path = os.path.join(cur_path, "..", "data", "DogWalkingData")
    save_path = os.path.join(cur_path, "..", "out")
    neural_file = "Neural/AlignedTestNeural.mat"
    motion_file = "Motion/AlignedTestMotion.mat"
    run_dog_walking(data_path, neural_file, motion_file, params, save_path)
