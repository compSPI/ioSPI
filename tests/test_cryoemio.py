"""Unit test for tem wrapper I/O helper functions."""
import os
import tempfile

import h5py
import mrcfile
import numpy as np
import yaml

from ioSPI import cryoemio


def test_data_and_dic2hdf5():
    """Test data_and_dic2hdf5 helper with a simple hdf5 file."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".hdf5")
    tmp.close()

    data = {"a": 1, "b": 2, "c": 3}

    try:
        cryoemio.data_and_dic2hdf5(data, tmp.name)
        with h5py.File(tmp.name, "r") as f:
            out_dict = f["data"]
            assert out_dict["a"][0] == 1
            assert out_dict["b"][0] == 2
            assert out_dict["c"][0] == 3
    finally:
        os.unlink(tmp.name)


def test_fill_parameters_dictionary_max():
    """Test fill_parameters_dictionary with maximal garbage parameters."""
    tmp_yml = tempfile.NamedTemporaryFile(delete=False, suffix=".yml")
    tmp_yml.close()

    mrc_file = "a.mrc"
    pdb_file = "a.pdb"
    voxel_size = 0.2
    particle_name = "africa"
    particle_mrcout = "b.mrc"
    crd_file = "a.crd"
    sample_dimensions = [200, 10, 5]
    beam_params = [100, 2.1, 50, 1]
    dose = 20
    optics_params = [21000, 2.1, 2.1, 50, 3.1, 0.5, 1.2, 0, 0]
    defocus = 1.5
    optics_defocout = "optics.txt"
    detector_params = [2120, 1080, 2, 31, "no", 0.1, 0.1, 0.0, 0.7, 0, 0]
    noise = 0.1
    log_file = "itslog.log"
    seed = 210
    key = particle_mrcout.split(".mrc")[0]

    try:
        with open(tmp_yml.name, "w") as f:
            data = {
                "mrc_file": mrc_file,
                "pdb_file": pdb_file,
                "voxel_size": voxel_size,
                "particle_name": particle_name,
                "particle_mrcout": particle_mrcout,
                "crd_file": crd_file,
                "sample_dimensions": sample_dimensions,
                "beam_params": beam_params,
                "dose": dose,
                "optics_params": optics_params,
                "defocus": defocus,
                "optics_defocout": optics_defocout,
                "detector_params": detector_params,
                "noise": noise,
                "log_file": log_file,
                "seed": seed,
            }
            contents = yaml.dump(data)
            f.write(contents)
        out_dict = cryoemio.fill_parameters_dictionary(tmp_yml.name)

        print(f"out_dict:\n{out_dict}\n")
        assert out_dict["simulation"]["seed"] == seed
        assert out_dict["simulation"]["log_file"] == log_file

        assert out_dict["sample"]["diameter"] == sample_dimensions[0]
        assert out_dict["sample"]["thickness_center"] == sample_dimensions[1]
        assert out_dict["sample"]["thickness_edge"] == sample_dimensions[2]

        assert out_dict["particle"]["name"] == particle_name
        assert out_dict["particle"]["voxel_size"] == voxel_size
        assert out_dict["particle"]["pdb_file"] == pdb_file
        assert out_dict["particle"]["map_file_re_out"] == key + "_real.mrc"
        assert out_dict["particle"]["map_file_im_out"] == key + "_imag.mrc"

        assert out_dict["particleset"]["name"] == particle_name
        assert out_dict["particleset"]["crd_file"] == crd_file

        assert out_dict["beam"]["voltage"] == beam_params[0]
        assert out_dict["beam"]["spread"] == beam_params[1]
        assert out_dict["beam"]["dose_per_im"] == dose
        assert out_dict["beam"]["dose_sd"] == beam_params[3]

        assert out_dict["optics"]["magnification"] == optics_params[0]
        assert out_dict["optics"]["cs"] == optics_params[1]
        assert out_dict["optics"]["cc"] == optics_params[2]
        assert out_dict["optics"]["aperture"] == optics_params[3]
        assert out_dict["optics"]["focal_length"] == optics_params[4]
        assert out_dict["optics"]["cond_ap_angle"] == optics_params[5]
        assert out_dict["optics"]["defocus_nominal"] == optics_params[6]
        assert out_dict["optics"]["defocus_syst_error"] == optics_params[7]
        assert out_dict["optics"]["defocus_nonsyst_error"] == optics_params[8]
        assert out_dict["optics"]["defocus_file_out"] == optics_defocout

        assert out_dict["detector"]["det_pix_x"] == detector_params[0]
        assert out_dict["detector"]["det_pix_y"] == detector_params[1]
        assert out_dict["detector"]["pixel_size"] == detector_params[2]
        assert out_dict["detector"]["gain"] == detector_params[3]
        assert out_dict["detector"]["use_quantization"] == noise
        assert out_dict["detector"]["dqe"] == detector_params[5]
        assert out_dict["detector"]["mtf_a"] == defocus
        assert out_dict["detector"]["mtf_b"] == detector_params[7]
        assert out_dict["detector"]["mtf_c"] == detector_params[8]
        assert out_dict["detector"]["mtf_alpha"] == detector_params[9]
        assert out_dict["detector"]["mtf_beta"] == detector_params[10]
        assert out_dict["detector"]["image_file_out"] == mrc_file
    finally:
        os.unlink(tmp_yml.name)


def test_fill_parameters_dictionary_min():
    """Test fill_parameters_dictionary with minimal garbage parameters."""
    tmp_yml = tempfile.NamedTemporaryFile(delete=False, suffix=".yml")
    tmp_yml.close()

    mrc_file = "a.mrc"
    pdb_file = "a.pdb"
    crd_file = "a.crd"

    try:
        with open(tmp_yml.name, "w") as f:
            data = {"mrc_file": mrc_file, "pdb_file": pdb_file, "crd_file": crd_file}
            contents = yaml.dump(data)
            f.write(contents)
        out_dict = cryoemio.fill_parameters_dictionary(tmp_yml.name)

        print(f"out_dict:\n{out_dict}\n")
        assert out_dict["particle"]["pdb_file"] == pdb_file
        assert out_dict["detector"]["image_file_out"] == mrc_file
        assert out_dict["particleset"]["crd_file"] == crd_file
    finally:
        os.unlink(tmp_yml.name)


def test_mrc2data():
    """Test mrc2data helper function with a 2D mrc file."""
    tmp_mrc = tempfile.NamedTemporaryFile(delete=False, suffix=".mrc")
    tmp_mrc.close()
    data = np.zeros((5, 5), dtype=np.int8)

    try:
        with mrcfile.open(tmp_mrc.name) as mrc:
            mrc.set_data(data)
        out_data = cryoemio.mrc2data(tmp_mrc.name)
        print("out_data:\n{out_data}\n")
        assert out_data == data
    finally:
        os.unlink(tmp_mrc.name)


def test_mrc2data_large():
    """Test mrc2data helper function with a 3D mrc file."""
    tmp_mrc = tempfile.NamedTemporaryFile(delete=False, suffix=".mrc")
    tmp_mrc.close()
    data = np.zeros((5, 5, 2), dtype=np.int8)

    try:
        with mrcfile.open(tmp_mrc.name) as mrc:
            mrc.set_data(data)
        out_data = cryoemio.mrc2data(tmp_mrc.name)
        print("out_data:\n{out_data}\n")
        assert out_data == data
    finally:
        os.unlink(tmp_mrc.name)


def test_recursively_save_dict_contents_to_group():
    """Test recursively_save_dict_contents_to_group helper with a simple hdf5 file."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".hdf5")
    tmp.close()

    data = {"a": 1.0, "b": None, "c": {"d": 1}}

    try:
        with h5py.File(tmp.name, "w") as f:
            cryoemio.recursively_save_dict_contents_to_group(f, "", data)
        with h5py.File(tmp.name, "r") as f:
            print(f"f[a] = {f['a']}, f[b] = {f['b']}, f[c/d] = {f['c/d']}")
            assert f["a"] == 1.0 and f["b"] == "None" and f["c/d"] == 1
    finally:
        os.unlink(tmp.name)


def test_write_inp_file():
    """Test write_inp_file helper with output from fill_parameters_dictionary."""
    tmp_inp = tempfile.NamedTemporaryFile(delete=False, suffix=".imp")
    tmp_inp.close()
    tmp_yml = tempfile.NamedTemporaryFile(delete=False, suffix=".yml")
    tmp_yml.close()

    mrc_file = "a.mrc"
    pdb_file = "a.pdb"
    crd_file = "a.crd"

    try:
        with open(tmp_yml.name, "w") as f:
            data = {"mrc_file": mrc_file, "pdb_file": pdb_file, "crd_file": crd_file}
            contents = yaml.dump(data)
            f.write(contents)
        out_dict = cryoemio.fill_parameters_dictionary(tmp_yml.name)
        cryoemio.write_inp_file(out_dict, tmp_inp.name)
    finally:
        os.unlink(tmp_inp.name)
        os.unlink(tmp_yml.name)
