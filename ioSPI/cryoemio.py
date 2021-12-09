"""Helper functions for tem.py processing of input and output files."""

import random

import h5py
import mrcfile
import numpy as np
import yaml


def mrc2data(mrc_file):
    """Return micrograph from an input .mrc file.

    Parameters
    ----------
    mrc_file : str
        File name for .mrc file to turn into micrograph
    """
    with mrcfile.open(mrc_file, "r", permissive=True) as mrc:
        micrograph = mrc.data
    if len(micrograph.shape) == 2:
        micrograph = micrograph[np.newaxis, ...]
    return micrograph


def data_and_dic2hdf5(data, h5_file):
    """Convert dictionary data to hdf5 file format.

    Parameters
    ----------
    data : dict
        Dictionary of data to save.
    h5_file : str
        Relative path to h5 file.
    """
    dic = {"data": data}
    with h5py.File(h5_file, "w") as file:
        recursively_save_dict_contents_to_group(file, "/", dic)


def recursively_save_dict_contents_to_group(h5file, path, dic):
    """Recursively save dictionary contents to group.

    Parameters
    ----------
    h5file : File
        .hdf5 file to write to.
    path : str
        Relative path to save dictionary contents.
    dic : dict
        Dictionary containing data.
    """
    for k, v in dic.items():
        if isinstance(v, (np.ndarray, np.int64, np.float64, int, float, str, bytes)):
            h5file[path + k] = v
        elif isinstance(v, type(None)):
            h5file[path + k] = str("None")
        elif isinstance(v, dict):
            recursively_save_dict_contents_to_group(h5file, path + k + "/", v)
        else:
            raise ValueError("Cannot save %s type" % type(v))


