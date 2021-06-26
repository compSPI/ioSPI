"""Unit test for read/write of atomic models."""

import unittest

from iospi.iotools.atomic_models import read_gemmi_model, write_gemmi_model

# import gemmi


class TestAtomicModels(unittest.TestCase):
    """Test for reading and writing atomic models."""

    # def test_read_or_write_gemmi_model_success(self):
    #     """Read Gemmi model success test"""
    #     expected = gemmi.Model("model")
    #     for path in ["test.pdb", "test.cif"]:
    #         write_gemmi_model(path, model=expected)
    #         actual = read_gemmi_model(path)
    #         self.assertIs(actual, expected)

    def test_read_gemmi_model_oserror(self):
        """Read Gemmi OSError test"""
        path = "non-existing-file.pdb"
        expected = "File could not be found."
        with self.assertRaises(OSError) as exception_context:
            _ = read_gemmi_model(path)
        actual = str(exception_context.exception)
        self.assertEqual(actual, expected)

    def test_read_gemmi_model_filename_extension_error(self):
        """Read Gemmi Filename Extension Error"""
        path = "test.txt"
        expected = "File format not recognized."
        with open(path, "w"):
            pass
        with self.assertRaises(Exception) as exception_context:
            _ = read_gemmi_model(path)
        actual = str(exception_context.exception)
        self.assertEqual(actual, expected)
