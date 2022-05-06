"""Unit test for read/write of atomic models."""

import os

import gemmi
import numpy as np
import pytest

from ioSPI.atomic_models import (
    extract_atomic_parameter,
    extract_gemmi_atoms,
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
        os.remove(path)
        assert model.__class__ is gemmi.Model

    def test_read_atomic_model_from_cif(self):
        """Test read_gemmi_model for cif."""
        cif_filename = "2dhb.cif"
        path = os.path.join(DATA, cif_filename)
        os.system(f"wget https://files.rcsb.org/download/{cif_filename} -P {DATA}")
        model = read_atomic_model(path)
        os.remove(path)
        assert model.__class__ is gemmi.Model

    def test_extract_gemmi_atoms(self):
        """Check that extraction retrieves correct no. of chains."""
        pdb_filename = "2dhb.pdb"
        path = os.path.join(DATA, pdb_filename)
        os.system(f"wget https://files.rcsb.org/download/{pdb_filename} -P {DATA}")
        model = read_atomic_model(path, assemble=False)
        os.remove(path)
        atoms = extract_gemmi_atoms(model, chains=None, split_chains=True)
        assert len(atoms) == 2  # expecting two chains
        atoms = extract_gemmi_atoms(model, chains=["A"], split_chains=True)
        assert len(atoms) == 1  # expecting one chain
        atoms = extract_gemmi_atoms(model)
        assert len(atoms) == 2201  # number of atoms, post-cleaning

    def test_extract_atomic_parameters(self):
        """Check that form factors are same for same element type."""
        pdb_filename = "2dhb.pdb"
        path = os.path.join(DATA, pdb_filename)
        os.system(f"wget https://files.rcsb.org/download/{pdb_filename} -P {DATA}")
        model = read_atomic_model(path, assemble=False)
        os.remove(path)
        atoms = extract_gemmi_atoms(model)

        atomic_coordinates = extract_atomic_parameter(atoms, "cartesian_coordinates")
        assert len(atomic_coordinates[0]) == 3  # x, y and z

        indices = [i for i in range(len(atoms)) if atoms[i].element.name == "N"]
        for ptype in ["electron_form_factor_a", "electron_form_factor_b"]:
            params = extract_atomic_parameter(atoms, ptype)
            ffs_N = np.array(params)[np.array(indices).astype(int)]
            assert np.allclose(ffs_N[0], ffs_N)

        expected = "Atomic parameter type not recognized."
        with pytest.raises(ValueError) as exception_context:
            _ = extract_atomic_parameter(atoms, "color")
        actual = str(exception_context.value)
        assert expected in actual

        atoms = extract_gemmi_atoms(model, split_chains=True)
        params = extract_atomic_parameter(
            atoms, "cartesian_coordinates", split_chains=True
        )
        assert len(params) == 2  # expect two chains

    def test_write_atomic_model_to_pdb(self):
        """Test test_write_gemmi_model_pdb."""
        pdb_filename = "2dhb.pdb"
        path_input = os.path.join(DATA, pdb_filename)
        os.system(f"wget https://files.rcsb.org/download/{pdb_filename} -P {DATA}")
        model = read_atomic_model(path_input, assemble=False)
        os.remove(path_input)
        path_output = os.path.join(OUT, f"test_{pdb_filename}")
        write_atomic_model(path_output, model)
        model = read_atomic_model(path_output, assemble=False)
        os.remove(path_output)
        assert model.__class__ is gemmi.Model

    def test_write_atomic_model_to_cif(self):
        """Test test_write_gemmi_model_cif."""
        cif_filename = "2dhb.cif"
        path_input = os.path.join(DATA, cif_filename)
        os.system(f"wget https://files.rcsb.org/download/{cif_filename} -P tests/data")
        model = read_atomic_model(path_input, assemble=False)
        os.remove(path_input)
        path_output = os.path.join(OUT, f"test_{cif_filename}")
        write_atomic_model(path_output, model)
        model = read_atomic_model(path_output, assemble=False)
        os.remove(path_output)
        assert model.__class__ is gemmi.Model

    def test_write_cartesian_coordinates_filename_extension_error(self):
        """Test output format is recognized."""
        path = "test.txt"
        expected = "File format not recognized."
        with pytest.raises(ValueError) as exception_context:
            write_cartesian_coordinates(path)
        actual = str(exception_context.value)
        assert expected in actual

    def test_write_cartesian_coordinates_input_shape(self):
        """Test shape of input array."""
        path = "test.cif"
        array = np.empty((1, 1))
        expected = "Numpy array of cartesian coordinates should be of shape (Natom, 3)."
        with pytest.raises(ValueError) as exception_context:
            write_cartesian_coordinates(path, cartesian_coordinates_np=array)
        actual = str(exception_context.value)
        assert expected in actual

    def test_write_cartesian_coordinates_to_pdb(self):
        """Test write_cartesian_coordinates for pdb."""
        path_output = os.path.join(OUT, "test_cartesian.pdb")
        write_cartesian_coordinates(path_output)
        model = read_atomic_model(path_output, assemble=False)
        os.remove(path_output)
        assert model.__class__ is gemmi.Model

    def test_write_cartesian_coordinates_to_cif(self):
        """Test write_cartesian_coordinates for cif."""
        path_output = os.path.join(OUT, "test_cartesian.cif")
        write_cartesian_coordinates(path_output)
        model = read_atomic_model(path_output, assemble=False)
        os.remove(path_output)
        assert model.__class__ is gemmi.Model