def fill_parameters_dictionary(
    yaml_file, mrc_file, pdb_file, crd_file, log_file, dose=None, noise=None
):
    """Return parameter dictionary with settings for simulation.

    Parameters
    ----------
    yaml_file : str
        Path to the .yml file with the parameters
    mrc_file : str
        Micrograph file
    pdb_file : str
        PDB file of sample
    crd_file : str
        Coordinates of the sample copies
    log_file : str
        Log file for the run
    dose : int
        If present, overrides beam_parameters[electron_dose]
    noise : str
        'yes' or 'no'. If present, overrides detector_params[noise]

    YAML file entries:
    ------------------
    *** molecular_model ***
    - voxel size                   : The size of voxels in the particle map in nm.
    - particle_name                : Name of the particle. Not very important.
    - particle_mrcout [OPTIONAL]   : if present, volume map of sample is written.

    *** specimen_grid_params ***
    - hole_diameter                : diameter in nm
    - hole_thickness_center        : thickness at center in nm
    - hole_thickness_edge          : thickness at edge in nm.

    *** beam_parameters ***
    - voltage                      : voltage in kV
    - energy_spread                : energy spread in V
    - electron_dose                : dose per image in e/nm**2
    - electron_dose_std            : standard deviation of dose per image

    *** optics_parameters ***
    - magnification                : magnification (81000; 105000; 130000)
    - spherical_aberration         : spherical aberration in mm
    - chromatic_aberration         : chromatic aberration in mm
    - aperture_diameter            : diam in um of aperture in back focal plane (50-100)
    - focal_length                 : focal length in mm of primary lens
    - aperture_angle               : aperture angle in mrad of the beam furnished by
                                         the condenser lens
    - defocus [OPTIONAL]           : nominal defocus value in um
    - defocus_syst_error           : standard deviation of a systematic error
                                         added to the nominal defocus, measured
                                         in um. Same error is added to the defocus
                                         of every image.
    - defocus_nonsyst_error        : standard deviation of a nonsystematic error
                                         added to the nominal defocus and the
                                         systematic error, measured in um. A new
                                         value of error is computed for every image.
    - optics_defocusout [OPTIONAL] : if present, defocus values written to file.

    *** detector_parameters ***
    - detector_Nx                  : number of pixels on detector along x axis
    - detector_Ny                  : number of pixels on detector along y axis
    - detector_pixel_size          : physical pixel size in um
    - detector_gain                : detector gain: avg number of counts per electron
    - noise                        : quantized electron waves result in noise
    - detector_Q_efficiency        : detector quantum efficiency
    - MTF_params                   : list of 5 MTF parameters

    *** miscellaneous ***
    - seed [OPTIONAL]              : seed for the run. If not present, random.
    """
    parameters = None
    with open(yaml_file, "r") as f:
        parameters = yaml.safe_load(f)

    # fill the dictionary
    dic = {"simulation": {}}
    if "miscellaneous" in parameters:
        if "seed" in parameters["miscellaneous"]:
            dic["simulation"]["seed"] = parameters["miscellaneous"]["seed"]
        else:
            random.seed()
            dic["simulation"]["seed"] = random.randint(0, int(1e10))
    dic["simulation"]["log_file"] = log_file
    dic["sample"] = {}
    dic["sample"]["diameter"] = parameters["specimen_grid_params"][
        "hole_diameter"
    ]  # diameter in nm
    dic["sample"]["thickness_center"] = parameters["specimen_grid_params"][
        "hole_thickness_center"
    ]  # thickness at center in nm
    dic["sample"]["thickness_edge"] = parameters["specimen_grid_params"][
        "hole_thickness_edge"
    ]  # thickness at edge in nm
    dic["particle"] = {}
    dic["particle"]["name"] = parameters["molecular_model"]["particle_name"]
    dic["particle"]["voxel_size"] = parameters["molecular_model"]["voxel_size"]
    dic["particle"]["pdb_file"] = pdb_file
    if "particle_mrcout" in parameters["molecular_model"]:
        key = parameters["molecular_model"]["particle_mrcout"].split(".mrc")[0]
        dic["particle"]["map_file_re_out"] = key + "_real.mrc"
        dic["particle"]["map_file_im_out"] = key + "_imag.mrc"
    else:
        dic["particle"]["map_file_re_out"] = None
    dic["particleset"] = {}
    dic["particleset"]["name"] = parameters["molecular_model"]["particle_name"]
    dic["particleset"]["crd_file"] = crd_file
    dic["beam"] = {}
    dic["beam"]["voltage"] = parameters["beam_parameters"]["voltage"]  # voltage in kV
    dic["beam"]["spread"] = parameters["beam_parameters"][
        "energy_spread"
    ]  # energy spread in V
    if dose is not None:
        dic["beam"]["dose_per_im"] = dose
    else:
        dic["beam"]["dose_per_im"] = parameters["beam_parameters"][
            "electron_dose"
        ]  # dose per image in e/nm**2
    dic["beam"]["dose_sd"] = parameters["beam_parameters"][
        "electron_dose_std"
    ]  # standard deviation of dose per image
    dic["optics"] = {}

    dic["optics"]["magnification"] = parameters["optics_parameters"][
        "magnification"
    ]  # magnification
    dic["optics"]["cs"] = parameters["optics_parameters"][
        "spherical_aberration"
    ]  # spherical aberration in mm
    dic["optics"]["cc"] = parameters["optics_parameters"][
        "chromatic_aberration"
    ]  # chromatic aberration in mm
    dic["optics"]["aperture"] = parameters["optics_parameters"][
        "aperture_diameter"
    ]  # diameter in um of aperture in back focal plane
    dic["optics"]["focal_length"] = parameters["optics_parameters"][
        "focal_length"
    ]  # focal length in mm of primary lens
    dic["optics"]["cond_ap_angle"] = parameters["optics_parameters"][
        "aperture_angle"
    ]  # aperture angle in mrad of the beam furnished by the condenser lens
    dic["detector"] = {}
    if "defocus" in parameters["optics_parameters"]:
        dic["optics"]["defocus_nominal"] = parameters["optics_parameters"]["defocus"]
        dic["detector"]["mtf_a"] = parameters["optics_parameters"]["defocus"]
    else:
        dic["optics"]["defocus_nominal"] = parameters["detector_parameters"][
            "MTF_params"
        ][0]
        dic["detector"]["mtf_a"] = parameters["detector_parameters"]["MTF_params"][0]
    dic["optics"]["defocus_syst_error"] = parameters["optics_parameters"][
        "defocus_syst_error"
    ]
    dic["optics"]["defocus_nonsyst_error"] = parameters["optics_parameters"][
        "defocus_nonsyst_error"
    ]
    if "optics_defocusout" in parameters["optics_parameters"]:
        dic["optics"]["defocus_file_out"] = parameters["optics_parameters"][
            "optics_defocusout"
        ]  # file to which defocus values are written
    else:
        dic["optics"]["defocus_file_out"] = None
    dic["detector"]["det_pix_x"] = parameters["detector_parameters"][
        "detector_Nx"
    ]  # number of pixels on detector along x axis
    dic["detector"]["det_pix_y"] = parameters["detector_parameters"][
        "detector_Ny"
    ]  # number of pixels on detector along y axis
    dic["detector"]["pixel_size"] = parameters["detector_parameters"][
        "detector_pixel_size"
    ]  # physical pixel size in um
    dic["detector"]["gain"] = parameters["detector_parameters"][
        "detector_gain"
    ]  # detector gain: average number of counts per electron
    if noise is not None:
        dic["detector"]["use_quantization"] = noise
    else:
        dic["detector"]["use_quantization"] = parameters["detector_parameters"][
            "noise"
        ]  # quantized electron waves result in noise
    dic["detector"]["dqe"] = parameters["detector_parameters"][
        "detector_Q_efficiency"
    ]  # detector quantum efficiency
    dic["detector"]["mtf_b"] = parameters["detector_parameters"]["MTF_params"][
        1
    ]  # parameter of MTF
    dic["detector"]["mtf_c"] = parameters["detector_parameters"]["MTF_params"][
        2
    ]  # parameter of MTF
    dic["detector"]["mtf_alpha"] = parameters["detector_parameters"]["MTF_params"][
        3
    ]  # parameter of MTF
    dic["detector"]["mtf_beta"] = parameters["detector_parameters"]["MTF_params"][
        4
    ]  # parameter of MTF
    # file with resulting micrograph
    dic["detector"]["image_file_out"] = mrc_file

    return dic


