"""contain function to load parameters from the starfile."""
import os

import numpy as np
import starfile


def check_star_file(path):
    """Check if the starfile exists and is valid."""
    if not os.path.isfile(path):
        raise FileNotFoundError("Input star file doesn't exist!")
    if ".star" not in path:
        raise FileExistsError("Input star file is not a valid star file!")


def starfile_opticsparams(config):
    """Update attributes of config with metadata from input starfile.

    Parameters
    ----------
    config: class
        Class containing parameters of the dataset generator.

    Returns
    -------
    config: class
    """
    check_star_file(config.input_starfile_path)
    df = starfile.read(config.input_starfile_path)
    config.side_len = df["optics"]["rlnImageSize"][0]
    config.kv = df["optics"]["rlnVoltage"][0]
    config.pixel_size = df["optics"]["rlnImagePixelSize"][0]
    config.spherical_aberration = df["optics"]["rlnSphericalAberration"][0]
    config.amplitude_contrast = df["optics"]["rlnAmplitudeContrast"][0]
    if hasattr(df["optics"], "rlnCtfBfactor"):
        config.b_factor = df["optics"]["rlnCtfBfactor"][0]

    return config


def return_names(config):
    """Return relion-convention names of metadata for starfile.

    Parameters
    ----------
    config: class
        Class containing parameters of the dataset generator.

    Returns
    -------
    names: list of str
    """
    names = [
        "__rlnImageName",
        "__rlnAngleRot",
        "__rlnAngleTilt",
        "__rlnAnglePsi",
    ]
    if config.shift:
        names += ["__rlnOriginX", "__rlnOriginY"]
    if config.ctf:
        names += ["__rlnDefocusU", "__rlnDefocusV", "__rlnDefocusAngle"]

    names += [
        "__rlnVoltage",
        "__rlnImagePixelSize",
        "__rlnSphericalAberration",
        "__rlnAmplitudeContrast",
        "__rlnCtfBfactor",
    ]
    return names


def starfile_data(datalist, rot_params, ctf_params, shift_params, iterations, config):
    """Append the datalist with the parameters of the simulator.

    Parameters
    ----------
    rot_params: dict of type str to {tensor}
        Dictionary of rotation parameters for a projection chunk
    ctf_params: dict of type str to {tensor}
        Dictionary of Contrast Transfer Function (CTF) parameters
         for a projection chunk
    shift_params: dict of type str to {tensor}
        Dictionary of shift parameters for a projection chunk
    iterations: int
        iteration number of the loop. Used in naming the mrcs file.
    config: class
         class containing parameters of the dataset generator.

    Returns
    -------
    datalist: list
        list containing the metadata of the projection chunks.
        This list is then used to save the starfile.
    """
    image_name = [
        str(idx).zfill(3) + "@" + str(iterations).zfill(4) + ".mrcs"
        for idx in range(config.batch_size)
    ]

    for num in range(config.batch_size):
        list_var = [
            image_name[num],
            rot_params["relion_angle_rot"][num].item(),
            rot_params["relion_angle_tilt"][num].item(),
            rot_params["relion_angle_psi"][num].item(),
        ]
        if shift_params:
            list_var += [
                shift_params["shift_x"][num].item(),
                shift_params["shift_y"][num].item(),
            ]
        if ctf_params:
            list_var += [
                1e4 * ctf_params["defocus_u"][num].item(),
                1e4 * ctf_params["defocus_v"][num].item(),
                np.radians(ctf_params["defocus_angle"][num].item()),
            ]

        list_var += [
            config.kv,
            config.pixel_size,
            config.cs,
            config.amplitude_contrast,
            config.b_factor,
        ]
        datalist.append(list_var)
    return datalist
