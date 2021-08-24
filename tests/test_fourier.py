import numpy as np
from ioSPI import fourier


# right way to use as global in testing environment?
N = 128
arr2d = np.random.normal(size=N * N).reshape(N, N)
arr3d = np.random.normal(size=N * N * N).reshape(N, N, N)


def test_do_fft():
    """Test fft wrapper.

    Conservation of variance due to gaussian white noise input.
    """
    for arr, d in zip([arr2d, arr3d], [2, 3]):
        arr_f = fourier.do_fft(arr, d=d)
        assert arr_f.dtype == "complex128"
        assert arr_f.shape == tuple([N] * d)
        assert np.isclose(
            np.var(arr), np.var(arr_f), atol=1e-3
        )  # change atol if N different

        assert np.allclose(
            fourier.do_fft(arr, d=d, only_real=True),
            fourier.do_fft(arr, d=d).real,
        )


def test_do_ifft():
    """Test ifft wrapper."""
    for arr, d in zip([arr2d, arr3d], [2, 3]):
        arr_i = fourier.do_ifft(arr, d=d)
        assert arr_i.dtype == "float64"
        assert arr_i.shape == tuple([N] * d)

        # needs work: normalization constant
        # assert np.isclose(np.var(arr_i),np.var(arr),atol=1e-3)

        arr_i = fourier.do_ifft(arr, d=d, only_real=False)
        assert arr_i.dtype == "complex128"


def test_do_fft_and_ifft():
    """Recover the original array after fft and ifft."""
    arr2d_f = fourier.do_fft(arr2d, d=2)
    arr2d_r = fourier.do_ifft(arr2d_f, d=2)
    assert np.allclose(arr2d_r, arr2d)


def test_make_neg_pos_2d():
    """Test 2D checkerboard."""
    neg_pos_3d = fourier.make_neg_pos_2d(arr3d.shape)
    assert np.allclose(neg_pos_3d ** 2, np.ones((N, N, N)))
    assert np.isclose(0, neg_pos_3d.mean())


def test_make_neg_pos_3d():
    """Test 3D checkerboard."""
    neg_pos_3d = fourier.make_neg_pos_3d(arr3d.shape)
    assert np.allclose(neg_pos_3d ** 2, np.ones((N, N, N)))
    assert np.isclose(0, neg_pos_3d.mean())


def test_fft3d():
    """Test 3d fft core function."""
    arr3d_f = fourier.fft3d(arr3d, mode="forward")
    assert arr3d_f.shape == (N, N, N)
    arr3d_r = fourier.fft3d(arr3d_f, mode="inverse")
    assert arr3d_r.shape == (N, N, N)


def test_fft2d():
    """Test 2d fft core function."""
    arr2d_f = fourier.fft2d(arr2d, mode="forward")
    assert arr2d_f.shape == (N, N)
    arr2d_r = fourier.fft2d(arr2d_f, mode="inverse")
    assert arr2d_r.shape == (N, N)

    arr2d_batch = arr3d[: N // 2]
    arr2d_batch_f = fourier.fft2d(arr2d_batch, batch=True, mode="forward")
    arr2d_manual_batch_f = np.zeros((N // 2, N, N), dtype=np.complex128)
    for n in range(N // 2):
        arr2d_manual_batch_f[n] = fourier.fft2d(arr2d_batch[n], mode="forward")
    assert np.allclose(arr2d_manual_batch_f, arr2d_batch_f)
