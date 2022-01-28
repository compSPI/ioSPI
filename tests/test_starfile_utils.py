"""Contain test functions for starfile_utils."""
import numpy as np
import pytest
import torch

from ioSPI.starfile_utils import (
    check_star_file,
    return_names,
    starfile_data,
    starfile_opticsparams,
)


def normalized_mse(a, b):
    """Return normalized error between two numpy arrays."""
    return np.sum((a - b) ** 2) ** 0.5 / np.sum(a ** 2) ** 0.5


def test_check_star_file():
    """Check if the starfile exists with the right format."""
    path = "non-existing-file.random_format"
    expected = "Input star file doesn't exist!"
    with pytest.raises(FileNotFoundError) as exception_context:
        check_star_file(path)
    actual = str(exception_context.value)
    assert expected in actual

    path = "ioSPI/starfile_utils.py"
    expected = "Input star file is not a valid star file!"

    with pytest.raises(FileExistsError) as exception_context:
        check_star_file(path)
    actual = str(exception_context.value)
    assert expected in actual


def test_starfile_opticsparams():
    """Check if the updated config attributes have the right instances."""

    class config:
        """Class to instantiate the config object."""

        input_starfile_path = "tests/data/test.star"

    config = starfile_opticsparams(config)
    int_type = np.int64
    float_type = np.float64
    assert isinstance(config.side_len, int_type)
    assert isinstance(config.kv, float_type)
    assert isinstance(config.amplitude_contrast, float_type)
    assert isinstance(config.pixel_size, float_type)
    assert isinstance(config.cs, float_type)


def test_return_names():
    """Check if the names retuned have the right instance."""

    class config:
        """Class to instantiate the config object."""

        shift = True
        ctf = True

    names = return_names(config)
    for name in names:
        assert isinstance(name, str) and name[:5] == "__rln"


def test_starfile_data():
    """Check if the datalist returned is equal to the input params."""

    class config:
        """Class to instantiate the config object."""

        batch_size = 12
        input_starfile_path = "tests/data/test.star"
        b_factor = 23

    iterations = 3
    config = starfile_opticsparams(config)
    rot_val = torch.randn(config.batch_size, 3)
    shift_val = torch.randn(config.batch_size, 2)
    ctf_val = torch.randn(config.batch_size, 3)
    rot_params = {
        "relion_angle_rot": rot_val[:, 0],
        "relion_angle_tilt": rot_val[:, 1],
        "relion_angle_psi": rot_val[:, 2],
    }

    shift_params = {"shift_x": shift_val[:, 0], "shift_y": shift_val[:, 1]}
    ctf_params = {
        "defocus_u": ctf_val[:, 0],
        "defocus_v": ctf_val[:, 1],
        "defocus_angle": ctf_val[:, 2],
    }
    datalist = []
    datalist = starfile_data(
        datalist, rot_params, ctf_params, shift_params, iterations, config
    )
    assert len(datalist) == config.batch_size
    for num, list_var in enumerate(datalist):

        assert isinstance(list_var[0], str)
        assert (
            normalized_mse(list_var[1], rot_params["relion_angle_rot"][num].numpy())
            < 0.01
        )
        assert (
            normalized_mse(list_var[2], rot_params["relion_angle_tilt"][num].numpy())
            < 0.01
        )
        assert (
            normalized_mse(list_var[3], rot_params["relion_angle_psi"][num].numpy())
            < 0.01
        )
        assert normalized_mse(list_var[4], shift_params["shift_x"][num].numpy()) < 0.01
        assert normalized_mse(list_var[5], shift_params["shift_y"][num].numpy()) < 0.01
        assert (
            normalized_mse(list_var[6], 1e4 * ctf_params["defocus_u"][num].numpy())
            < 0.01
        )
        assert (
            normalized_mse(list_var[7], 1e4 * ctf_params["defocus_v"][num].numpy())
            < 0.01
        )
        assert (
            normalized_mse(
                list_var[8], np.radians(ctf_params["defocus_angle"][num].numpy())
            )
            < 0.01
        )
        assert normalized_mse(list_var[9], config.kv) < 0.01
        assert normalized_mse(list_var[10], config.pixel_size) < 0.01
        assert normalized_mse(list_var[11], config.cs) < 0.01
        assert normalized_mse(list_var[12], config.amplitude_contrast) < 0.01
        assert normalized_mse(list_var[13], config.b_factor) < 0.01
