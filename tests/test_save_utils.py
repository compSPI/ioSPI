"""Contain test functions for save_utils."""
import os

import torch

from ioSPI.save_utils import save_mrc, save_starfile, save_starfile_cryoem_convention


def test_save_mrc():
    """Test if the saved mrcs file exists."""
    projections = torch.randn(4, 1, 5, 5)
    output_path = "tests/data/"
    iterations = 0
    save_mrc(output_path, projections, iterations)
    expected_file = os.path.join(output_path, str(iterations).zfill(4) + ".mrcs")
    assert os.path.isfile(expected_file)
    os.remove(expected_file)


def test_save_starfile_cryoem_convention():
    """Test if the saved star file exists."""
    output_path = "tests/data/"
    datalist = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]]

    class config:
        """Class to instantiate the config object."""

        ctf = True
        shift = True

    save_name = "temp"

    save_starfile_cryoem_convention(output_path, datalist, config, save_name)
    expected_file = os.path.join(output_path, save_name + ".star")
    assert os.path.isfile(expected_file)
    os.remove(expected_file)


def test_save_starfile():
    """Test if the saved star file exists."""
    output_path = "tests/data/"
    datalist = [[1, 2, 3]]
    variable_names = ["a", "b", "c"]
    save_name = "temp"

    save_starfile(output_path, datalist, variable_names, save_name)
    expected_file = os.path.join(output_path, save_name + ".star")
    assert os.path.isfile(expected_file)
    os.remove(expected_file)
