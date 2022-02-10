"""Format and write particle metadata."""
import os

import numpy as np
import pandas as pd
import starfile


def check_star_file(path):
    """Check if the starfile exists and is valid."""
    if not os.path.isfile(path):
        raise FileNotFoundError("Input star file doesn't exist!")
    if ".star" not in path:
        raise FileExistsError("Input star file is not a valid star file!")


def format_metadata_for_writing(data_list, variable_names):
    """Perform formatting actions to prepare metadata for output to starfile.

    Parameters
    ----------
    data_list: list
        list containing data set generation variables
    variable_names: list of str
        list containing name of the variables contained in the datalist

    Returns
    -------
    metadata : pandas.DataFrame
        Metadata ready to be outputted in a starfile.
    """
    indices = list(range(len(data_list)))
    return pd.DataFrame(
        data=data_list,
        index=indices,
        columns=(variable_names),
    )


def format_metadata_for_writing_cryoem_convention(data_list, config):
    """Perform formatting actions to prepare metadata for output to starfile.

    Parameters
    ----------
    data_list: list
         list containing data set generation variables
    config: class
        class containing bool values
        ctf: bool
            indicates if the CTF effect is to be used in the forward model
        shift: bool
            indicates if the shift operator is to be used in the forward model.

    Returns
    -------
    metadata : pandas.DataFrame
        Metadata ready to be outputted in a starfile.
    """
    return format_metadata_for_writing(data_list, get_starfile_metadata_names(config))


def get_starfile_metadata_names(config):
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


def update_optics_config_from_starfile(config):
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
    config.cs = df["optics"]["rlnSphericalAberration"][0]
    config.amplitude_contrast = df["optics"]["rlnAmplitudeContrast"][0]
    if hasattr(df["optics"], "rlnCtfBfactor"):
        config.b_factor = df["optics"]["rlnCtfBfactor"][0]

    return config


def write_metadata_to_starfile(path, metadata, filename="metadata.star"):
    """Save the metadata in a starfile in the output directory.

    Parameters
    ----------
    path: str
        path to save starfile.
    metadata: pandas.DataFrame
        metadata to be outputted.
    filename: str
        name of the output file.
    """
    if filename.endswith(".star"):
        starfile.write(metadata, os.path.join(path, filename), overwrite=True)
    else:
        starfile.write(metadata, os.path.join(path, filename + ".star"), overwrite=True)
