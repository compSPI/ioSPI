"""Unit tests for density maps helper functions."""

import os
import tempfile

import mrcfile
import numpy as np

from ioSPI import density_maps


def test_read_density_map_from_mrc():
    """Test read_density_map_from_mrc util function with a random mrc file."""
    tmp_mrc = tempfile.NamedTemporaryFile(delete=False, suffix=".mrc")
    tmp_mrc.close()
    data = np.random.uniform(0, 1, (5, 5, 5)).astype(dtype="float32")

    try:
        with mrcfile.new(tmp_mrc.name, overwrite=True) as mrc:
            mrc.set_data(data)
        out_data = density_maps.read_density_map_from_mrc(tmp_mrc.name)
        assert (out_data == data).all()
    finally:
        os.unlink(tmp_mrc.name)


def test_read_density_map_from_mrc_cubic():
    """Test read_density_map_from_mrc util function make_cubic function."""
    tmp_mrc = tempfile.NamedTemporaryFile(delete=False, suffix=".mrc")
    tmp_mrc.close()
    data = np.random.uniform(0, 1, (4, 5, 6)).astype(dtype="float32")

    try:
        with mrcfile.new(tmp_mrc.name, overwrite=True) as mrc:
            mrc.set_data(data)
        out_data = density_maps.read_density_map_from_mrc(tmp_mrc.name, make_cubic=True)
        assert out_data.shape[0] == 6
        assert out_data.shape[1] == 6
        assert out_data.shape[2] == 6
    finally:
        os.unlink(tmp_mrc.name)
