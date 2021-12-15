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
            assert out_dict["a"][()] == 1
            assert out_dict["b"][()] == 2
            assert out_dict["c"][()] == 3
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
    hole_diameter = 200
    hole_thickness_center = 10
    hole_thickness_edge = 5
    voltage = 100
    energy_spread = 2.1
    electron_dose = 50
    electron_dose_std = 1
    dose = 20
    magnification = 21000
    spherical_aberration = 2.1
    chromatic_aberration = 2.1
    aperture_diameter = 50
    focal_length = 3.1
    aperture_angle = 0.5
    defocus = 1.2
    defocus_syst_error = 0
    defocus_nonsyst_error = 0
    optics_defocusout = "optics.txt"
    detector_nx = 2120
    detector_ny = 1080
    detector_pixel_size = 2
    detector_gain = 31
    noise = "no"
    detector_q_efficiency = 0.1
    mtf_params = [0.1, 0.0, 0.7, 0, 0]
    noise_override = "yes"
    log_file = "itslog.log"
    seed = 210
    snr = 0.6
    snr_db = 10
    key = particle_mrcout.split(".mrc")[0]

    try:
        with open(tmp_yml.name, "w") as f:
            data = {
                "molecular_model": {
                    "voxel_size_nm": voxel_size,
                    "particle_name": particle_name,
                    "particle_mrcout": particle_mrcout,
                },
                "specimen_grid_params": {
                    "hole_diameter_nm": hole_diameter,
                    "hole_thickness_center_nm": hole_thickness_center,
                    "hole_thickness_edge_nm": hole_thickness_edge,
                },
                "beam_parameters": {
                    "voltage_kv": voltage,
                    "energy_spread_v": energy_spread,
                    "electron_dose_e_per_nm2": electron_dose,
                    "electron_dose_std_e_per_nm2": electron_dose_std,
                },
                "optics_parameters": {
                    "magnification": magnification,
                    "spherical_aberration_mm": spherical_aberration,
                    "chromatic_aberration_mm": chromatic_aberration,
                    "aperture_diameter_um": aperture_diameter,
                    "focal_length_mm": focal_length,
                    "aperture_angle_mrad": aperture_angle,
                    "defocus_um": defocus,
                    "defocus_syst_error_um": defocus_syst_error,
                    "defocus_nonsyst_error_um": defocus_nonsyst_error,
                    "optics_defocusout": optics_defocusout,
                },
                "detector_parameters": {
                    "detector_nx_px": detector_nx,
                    "detector_ny_px": detector_ny,
                    "detector_pixel_size_um": detector_pixel_size,
                    "average_gain_count_per_electron": detector_gain,
                    "noise": noise,
                    "detector_q_efficiency": detector_q_efficiency,
                    "mtf_params": mtf_params,
                },
                "miscellaneous": {
                    "seed": seed,
                    "signal_to_noise": snr,
                    "signal_to_noise_db": snr_db,
                },
            }
            contents = yaml.dump(data)
            f.write(contents)
        out_dict = cryoemio.fill_parameters_dictionary(
            tmp_yml.name,
            mrc_file,
            pdb_file,
            crd_file,
            log_file,
            dose=dose,
            noise=noise_override,
        )

        assert out_dict["simulation"]["seed"] == seed
        assert out_dict["simulation"]["log_file"] == log_file

        assert out_dict["sample"]["diameter"] == hole_diameter
        assert out_dict["sample"]["thickness_center"] == hole_thickness_center
        assert out_dict["sample"]["thickness_edge"] == hole_thickness_edge

        assert out_dict["particle"]["name"] == particle_name
        assert out_dict["particle"]["voxel_size"] == voxel_size
        assert out_dict["particle"]["pdb_file"] == pdb_file
        assert out_dict["particle"]["map_file_re_out"] == key + "_real.mrc"
        assert out_dict["particle"]["map_file_im_out"] == key + "_imag.mrc"

        assert out_dict["particleset"]["name"] == particle_name
        assert out_dict["particleset"]["crd_file"] == crd_file

        assert out_dict["beam"]["voltage"] == voltage
        assert out_dict["beam"]["spread"] == energy_spread
        assert out_dict["beam"]["dose_per_im"] == dose
        assert out_dict["beam"]["dose_sd"] == electron_dose_std

        assert out_dict["optics"]["magnification"] == magnification
        assert out_dict["optics"]["cs"] == spherical_aberration
        assert out_dict["optics"]["cc"] == chromatic_aberration
        assert out_dict["optics"]["aperture"] == aperture_diameter
        assert out_dict["optics"]["focal_length"] == focal_length
        assert out_dict["optics"]["cond_ap_angle"] == aperture_angle
        assert out_dict["optics"]["defocus_nominal"] == defocus
        assert out_dict["optics"]["defocus_syst_error"] == defocus_syst_error
        assert out_dict["optics"]["defocus_nonsyst_error"] == defocus_nonsyst_error
        assert out_dict["optics"]["defocus_file_out"] == optics_defocusout

        assert out_dict["detector"]["det_pix_x"] == detector_nx
        assert out_dict["detector"]["det_pix_y"] == detector_ny
        assert out_dict["detector"]["pixel_size"] == detector_pixel_size
        assert out_dict["detector"]["gain"] == detector_gain
        assert out_dict["detector"]["use_quantization"] == noise_override
        assert out_dict["detector"]["dqe"] == detector_q_efficiency
        assert out_dict["detector"]["mtf_a"] == defocus
        assert out_dict["detector"]["mtf_b"] == mtf_params[1]
        assert out_dict["detector"]["mtf_c"] == mtf_params[2]
        assert out_dict["detector"]["mtf_alpha"] == mtf_params[3]
        assert out_dict["detector"]["mtf_beta"] == mtf_params[4]
        assert out_dict["detector"]["image_file_out"] == mrc_file

        assert out_dict["other"]["signal_to_noise"] == snr
        assert out_dict["other"]["signal_to_noise_db"] == snr_db
    finally:
        os.unlink(tmp_yml.name)


