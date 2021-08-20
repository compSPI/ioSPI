import numpy as np
import pyfftw.interfaces.numpy_fft
from numba import jit


@jit
def make_neg_pos_2d(arr2d_shape):
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
    neg_pos_2d : numpy.ndarray, shape (n_particle,N_fourier_pixels,N_fourier_pixels)
        Checkerboard array.
    """
    # assert arr2d.ndim == 3  # extra axis
    n_particle, R1, R2 = arr2d_shape
    neg_pos_2d = np.ones(arr2d_shape)
    for particle in range(n_particle):
        for r1 in range(R1):
            for r2 in range(R2):
                if (r1 + r2) % 2:
                    neg_pos_2d[particle, r1, r2] *= -1
    return neg_pos_2d


@jit
def make_neg_pos_3d(arr3d_shape):
    """Apply checkerboard pattern for 3D FFT.

    Each pixel switches from positive to negative in checker board pattern.
    Equivalent to fft shifting
    https://dsp.stackexchange.com/questions/9039/centering-zero-frequency-for-discrete-fourier-transform

    Parameters
    ----------
    arr3d_shape : tuple (N_fourier_pixels,N_fourier_pixels,N_fourier_pixels)
        Input shape tuple.

    Returns
    -------
    neg_pos_3d : numpy.ndarray, shape (N,N,N)
        Checkerboard array.
    """
    R1, R2, R3 = arr3d_shape
    neg_pos_3d = np.ones(arr3d_shape)
    for r1 in range(R1):
        for r2 in range(R2):
            for r3 in range(R3):
                if (r1 + r2 + r3) % 2:
                    neg_pos_3d[r1, r2, r3] *= -1
    return neg_pos_3d


def fft3d(
    arr3d,
    mode,
    neg_pos_3d=None,
    numpy_fft=pyfftw.interfaces.numpy_fft,
    only_real=False,
):
    """3D FFT

    Wraps fft2d
    Fast fourier transform. We apply an alterating +1/-1 multiplicative
    before we go to/from Fourier space.
    Later we apply this again to the transform.
    The checkerboard pattern is applied instead of fft shifting
    to have the dc component in centre of image
    (even number of pixels, one to right of centre).

    Parameters
    ----------
    arr3d : numpy.ndarray, shape (N,N,N)
        Input array.
    mode : str
        Forward or reverse
    neg_pos_3d : numpy.ndarray, shape (N,N,N)
        Optional precomputed array. If None (default) passed,
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
    # compute on the fly if not precomputed
    if neg_pos_3d is None:
        neg_pos_3d = make_neg_pos_3d(arr3d)
        # extra multiplication for mod 4
        if arr3d.shape[0] % 4 != 0:
            neg_pos_3d *= -1

    if mode == "forward":
        arr3d_f = numpy_fft.fftn(neg_pos_3d * arr3d)
        arr3d_f /= np.sqrt(np.prod(arr3d_f.shape))
    elif mode == "inverse":
        arr3d_f = numpy_fft.ifftn(neg_pos_3d * arr3d)
        arr3d_f *= np.sqrt(np.prod(arr3d_f.shape))

    if only_real:
        arr3d_f = arr3d_f.real

    arr3d_f *= neg_pos_3d
    return arr3d_f


def fft2d(
    arr2d,
    mode,
    numpy_fft=pyfftw.interfaces.numpy_fft,
    only_real=False,
    batch=False,
):
    """2D FFT

    Fast fourier transform. We apply an alterating +1/-1 multiplicative
    before we go to/from Fourier space.
    Later we apply this again to the transform.
    The checkerboard pattern is applied instead of fft shifting
    to have the dc component in centre of image
    (even number of pixels, one to right of centre).

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
    # needs work: look into pyfftw.interfaces.numpy_fft.irfftn .
    # needs work: throw error instead of using assert
    # assert (arr2d.ndim == 2 and not batch) or (batch and arr2d.ndim == 3)
    n1, n2 = arr2d.shape[-2:]
    # assert n1 == n2
    # we apply an alterating +1/-1 multiplicative
    # before we go to/from Fourier space.
    # Later we apply this again to the transform.
    # checkerboard pattern applied instead of fft shifting
    # to have dc component in centre of image
    # (even number of pixels, one to right of centre)

    # reshape to 3 dimensions
    arr2d = arr2d.reshape(-1, n1, n1)
    neg_pos_2d = make_neg_pos_2d(arr2d.shape)
    neg_pos_2d *= neg_pos_2d

    if mode == "forward":
        arr2d_f = numpy_fft.fftn(arr2d, axes=(-2, -1))
        arr2d_f /= n1
    elif mode == "inverse":
        arr2d_f = numpy_fft.ifftn(arr2d, axes=(-2, -1))
        arr2d_f *= n1

    if only_real:
        arr2d_f = arr2d_f.real

    arr2d_f *= neg_pos_2d
    if not batch:
        arr2d_f = arr2d_f.reshape(n1, n2)

    return arr2d_f


def do_fft(arr, d=3, only_real=False, **kwargs):
    """Forward FFT wrapper.

    Computes forward fast fourier transform for 2 or 3 dimensions.

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
        arr_f = fft2d(arr, mode="forward", only_real=only_real, **kwargs)
    elif d == 3:
        arr_f = fft3d(arr, mode="forward", only_real=only_real, **kwargs)
    return arr_f


def do_ifft(arr_f, d=3, only_real=True, **kwargs):
    """Inverse FFT wrapper.

    Computes inverse fast fourier transform for 2 or 3 dimensions.

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
        arr = fft2d(arr_f, mode="inverse", only_real=only_real, **kwargs)
    elif d == 3:
        arr = fft3d(arr_f, mode="inverse", only_real=only_real, **kwargs)
    return arr
