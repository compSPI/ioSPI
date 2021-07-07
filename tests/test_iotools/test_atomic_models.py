"""Unit test for read/write of atomic models."""

import os

import pytest

from ioSPI.iotools.atomic_models import read_gemmi_model


class TestAtomicModels:
    """Test for reading and writing atomic models."""

    def test_read_gemmi_model_oserror(self):
        """Read with Gemmi - OSError test"""
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