def test_fill_parameters_dictionary_min():
    """Test fill_parameters_dictionary with minimal garbage parameters."""
    tmp_yml = tempfile.NamedTemporaryFile(delete=False, suffix=".yml")
    tmp_yml.close()

    mrc_file = "a.mrc"
    pdb_file = "a.pdb"
    voxel_size = 0.2
    particle_name = "africa"
    crd_file = "a.crd"
    hole_diameter = 200
    hole_thickness_center = 10
    hole_thickness_edge = 5
    voltage = 100
    energy_spread = 2.1
    electron_dose = 50
    electron_dose_std = 1
    magnification = 21000
    spherical_aberration = 2.1
    chromatic_aberration = 2.1
    aperture_diameter = 50
    focal_length = 3.1
    aperture_angle = 0.5
    defocus_syst_error = 0
    defocus_nonsyst_error = 0
    detector_nx = 2120
    detector_ny = 1080
    detector_pixel_size = 2
    detector_gain = 31
    noise = "no"
    detector_q_efficiency = 0.1
    mtf_params = [0.1, 0.0, 0.7, 0, 0]
    log_file = "itslog.log"

    try:
        with open(tmp_yml.name, "w") as f:
            data = {
                "molecular_model": {
                    "voxel_size_nm": voxel_size,
                    "particle_name": particle_name,
                },
                "specimen_grid_params": {
                    "hole_diameter_nm": hole_diameter,
                    "hole_thickness_center_nm": hole_thickness_center,
                    "hole_thickness_edge_nm": hole_thickness_edge,
                },
                "beam_parameters": {
                    "voltage_kv": voltage,
                    "energy_spread_v": energy_spread,
                    "electron_dose_e_per_nm2": electron_dose,
                    "electron_dose_std_e_per_nm2": electron_dose_std,
                },
                "optics_parameters": {
                    "magnification": magnification,
                    "spherical_aberration_mm": spherical_aberration,
                    "chromatic_aberration_mm": chromatic_aberration,
                    "aperture_diameter_um": aperture_diameter,
                    "focal_length_mm": focal_length,
                    "aperture_angle_mrad": aperture_angle,
                    "defocus_syst_error_um": defocus_syst_error,
                    "defocus_nonsyst_error_um": defocus_nonsyst_error,
                },
                "detector_parameters": {
                    "detector_nx_px": detector_nx,
                    "detector_ny_px": detector_ny,
                    "detector_pixel_size_um": detector_pixel_size,
                    "average_gain_count_per_electron": detector_gain,
                    "noise": noise,
                    "detector_q_efficiency": detector_q_efficiency,
                    "mtf_params": mtf_params,
                },
            }
            contents = yaml.dump(data)
            f.write(contents)
        out_dict = cryoemio.fill_parameters_dictionary(
            tmp_yml.name, mrc_file, pdb_file, crd_file, log_file
        )

        assert out_dict["simulation"]["log_file"] == log_file

        assert out_dict["sample"]["diameter"] == hole_diameter
        assert out_dict["sample"]["thickness_center"] == hole_thickness_center
        assert out_dict["sample"]["thickness_edge"] == hole_thickness_edge

        assert out_dict["particle"]["name"] == particle_name
        assert out_dict["particle"]["voxel_size"] == voxel_size
        assert out_dict["particle"]["pdb_file"] == pdb_file

        assert out_dict["particleset"]["name"] == particle_name
        assert out_dict["particleset"]["crd_file"] == crd_file

        assert out_dict["beam"]["voltage"] == voltage
        assert out_dict["beam"]["spread"] == energy_spread
        assert out_dict["beam"]["dose_per_im"] == electron_dose
        assert out_dict["beam"]["dose_sd"] == electron_dose_std

        assert out_dict["optics"]["magnification"] == magnification
        assert out_dict["optics"]["cs"] == spherical_aberration
        assert out_dict["optics"]["cc"] == chromatic_aberration
        assert out_dict["optics"]["aperture"] == aperture_diameter
        assert out_dict["optics"]["focal_length"] == focal_length
        assert out_dict["optics"]["cond_ap_angle"] == aperture_angle
        assert out_dict["optics"]["defocus_nominal"] == mtf_params[0]
        assert out_dict["optics"]["defocus_syst_error"] == defocus_syst_error
        assert out_dict["optics"]["defocus_nonsyst_error"] == defocus_nonsyst_error

        assert out_dict["detector"]["det_pix_x"] == detector_nx
        assert out_dict["detector"]["det_pix_y"] == detector_ny
        assert out_dict["detector"]["pixel_size"] == detector_pixel_size
        assert out_dict["detector"]["gain"] == detector_gain
        assert out_dict["detector"]["use_quantization"] == noise
        assert out_dict["detector"]["dqe"] == detector_q_efficiency
        assert out_dict["detector"]["mtf_a"] == mtf_params[0]
        assert out_dict["detector"]["mtf_b"] == mtf_params[1]
        assert out_dict["detector"]["mtf_c"] == mtf_params[2]
        assert out_dict["detector"]["mtf_alpha"] == mtf_params[3]
        assert out_dict["detector"]["mtf_beta"] == mtf_params[4]
        assert out_dict["detector"]["image_file_out"] == mrc_file
    finally:
        os.unlink(tmp_yml.name)


