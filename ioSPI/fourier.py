import numpy as np
import pyfftw.interfaces.numpy_fft
from numba import jit


@jit
def neg_pos_2d(arr2d):
    """Apply checkerboard pattern.

    Each pixel switches from positive to negative in
    checker board pattern.

    Parameters
    ----------
    arr2d : numpy.ndarray, shape (N,N)
        Input array.

    Returns
    -------
    arr2d : numpy.ndarray, shape (N,N)
        Output array.
    """
    assert arr2d.ndim == 3  # extra axis
    for n_particle in range(arr2d.shape[0]):
        for r in range(arr2d.shape[1]):
            for c in range(arr2d.shape[2]):
                if (r + c) % 2:
                    arr2d[n_particle, r, c] *= -1
    return arr2d


@jit
def make_neg_pos_3d(arr3d):
    """Apply checkerboard pattern.

    Each pixel switches from positive to negative in
    checker board pattern.

    Parameters
    ----------
    arr3d : numpy.ndarray, shape (N,N,N)
        Input array.

    Returns
    -------
    neg_pos_3d : numpy.ndarray, shape (N,N,N)
        Output array.
    """
    R1, R2, R3 = arr3d.shape
    neg_pos_3d = np.ones(arr3d.shape)
    for r1 in range(R1):
        for r2 in range(R2):
            for r3 in range(R3):
                if (r1 + r2 + r3) % 2:
                    neg_pos_3d[r1, r2, r3] *= -1.0
    return neg_pos_3d


def fft3d(
    arr3d,
    mode,
    neg_pos_3d=None,
    numpy_fft=pyfftw.interfaces.numpy_fft,
    only_real=False
):
    """3D FFT

    Fast fourier transform

    Parameters
    ----------
    arr3d : numpy.ndarray, shape (N,N,N)
        Input array.
    mode : str
        Forward or reverse
    neg_pos_3d : numpy.ndarray, shape (N,N,N)
        Optinal precomputed array. If None (default) passed,
        computes on the fly.
    numpy_fft : func
        Function backend for performing the fft.
    only_real : bool
        If True, return only real part of transform.

    Returns
    -------
    arr3d_f : numpy.ndarray, shape (N,N,N)
        Output array.
    """
    if neg_pos_3d is None:
        neg_pos_3d = make_neg_pos_3d(arr3d)
    if arr3d.shape[0] % 4 != 0:
        neg_pos_3d *= -1

    if mode == "f":
        arr3d_f = numpy_fft.fftn(neg_pos_3d * arr3d)
        arr3d_f /= np.sqrt(np.prod(arr3d_f.shape))
    elif mode == "i":
        arr3d_f = numpy_fft.ifftn(neg_pos_3d * arr3d)
        arr3d_f *= np.sqrt(np.prod(arr3d_f.shape))

    if only_real:
        arr3d_f = arr3d_f.real

    arr3d_f *= neg_pos_3d
    return arr3d_f


def do_fft(arr, d=3, only_real=False, **kwargs):
    """FFT wrapper.

    Wraps fft2d

    Parameters
    ----------
    arr : numpy.ndarray, shape (N,N) or (N,N,N)
        Input array.
    d : int, 2 or 3
        Dimension.
    only_real : bool
        If True, return only real part of transform.

    Returns
    -------
    arr_f : numpy.ndarray, shape (N,N) or (N,N,N)
        Output array.
    """
    if d == 2:
        arr_f = fft2d(arr, mode="f", only_real=only_real, **kwargs)
    elif d == 3:
        arr_f = fft3d(arr, mode="f", only_real=only_real, **kwargs)
    return arr_f


def do_ifft(arr_f, d=3, only_real=True, **kwargs):
    """iFFT wrapper.

    Wraps fft2d

    Parameters
    ----------
    arr_f : numpy.ndarray, shape (N,N) or (N,N,N)
        Input array.
    d : int, 2 or 3
        Dimension.
    only_real : bool
        If True, return only real part of transform.

    Returns
    -------
    arr : numpy.ndarray, shape (N,N) or (N,N,N)
        Output array.
    """
    if d == 2:
        arr = fft2d(arr_f, mode="i", only_real=only_real, **kwargs)
    elif d == 3:
        arr = fft3d(arr_f, mode="i", only_real=only_real, **kwargs)
    return arr


def fft2d(
    arr2d,
    mode,
    numpy_fft=pyfftw.interfaces.numpy_fft,
    only_real=False,
    batch=False
):
    """2D FFT

    Fast fourier transform
    TODO: look into pyfftw.interfaces.numpy_fft.irfftn .

    Parameters
    ----------
    arr2d : numpy.ndarray, shape (N,N) or (num_exposures,N,N)
        Input array.
    mode : str
        Forward or reverse
    numpy_fft : func
        Function backend for performing the fft.
    only_real : bool
        If True, return only real part of transform.
    batch : bool
        Use for batch of exposures.

    Returns
    -------
    arr2d_f : numpy.ndarray, shape (N,N) or (num_exposures,N,N)
        Output array.
    """
    assert (arr2d.ndim == 2 and not batch) or (batch and arr2d.ndim == 3)
    n1, n2 = arr2d.shape[-2:]
    assert n1 == n2
    # we apply an alterating +1/-1 multiplicative
    # before we go to/from Fourier space.
    # Later we apply this again to the transform.
    arr2d = neg_pos_2d(arr2d.reshape(-1, n1, n1).copy())

    if mode == "f":
        arr2d_f = numpy_fft.fftn(arr2d, axes=(-2, -1))
        arr2d_f /= n1
    elif mode == "i":
        arr2d_f = numpy_fft.ifftn(arr2d, axes=(-2, -1))
        arr2d_f *= n1

    if only_real:
        arr2d_f = arr2d_f.real

    arr2d_f = neg_pos_2d(arr2d_f.copy())
    if not batch:
        arr2d_f = arr2d_f.reshape(n1, n2)

    return arr2d_f
