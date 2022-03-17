"""Unit test for read/write of atomic models."""

import os

import gemmi
import pytest

from ..ioSPI.atomic_models import (
    read_atomic_model,
    write_atomic_model,
    write_cartesian_coordinates,
)

DATA = "tests/data"
OUT = ""


class TestAtomicModels:
    """Test for reading and writing atomic models."""

    def test_read_atomic_model_oserror(self):
        """Read with Gemmi - OSError test."""
        path = "non-existing-file.pdb"
        expected = "File could not be found."
        with pytest.raises(OSError) as exception_context:
            _ = read_atomic_model(path)
        actual = str(exception_context.value)
        assert expected in actual

    def test_read_atomic_model_filename_extension_error(self):
        """Read with Gemmi - Filename Extension Error."""
        path = "test.txt"
        expected = "File format not recognized."
        open(path, "w").close()
        with pytest.raises(ValueError) as exception_context:
            _ = read_atomic_model(path)
        os.remove(path)
        actual = str(exception_context.value)
        assert expected in actual

    @staticmethod
    def test_placeholder():
        """Test placeholder."""
        print("Test placeholder.")

    def test_read_atomic_model_from_pdb(self):
        """Test read_gemmi_model for pdb."""
        pdb_filename = "2dhb.pdb"
        path = os.path.join(DATA, pdb_filename)
        os.system(f"wget https://files.rcsb.org/download/{pdb_filename} -P {DATA}")
        model = read_atomic_model(path)
        assert model.__class__ is gemmi.Model

    def test_read_atomic_model_from_cif(self):
        """Test read_gemmi_model for cif."""
        cif_filename = "2dhb.cif"
        path = os.path.join(DATA, cif_filename)
        os.system(f"wget https://files.rcsb.org/download/{cif_filename} -P {DATA}")
        model = read_atomic_model(path)
        assert model.__class__ is gemmi.Model

    def test_write_atomic_model_to_pdb(self):
        """Test test_write_gemmi_model_pdb."""
        pdb_filename = "2dhb.pdb"
        path_input = os.path.join(DATA, pdb_filename)
        os.system(f"wget https://files.rcsb.org/download/{pdb_filename} -P {DATA}")
        model = read_atomic_model(path_input, assemble=False)
        path_output = os.path.join(OUT, f"test_{pdb_filename}")
        write_atomic_model(path_output, model)
        model = read_atomic_model(path_output, assemble=False)
        assert model.__class__ is gemmi.Model

    def test_write_atomic_model_to_cif(self):
        """Test test_write_gemmi_model_cif."""
        cif_filename = "2dhb.cif"
        path_input = os.path.join(DATA, cif_filename)
        os.system(f"wget https://files.rcsb.org/download/{cif_filename} -P tests/data")
        model = read_atomic_model(path_input, assemble=False)
        path_output = os.path.join(OUT, f"test_{cif_filename}")
        write_atomic_model(path_output, model)
        model = read_atomic_model(path_output, assemble=False)
        assert model.__class__ is gemmi.Model

    def test_write_cartesian_coordinates_to_pdb(self):
        """Test write_cartesian_coordinates for pdb."""
        path_output = os.path.join(OUT, "test_cartesian.pdb")
        write_cartesian_coordinates(path_output)
        model = read_atomic_model(path_output, assemble=False)
        assert model.__class__ is gemmi.Model

    def test_write_cartesian_coordinates_to_cif(self):
        """Test write_cartesian_coordinates for cif."""
        path_output = os.path.join(OUT, "test_cartesian.cif")
        write_cartesian_coordinates(path_output)
        model = read_atomic_model(path_output, assemble=False)
        assert model.__class__ is gemmi.Model