def test_mrc2data():
    """Test mrc2data helper function with a 2D mrc file."""
    tmp_mrc = tempfile.NamedTemporaryFile(delete=False, suffix=".mrc")
    tmp_mrc.close()
    data = np.zeros((5, 5), dtype=np.int8)

    try:
        with mrcfile.new(tmp_mrc.name, overwrite=True) as mrc:
            mrc.set_data(data)
        out_data = cryoemio.mrc2data(tmp_mrc.name)
        assert (out_data == data).all()
    finally:
        os.unlink(tmp_mrc.name)


def test_mrc2data_large():
    """Test mrc2data helper function with a 3D mrc file."""
    tmp_mrc = tempfile.NamedTemporaryFile(delete=False, suffix=".mrc")
    tmp_mrc.close()
    data = np.zeros((5, 5, 2), dtype=np.int8)

    try:
        with mrcfile.new(tmp_mrc.name, overwrite=True) as mrc:
            mrc.set_data(data)
        out_data = cryoemio.mrc2data(tmp_mrc.name)
        assert (out_data == data).all()
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
            assert f["a"][()] == 1.0
            assert f["b"].asstr()[()] == "None"
            assert f["c/d"][()] == 1
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
    voxel_size = 0.2
    particle_name = "africa"
    crd_file = "a.crd"
    hole_diameter = 200
    hole_thickness_center = 10
    hole_thickness_edge = 5
    voltage = 100
    energy_spread = 2.1
    electron_dose = 50
    electron_dose_std = 1
    magnification = 21000
    spherical_aberration = 2.1
    chromatic_aberration = 2.1
    aperture_diameter = 50
    focal_length = 3.1
    aperture_angle = 0.5
    defocus_syst_error = 0
    defocus_nonsyst_error = 0
    detector_nx = 2120
    detector_ny = 1080
    detector_pixel_size = 2
    detector_gain = 31
    noise = "no"
    detector_q_efficiency = 0.1
    mtf_params = [0.1, 0.0, 0.7, 0, 0]
    log_file = "itslog.log"

    try:
        with open(tmp_yml.name, "w") as f:
            data = {
                "molecular_model": {
                    "voxel_size_nm": voxel_size,
                    "particle_name": particle_name,
                },
                "specimen_grid_params": {
                    "hole_diameter_nm": hole_diameter,
                    "hole_thickness_center_nm": hole_thickness_center,
                    "hole_thickness_edge_nm": hole_thickness_edge,
                },
                "beam_parameters": {
                    "voltage_kv": voltage,
                    "energy_spread_v": energy_spread,
                    "electron_dose_e_per_nm2": electron_dose,
                    "electron_dose_std_e_per_nm2": electron_dose_std,
                },
                "optics_parameters": {
                    "magnification": magnification,
                    "spherical_aberration_mm": spherical_aberration,
                    "chromatic_aberration_mm": chromatic_aberration,
                    "aperture_diameter_um": aperture_diameter,
                    "focal_length_mm": focal_length,
                    "aperture_angle_mrad": aperture_angle,
                    "defocus_syst_error_um": defocus_syst_error,
                    "defocus_nonsyst_error_um": defocus_nonsyst_error,
                },
                "detector_parameters": {
                    "detector_nx_px": detector_nx,
                    "detector_ny_px": detector_ny,
                    "detector_pixel_size_um": detector_pixel_size,
                    "average_gain_count_per_electron": detector_gain,
                    "noise": noise,
                    "detector_q_efficiency": detector_q_efficiency,
                    "mtf_params": mtf_params,
                },
            }
            contents = yaml.dump(data)
            f.write(contents)
        out_dict = cryoemio.fill_parameters_dictionary(
            tmp_yml.name, mrc_file, pdb_file, crd_file, log_file
        )
        cryoemio.write_inp_file(out_dict, tmp_inp.name)
    finally:
        os.unlink(tmp_inp.name)
        os.unlink(tmp_yml.name)
