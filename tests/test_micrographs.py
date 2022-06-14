"""Unit tests for tem wrapper I/O helper functions."""

import os
import tempfile

import h5py
import mrcfile
import numpy as np
import torch

from ioSPI import micrographs


def test_populate_hdf5_with_dict():
    """Test populate_hdf5_with_dict helper with a simple hdf5 file."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".hdf5")
    tmp.close()

    data = {"a": 1.0, "b": None, "c": {"d": 1}}

    try:
        with h5py.File(tmp.name, "w") as f:
            micrographs._populate_hdf5_with_dict(f, "", data)
        with h5py.File(tmp.name, "r") as f:
            assert f["a"][()] == 1.0
            assert f["b"].asstr()[()] == "None"
            assert f["c/d"][()] == 1
    finally:
        os.unlink(tmp.name)


def test_read_micrograph_from_mrc():
    """Test read_micrograph_from_mrc helper function with a 2D mrc file."""
    tmp_mrc = tempfile.NamedTemporaryFile(delete=False, suffix=".mrc")
    tmp_mrc.close()
    data = np.zeros((5, 5), dtype=np.int8)

    try:
        with mrcfile.new(tmp_mrc.name, overwrite=True) as mrc:
            mrc.set_data(data)
        out_data = micrographs.read_micrograph_from_mrc(tmp_mrc.name)
        assert (out_data == data).all()
    finally:
        os.unlink(tmp_mrc.name)


def test_read_micrograph_from_mrc_large():
    """Test read_micrograph_from_mrc helper function with a 3D mrc file."""
    tmp_mrc = tempfile.NamedTemporaryFile(delete=False, suffix=".mrc")
    tmp_mrc.close()
    data = np.zeros((5, 5, 2), dtype=np.int8)

    try:
        with mrcfile.new(tmp_mrc.name, overwrite=True) as mrc:
            mrc.set_data(data)
        out_data = micrographs.read_micrograph_from_mrc(tmp_mrc.name)
        assert (out_data == data).all()
    finally:
        os.unlink(tmp_mrc.name)


def test_write_data_dict_to_hdf5():
    """Test write_data_dict_to_hdf5 helper with a simple hdf5 file."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".hdf5")
    tmp.close()

    data = {"a": 1, "b": 2, "c": 3}

    try:
        micrographs.write_data_dict_to_hdf5(tmp.name, data)
        with h5py.File(tmp.name, "r") as f:
            out_dict = f["data"]
            assert out_dict["a"][()] == 1
            assert out_dict["b"][()] == 2
            assert out_dict["c"][()] == 3
    finally:
        os.unlink(tmp.name)


def test_write_micrograph_to_mrc():
    """Test if the saved mrcs file exists."""
    projections = torch.randn(4, 1, 5, 5)
    output_path = "tests/data/"
    iterations = 0
    micrographs.write_micrograph_to_mrc(output_path, projections, iterations)
    expected_file = os.path.join(output_path, str(iterations).zfill(4) + ".mrcs")
    assert os.path.isfile(expected_file)
    os.remove(expected_file)
