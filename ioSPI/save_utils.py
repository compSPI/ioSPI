"""contain functions to save dataset and associated variables in different formats."""

import os

import mrcfile
import pandas as pd
import starfile

from .starfile_utils import return_names


def save_mrc(output_path, projections, iterations):
    """Save the projection batch as an mrcs file in the output directory.

    Parameters
    ----------
    output_path: str
        path to save data
    projections: torch.Tensor
        projection from the simulator (batch_size,1, side_len, side_len)
    iterations: int
        iteration number of the loop. Used in naming the mrcs file.`
    """
    image_path = os.path.join(output_path, str(iterations).zfill(4) + ".mrcs")
    projections = projections.detach().cpu().numpy()
    with mrcfile.new(image_path, overwrite="True") as m:
        m.set_data(projections.astype("float32"))


def save_starfile_cryoem_convention(output_path, datalist, config, save_name):
    """Save the metadata in a starfile in the output directory.

    Parameters
    ----------
    output_path: str
        path to save starfile
    datalist: list
         list containing data set generation variables
    config: class
        class containing bool values
        ctf: bool
            indicates if the CTF effect is to be used in the forward model
        shift: bool
            indicates if the shift operator is to be used in the forward model.
    """
    cryoem_variable_names = return_names(config)
    save_starfile(output_path, datalist, cryoem_variable_names, save_name)


def save_starfile(output_path, datalist, variable_names, save_name):
    """Save the metadata in a starfile in the output directory.

    Parameters
    ----------
    output_path: str
        path to save starfile
    datalist: list
        list containing data set generation variables
    variable_names: list of str
        list containing name of the variables contained in the datalist
    save_name: str
        name of the starfile to be saved.
    """
    indices = [idx for idx in range(len(datalist))]
    df = pd.DataFrame(
        data=datalist,
        index=indices,
        columns=(variable_names),
    )
    starfile.write(df, os.path.join(output_path, save_name + ".star"), overwrite=True)
