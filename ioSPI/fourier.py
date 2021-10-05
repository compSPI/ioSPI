"""Fourier."""

import numpy as np
import pyfftw.interfaces.numpy_fft
from numba import jit


@jit
def make_checkerboard_2d(arr2d_shape):
    """Apply checkerboard pattern for 2D FFT.

    Each pixel switches from positive to negative in checker board pattern.
    Equivalent to fft shifting
    https://dsp.stackexchange.com/questions/9039/centering-zero-frequency-for-discrete-fourier-transform

    Parameters
    ----------
    arr2d_shape : tuple (n_particle,N_fourier_pixels,N_fourier_pixels)
        Input shape tuple.

    Returns
    -------
    checkerboard_2d : numpy.ndarray, shape (n_particle,N_fft_pix,N_fft_pix)
        Checkerboard array.
    """
    n_particle, n_pixels_1, n_pixels_2 = arr2d_shape
    checkerboard_2d = np.ones(arr2d_shape)
    for particle in range(n_particle):
        for pix_1 in range(n_pixels_1):
            for pix_2 in range(n_pixels_2):
                if (pix_1 + pix_2) % 2:
                    checkerboard_2d[particle, pix_1, pix_2] *= -1.0
    return checkerboard_2d


@jit
def make_checkerboard_3d(arr3d_shape):
    """Apply checkerboard pattern for 3D FFT.

    Each pixel switches from positive to negative in checker board pattern.
    Equivalent to fft shifting
    https://dsp.stackexchange.com/questions/9039/centering-zero-frequency-for-discrete-fourier-transform

    Parameters
    ----------
    arr3d_shape : tuple (N_fft_pix,N_fft_pix,N_fft_pix)
        Input shape tuple.

    Returns
    -------
    checkerboard_3d : numpy.ndarray, shape (N_fft_pix,N_fft_pix,N_fft_pix)
        Checkerboard array.
    """
    num_pix_1, num_pix_2, num_pix_3 = arr3d_shape
    checkerboard_3d = np.ones(arr3d_shape)
    for pix_1 in range(num_pix_1):
        for pix_2 in range(num_pix_2):
            for pix_3 in range(num_pix_3):
                if (pix_1 + pix_2 + pix_3) % 2:
                    checkerboard_3d[pix_1, pix_2, pix_3] *= -1
    return checkerboard_3d


def fft3d(
    arr3d,
    mode,
    checkerboard_3d=None,
    numpy_fft=pyfftw.interfaces.numpy_fft,
    only_real=False,
):
    """Compute 3D FFT.

    Fast fourier transform. We apply an alterating +1/-1 multiplicative
    before we go to/from Fourier space.
    Later we apply this again to the transform.
    The checkerboard pattern is applied instead of fft shifting
    to have the dc component in centre of image
    (even number of pixels, one to right of centre).

    Parameters
    ----------
    arr3d : numpy.ndarray, shape (n_pixels,n_pixels,n_pixels)
        Input array.
    mode : str, {"forward", "inverse"}
        Forward or inverse
    checkerboard_3d : numpy.ndarray, shape (n_pixels,n_pixels,n_pixels)
        Optional precomputed array. If None (default) passed,
        computes on the fly.
    numpy_fft : func
        Function backend for performing the fft.
    only_real : bool
        If True, return only real part of transform.

    Returns
    -------
    arr3d_f : numpy.ndarray, shape (n_pixels,n_pixels,n_pixels)
        Output array.
    """
    # compute on the fly if not precomputed
    if checkerboard_3d is None:
        checkerboard_3d = make_checkerboard_3d(arr3d.shape)
        # extra multiplication for mod 4
        if arr3d.shape[0] % 4 != 0:
            checkerboard_3d *= -1

    if mode == "forward":
        arr3d_f = numpy_fft.fftn(checkerboard_3d * arr3d)
        arr3d_f /= np.sqrt(np.prod(arr3d_f.shape))
    elif mode == "inverse":
        arr3d_f = numpy_fft.ifftn(checkerboard_3d * arr3d)
        arr3d_f *= np.sqrt(np.prod(arr3d_f.shape))

    if only_real:
        arr3d_f = arr3d_f.real

    arr3d_f *= checkerboard_3d
    return arr3d_f


def fft2d(
    arr2d,
    mode,
    numpy_fft=pyfftw.interfaces.numpy_fft,
    only_real=False,
    batch=False,
):
    """Compute 2D FFT.

    Fast fourier transform. We apply an alterating +1/-1 multiplicative
    before we go to/from Fourier space.
    Later we apply this again to the transform.
    The checkerboard pattern is applied instead of fft shifting
    to have the dc component in centre of image
    (even number of pixels, one to right of centre).

    Parameters
    ----------
    arr2d : numpy.ndarray, shape (n_pixels,n_pixels,n_pixels)
    or (num_exposures,n_pixels,n_pixels)
        Input array.
    mode : str, {"forward", "inverse"}
        Forward or inverse
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
    n1, n2 = arr2d.shape[-2:]

    # reshape to 3 dimensions
    arr2d = arr2d.reshape(-1, n1, n1)
    checkerboard_2d = make_checkerboard_2d(arr2d.shape)
    checkerboard_2d *= checkerboard_2d

    if mode == "forward":
        arr2d_f = numpy_fft.fftn(arr2d, axes=(-2, -1))
        arr2d_f /= n1
    elif mode == "inverse":
        arr2d_f = numpy_fft.ifftn(arr2d, axes=(-2, -1))
        arr2d_f *= n1

    if only_real:
        arr2d_f = arr2d_f.real

    arr2d_f *= checkerboard_2d
    if not batch:
        arr2d_f = arr2d_f.reshape(n1, n2)

    return arr2d_f


def do_fft(arr, dim=3, only_real=False, **kwargs):
    """Wrap forward FFT.

    Computes forward fast fourier transform for 2 or 3 dimensions.

    Parameters
    ----------
    arr : numpy.ndarray, shape
    (n_pixels,n_pixels) or (n_pixels,n_pixels,n_pixels)
        Input array.
    dim : int, 2 or 3
        Dimension.
    only_real : bool
        If True, return only real part of transform.

    Returns
    -------
    arr_f : numpy.ndarray, shape
    (n_pixels,n_pixels) or (n_pixels,n_pixels,n_pixels)

        Output array.
    """
    if dim == 2:
        arr_f = fft2d(arr, mode="forward", only_real=only_real, **kwargs)
    elif dim == 3:
        arr_f = fft3d(arr, mode="forward", only_real=only_real, **kwargs)
    return arr_f


def do_ifft(arr_f, dim=3, only_real=True, **kwargs):
    """Wrap inverse FFT.

    Computes inverse fast fourier transform for 2 or 3 dimensions.

    Parameters
    ----------
    arr_f : numpy.ndarray, shape
    (n_pixels,n_pixels) or (n_pixels,n_pixels,n_pixels)
        Input array.
    dim : int, 2 or 3
        Dimension.
    only_real : bool
        If True, return only real part of transform.

    Returns
    -------
    arr : numpy.ndarray, shape
    (n_pixels,n_pixels) or (n_pixels,n_pixels,n_pixels)
        Output array.
    """
    if dim == 2:
        arr = fft2d(arr_f, mode="inverse", only_real=only_real, **kwargs)
    elif dim == 3:
        arr = fft3d(arr_f, mode="inverse", only_real=only_real, **kwargs)
    return arr
