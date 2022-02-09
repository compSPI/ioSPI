"""Contain test functions for metadata.py."""

import os

import numpy as np
import pytest

from ioSPI.metadata import (
    check_star_file,
    get_starfile_metadata_names,
    update_optics_config_from_starfile,
    write_starfile,
    write_starfile_cryoem_convention,
)


def test_check_star_file():
    """Check if the starfile exists with the right format."""
    path = "non-existing-file.random_format"
    expected = "Input star file doesn't exist!"
    with pytest.raises(FileNotFoundError) as exception_context:
        check_star_file(path)
    actual = str(exception_context.value)
    assert expected in actual

    path = "ioSPI/metadata.py"
    expected = "Input star file is not a valid star file!"

    with pytest.raises(FileExistsError) as exception_context:
        check_star_file(path)
    actual = str(exception_context.value)
    assert expected in actual


def test_update_optics_config_from_starfile():
    """Check if the updated config attributes have the right instances."""

    class Config:
        """Class to instantiate the config object."""

        input_starfile_path = "tests/data/test.star"

    config = update_optics_config_from_starfile(Config)
    int_type = np.int64
    float_type = np.float64
    assert isinstance(config.side_len, int_type)
    assert isinstance(config.kv, float_type)
    assert isinstance(config.amplitude_contrast, float_type)
    assert isinstance(config.pixel_size, float_type)
    assert isinstance(config.cs, float_type)


def test_get_starfile_metadata_names():
    """Check if the names returned have the right instance."""

    class Config:
        """Class to instantiate the config object."""

        shift = True
        ctf = True

    names = get_starfile_metadata_names(Config)
    for name in names:
        assert isinstance(name, str) and name[:5] == "__rln"


def test_write_starfile():
    """Test if the saved star file exists."""
    output_path = "tests/data/"
    datalist = [[1, 2, 3]]
    variable_names = ["a", "b", "c"]
    save_name = "temp"

    write_starfile(output_path, datalist, variable_names, save_name)
    expected_file = os.path.join(output_path, save_name + ".star")
    assert os.path.isfile(expected_file)
    os.remove(expected_file)


def test_save_starfile_cryoem_convention():
    """Test if the saved star file exists."""
    output_path = "tests/data/"
    data_list = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]]

    class Config:
        """Class to instantiate the config object."""

        ctf = True
        shift = True

    save_name = "temp"

    write_starfile_cryoem_convention(output_path, data_list, Config, save_name)
    expected_file = os.path.join(output_path, save_name + ".star")
    assert os.path.isfile(expected_file)
    os.remove(expected_file)
