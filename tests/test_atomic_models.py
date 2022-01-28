"""Unit test for read/write of atomic models."""

import os

import gemmi
import pytest

from ioSPI.iotools.atomic_models import read_gemmi_model, write_gemmi_model


class TestAtomicModels:
    """Test for reading and writing atomic models."""

    def test_read_gemmi_model_oserror(self):
        """Read with Gemmi - OSError test."""
        path = "non-existing-file.pdb"
        expected = "File could not be found."
        with pytest.raises(OSError) as exception_context:
            _ = read_gemmi_model(path)
        actual = str(exception_context.value)
        assert expected in actual

    def test_read_gemmi_model_filename_extension_error(self):
        """Read with Gemmi - Filename Extension Error."""
        path = "test.txt"
        expected = "File format not recognized."
        open(path, "w").close()
        with pytest.raises(ValueError) as exception_context:
            _ = read_gemmi_model(path)
        os.remove(path)
        actual = str(exception_context.value)
        assert expected in actual

    @staticmethod
    def test_placeholder():
        """Test placeholder."""
        print("Test placeholder.")

    def test_read_gemmi_model_pdb(self):
        """Test read_gemmi_model for pdb."""
        path = "2dhb.pdb"
        os.system("wget https://files.rcsb.org/download/" + path)
        model = read_gemmi_model(path)
        assert model.__class__ is gemmi.Model

    def test_read_gemmi_model_cif(self):
        """Test read_gemmi_model for cif."""
        path = "2dhb.cif"
        os.system("wget https://files.rcsb.org/download/" + path)
        model = read_gemmi_model(path)
        assert model.__class__ is gemmi.Model

    def test_write_gemmi_model_pdb(self):
        """Test test_write_gemmi_model_pdb."""
        path_input = "2dhb.pdb"
        os.system("wget https://files.rcsb.org/download/" + path_input)
        model = read_gemmi_model(path_input, assemble=False)
        path_output = "test_" + path_input
        write_gemmi_model(path_output, model)
        model = read_gemmi_model(path_output, assemble=False)
        assert model.__class__ is gemmi.Model

    def test_write_gemmi_model_cif(self):
        """Test test_write_gemmi_model_cif."""
        path_input = "2dhb.cif"
        os.system("wget https://files.rcsb.org/download/" + path_input)
        model = read_gemmi_model(path_input, assemble=False)
        path_output = "test_" + path_input
        write_gemmi_model(path_output, model)
        model = read_gemmi_model(path_output, assemble=False)
        assert model.__class__ is gemmi.Model
