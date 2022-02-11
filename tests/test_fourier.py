"""Test fourier."""

import numpy as np

from ..ioSPI import fourier

n_pixels = (np.random.randint(low=8, high=128) // 2) * 2
arr2d = np.random.normal(size=n_pixels * n_pixels).reshape(n_pixels, n_pixels)
arr3d = np.random.normal(size=n_pixels * n_pixels * n_pixels).reshape(
    n_pixels, n_pixels, n_pixels
)


def test_do_fft():
    """Test fft wrapper.

    Conservation of variance due to gaussian white noise input.
    """
    for arr, dim in zip([arr2d, arr3d], [2, 3]):
        arr_f = fourier.do_fft(arr, dim=dim)
        assert arr_f.dtype == "complex128"
        assert arr_f.shape == tuple([n_pixels] * dim)
        assert np.isclose(
            np.var(arr), np.var(arr_f), atol=1e-2
        )  # change atol if N different

        assert np.allclose(
            fourier.do_fft(arr, dim=dim, only_real=True),
            fourier.do_fft(arr, dim=dim).real,
        )


def test_do_ifft():
    """Test ifft wrapper."""
    for arr, dim in zip([arr2d, arr3d], [2, 3]):
        arr_i = fourier.do_ifft(arr, dim=dim)
        assert arr_i.dtype == "float64"
        assert arr_i.shape == tuple([n_pixels] * dim)

        arr_i = fourier.do_ifft(arr, dim=dim, only_real=False)
        assert arr_i.dtype == "complex128"


def test_do_fft_and_ifft():
    """Recover the original array after fft and ifft."""
    arr2d_f = fourier.do_fft(arr2d, dim=2)
    arr2d_r = fourier.do_ifft(arr2d_f, dim=2)
    assert np.allclose(arr2d_r, arr2d)


def test_make_checkerboard_2d():
    """Test 2D checkerboard."""
    checkerboard_2d = fourier.make_checkerboard_2d_prejit(
        arr2d.reshape(1, n_pixels, n_pixels).shape
    )
    assert np.allclose(checkerboard_2d**2, np.ones((1, n_pixels, n_pixels)))
    assert np.isclose(0, checkerboard_2d.mean())
    idx_rand_1, idx_rand_2 = np.random.randint(low=0, high=n_pixels, size=2)
    expected_value = 1
    if (idx_rand_1 + idx_rand_2) % 2:
        expected_value *= -1
    assert np.isclose(checkerboard_2d[0, idx_rand_1, idx_rand_2], expected_value)


def test_make_checkerboard_3d():
    """Test 3D checkerboard."""
    checkerboard_3d = fourier.make_checkerboard_3d_prejit(arr3d.shape)
    assert np.allclose(checkerboard_3d**2, np.ones((n_pixels, n_pixels, n_pixels)))
    assert np.isclose(0, checkerboard_3d.mean())
    idx_rand_1, idx_rand_2, idx_rand_3 = np.random.randint(low=0, high=n_pixels, size=3)
    expected_value = 1
    if (idx_rand_1 + idx_rand_2 + idx_rand_3) % 2:
        expected_value *= -1
    assert np.isclose(
        checkerboard_3d[idx_rand_1, idx_rand_2, idx_rand_3], expected_value
    )


def test_fft3d():
    """Test 3d fft core function."""
    arr3d_f = fourier.fft3d(arr3d, mode="forward")
    assert arr3d_f.shape == (n_pixels, n_pixels, n_pixels)
    arr3d_r = fourier.fft3d(arr3d_f, mode="inverse")
    assert arr3d_r.shape == (n_pixels, n_pixels, n_pixels)


def test_fft2d():
    """Test 2d fft core function."""
    arr2d_f = fourier.fft2d(arr2d, mode="forward")
    assert arr2d_f.shape == (n_pixels, n_pixels)
    arr2d_r = fourier.fft2d(arr2d_f, mode="inverse")
    assert arr2d_r.shape == (n_pixels, n_pixels)

    n_particles = n_pixels // 2
    arr2d_batch = arr3d[:n_particles]
    arr2d_batch_f = fourier.fft2d(arr2d_batch, batch=True, mode="forward")
    arr2d_manual_batch_f = np.zeros(
        (n_particles, n_pixels, n_pixels), dtype=np.complex128
    )
    for particle in range(n_particles):
        arr2d_manual_batch_f[particle] = fourier.fft2d(
            arr2d_batch[particle], mode="forward"
        )
    assert np.allclose(arr2d_manual_batch_f, arr2d_batch_f)
