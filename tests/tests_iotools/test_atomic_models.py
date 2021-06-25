"""Unit test for read/write of atomic models."""

import unittest

import gemmi

from iospi.iotools.atomic_models import read_gemmi_model, write_gemmi_model


class TestAtomicModels(unittest.TestCase):
    """Test for reading and writing atomic models."""

    def test_read_or_write_gemmi_model_success(self):
        """Read Gemmi model success test"""
        for path in ".test.pdb" ".test.cif":
            write_gemmi_model(path)
            self.assertIs(read_gemmi_model(path), gemmi.Model("model"))

    def test_read_gemmi_model_oserror(self):
        """Read Gemmi OSError test"""
        path = "non-existing-file.pdb"
        with self.assertRaises(OSError) as exception_context:
            _ = read_gemmi_model(path)
        self.assertEqual(str(exception_context.exception), "File could not be found.")

    def test_read_gemmi_model_filename_extension_error(self):
        """Read Gemmi Filename Extension Error"""
        path = ".test.txt"
        with open(path, "w"):
            pass
        with self.assertRaises(Exception) as exception_context:
            _ = read_gemmi_model(path)
        self.assertEqual(
            str(exception_context.exception), "File format not recognized."
        )
