#!/usr/bin/env python3
"""
@Description :   用于BCI解码的Kalman滤波算法
@Author      :   冉星辰 (ran.xingchen@qq.com)
@Created     :   2023/05/26 09:37:02
"""
import numpy as np
import pickle

from numpy import ndarray


class KalmanFilter():
    """
    Kalman filter for brain computer interface (BCI) decoding.

    This Kalman filter is designed for BCI decoding. You can
    use it to predict the target's future location by decoding
    the corresponding neural signal. In this framework, the
    target data (like position, velocity or acceleration, etc.)
    is modeled as the system state and the neural signal is
    modeled as the observation (measurement). Note that to use
    this Kalman filter, it assumes the observation is a linear
    function of the state plus Gaussian noise, and the target
    data at time t is assumed to be a linear function of the
    target data at the previous time instant plus Gaussian noise.

    The Kalman filter algorithm implements a discrete time,
    linear State-Space System described as follows.

        x(t) = A * x(t-1) + r(t-1)           (state equation)
        z(t) = H * x(t) + q(t)               (measurement equation)

    The Kalman filter algorithm involves two steps.
        - Predict: Using the previous states to predict the
                   current state.
        - Update:  Using the current measurement, such as the
                   recorded neural signal, to correct the state.

    Parameters
    ----------
    fast_compute : bool, optional
        If fast compute is True, use the numpy.linalg.lstsq function to
        compute the matrix needed. Otherwise, manually computing the function
        by inverse.
    eps : float, optional
        In case of during the computation, X'X is not full rank,
        the eps is added on the diagnol of the covariance matrix
        to make sure it always have inverse matrix.

    Examples
    --------

    References
    ----------
    [1] Wu, W., et al. (2002). Inferring hand motion from multi-cell
        recordings in motor cortex using a Kalman filter.
        SAB'02-workshop on motor control in humans and robots: On the
        interplay of real brains and artificial devices.
    """
    def __init__(self, fast_compute=True, eps=1e-8):
        self.fast_compute = fast_compute
        self.eps = eps

    def train(self, Z: ndarray, X: ndarray):
        """
        Parameters
        ----------
        Z : ndarray, shape (T, N)
            The measurement matrix which is used to calculate the
            models, where N means the feature dimensions of the
            measurement. In BCI application, it should be the X's
            corresponding neural data.
        X : ndarray, shape (T, M)
            The state matrix which is used to calculate the models,
            where T means the time steps and M means the feature
            dimensions. In the BCI application, it can be the
            movement or other behavior data.

        Attributes
        ----------
        A : ndarray, shape (M, M)
            Model describing state transition between time steps.
            Specify the transition of state between times as an M-by-M
            matrix. This attribute cannot be changed once the Kalman
            filter is trained.
        H : ndarray, shape (N, M)
            Model describing state to measurement transformation.
            Specify the transition from state to measurement as an N-by-M
            matrix. This attribute cannot be changed once the Kalman
            filter is trained.
        P : ndarray, shape (M, M)
            State estimation error covariance. Specify the covariance
            of the state estimation error as an M-by-M diagonal matrix.
        Q : ndarray, shape (M, M)
            Process noise covariance. Specify the covariance of process
            noise as an M-by-M matrix.
        R : ndarray, shape (N, N)
            Measurement noise covariance. Specify the covariance of
            measurement noise as an N-by-N matrix.
        """
        T, M = X.shape

        assert T == Z.shape[0], \
            'The state and measurement should have same number of time points!'

        if not self.fast_compute:
            eye = np.eye(M, dtype=X.dtype)
            eps = eye * self.eps

        X1, X2 = X[:-1], X[1:]

        if self.fast_compute:
            # State Transition Model
            self.A = np.linalg.lstsq(X1, X2, rcond=None)[0].T
            # Measurement Model
            self.H = np.linalg.lstsq(X, Z, rcond=None)[0].T
        else:
            # State Transition Model
            self.A = np.matmul(np.matmul(X2.T, X1),
                               np.linalg.pinv(np.matmul(X1.T, X1) + eps))
            # Measurement Model
            self.H = np.matmul(np.matmul(Z.T, X),
                               np.linalg.pinv(np.matmul(X.T, X) + eps))
        # Process Noise
        e_sta = X2.T - np.matmul(self.A, X1.T)
        self.W = np.matmul(e_sta, e_sta.T) / (T - 1)
        # Measurement Noise
        e_mea = Z.T - np.matmul(self.H, X.T)
        self.Q = np.matmul(e_mea, e_mea.T) / T
        # State Covariance
        self.P = np.matmul(X.T, X) / T

    def predict(self, Z: ndarray, x0: ndarray):
        """
        Predicts the measurement, state, and state estimation error covariance.
        The internal state and covariance of Kalman filter are overwritten
        by the prediction results.

        Parameters
        ----------
        Z : ndarray, shape (1, N) or (N,) or (T, N)
            The measurement matrix which is used to predict the
            corresponding state, where N means the feature dimensions
            of the measurement. The time step of Z can be 1 or T, if T,
            the predicted state also have T time step.
        x0 : ndarray, shape (1, M) or (M,)
            The initial state vector used to predict the next time step.

        Returns
        -------
        X : ndarray or tensor, shape (1, M) or (T, M)
            The prediction by the observation model and measurement model.
            It have same length with Z.
        """
        # Make sure Z and x0 have 2 dimensions
        if Z.ndim == 1:
            Z = Z[np.newaxis, :]
        if x0.ndim == 1:
            x0 = x0[np.newaxis, :]

        xt = x0.copy()  # x0 is the initialize state.
        Pt = self.P     # Initialize state estimation error covariance.
        X = []
        for zt in Z:
            zt = np.reshape(zt, (1, -1))
            # Priori estimate of xt and Pt
            xt = np.matmul(self.A, xt.T).T
            Pt = np.matmul(np.matmul(self.A, Pt), self.A.T) + self.W
            # Calculate Kalman gain of current step
            residual = np.matmul(np.matmul(self.H, Pt), self.H.T) + self.Q
            if self.fast_compute:
                Kt = np.linalg.lstsq(residual.T, np.matmul(self.H, Pt.T),
                                     rcond=None)[0].T
            else:
                Kt = np.matmul(np.matmul(Pt, self.H.T),
                               np.linalg.pinv(residual))
            # Update the estimation by measurement.
            # * Do not use inplace operation.
            xt = xt + np.matmul(Kt, zt.T - np.matmul(self.H, xt.T)).T
            Pt = Pt - np.matmul(np.matmul(Kt, self.H), Pt)

            # Push current time step predcting result to X
            X.append(xt)

        X = np.concatenate(X, axis=0)
        # Update the state estimation error covariance.
        self.P = Pt
        return X

    def save(self, path):
        """
        Save the Kalman filter parameters to the specified path.
        The saving parameters including: A, H, P, Q, W

        Parameters
        ----------
        path : str
            The path of the parameters will be saved.
        """
        with open(path, 'wb') as f:
            pickle.dump(self.A, f)
            pickle.dump(self.H, f)
            pickle.dump(self.P, f)
            pickle.dump(self.Q, f)
            pickle.dump(self.W, f)

    def load(self, path):
        """
        Load the Kalman filter parameters to the specified path.
        The loading parameters including: A, H, P, Q, W

        Parameters
        ----------
        path : str
            The path of the parameters will be loaded.
        """
        with open(path, 'rb') as f:
            self.A = pickle.load(f)
            self.H = pickle.load(f)
            self.P = pickle.load(f)
            self.Q = pickle.load(f)
            self.W = pickle.load(f)