def write_inp_file(dict_params, inp_file="input.txt"):
    """Write parameters to input .inp file.

    Parameters
    ----------
    dict_params : dict
        Dictionary containing parameters to write.
    inp_file : str
        Relative path to input file.
    """
    with open(inp_file, "w") as inp:
        inp.write(
            "=== simulation ===\n"
            "generate_micrographs = yes\n"
            "rand_seed = {0[seed]}\n"
            "log_file = {0[log_file]}\n".format(dict_params["simulation"])
        )
        inp.write(
            "=== sample ===\n"
            "diameter = {0[diameter]:d}\n"
            "thickness_edge = {0[thickness_edge]:d}\n"
            "thickness_center = {0[thickness_center]:d}\n".format(dict_params["sample"])
        )
        inp.write(
            "=== particle {0[name]} ===\n"
            "source = pdb\n"
            "voxel_size = {0[voxel_size]}\n"
            "pdb_file_in = {0[pdb_file]}\n".format(dict_params["particle"])
        )
        if dict_params["particle"]["map_file_re_out"] is not None:
            inp.write(
                "map_file_re_out = {0[map_file_re_out]}\n"
                "map_file_im_out = {0[map_file_im_out]}\n".format(
                    dict_params["particle"]
                )
            )
        inp.write(
            "=== particleset ===\n"
            "particle_type = {0[name]}\n"
            "particle_coords = file\n"
            "coord_file_in = {0[crd_file]}\n".format(dict_params["particleset"])
        )
        inp.write(
            "=== geometry ===\n"
            "gen_tilt_data = yes\n"
            "tilt_axis = 0\n"
            "ntilts = 1\n"
            "theta_start = 0\n"
            "theta_incr = 0\n"
            "geom_errors = none\n"
        )
        inp.write(
            "=== electronbeam ===\n"
            "acc_voltage = {0[voltage]}\n"
            "energy_spread = {0[spread]}\n"
            "gen_dose = yes\n"
            "dose_per_im = {0[dose_per_im]}\n"
            "dose_sd = {0[dose_sd]}\n".format(dict_params["beam"])
        )
        inp.write(
            "=== optics ===\n"
            "magnification = {0[magnification]}\n"
            "cs = {0[cs]}\n"
            "cc = {0[cc]}\n"
            "aperture = {0[aperture]}\n"
            "focal_length = {0[focal_length]}\n"
            "cond_ap_angle = {0[cond_ap_angle]}\n"
            "gen_defocus = yes\n"
            "defocus_nominal = {0[defocus_nominal]}\n"
            "defocus_syst_error = {0[defocus_syst_error]}\n"
            "defocus_syst_error = {0[defocus_nonsyst_error]}\n".format(
                dict_params["optics"]
            )
        )
        if dict_params["optics"]["defocus_file_out"] is not None:
            inp.write(
                "defocus_file_out = {0[defocus_file_out]}\n".format(
                    dict_params["optics"]
                )
            )
        inp.write(
            "=== detector ===\n"
            "det_pix_x = {0[det_pix_x]}\n"
            "det_pix_y = {0[det_pix_y]}\n"
            "pixel_size = {0[pixel_size]}\n"
            "gain = {0[gain]}\n"
            "use_quantization = {0[use_quantization]}\n"
            "dqe = {0[dqe]}\n"
            "mtf_a = {0[mtf_a]}\n"
            "mtf_b = {0[mtf_b]}\n"
            "mtf_c = {0[mtf_c]}\n"
            "mtf_alpha = {0[mtf_alpha]}\n"
            "mtf_beta = {0[mtf_beta]}\n"
            "image_file_out = {0[image_file_out]}\n".format(dict_params["detector"])
        )
