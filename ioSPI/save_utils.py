"""contain functions to save dataset and associated variables in different formats."""

import os

import mrcfile
import pandas as pd
import starfile

from .starfile_utils import return_names


def save_mrc(output_path, projections, iterations):
    """Save the projection chunks as an mrcs file in the output directory.

    Parameters
    ----------
    projections: torch.Tensor
        projection from the simulator (chunks,1, sidelen, sidelen)
    iterations: int
        iteration number of the loop. Used in naming the mrcs file.`
    """
    image_path = os.path.join(output_path, str(iterations).zfill(4) + ".mrcs")
    projections = projections.detach().cpu().numpy()
    with mrcfile.new(image_path, overwrite="True") as m:
        m.set_data(projections.astype("float32"))


def save_starfile(output_path, datalist, config, save_name):
    """Save the metadata in a starfile in the output directory."""
    df = pd.DataFrame(
        data=datalist,
        index=[idx for idx in range(len(datalist))],
        columns=return_names(config),
    )
    starfile.write(df, os.path.join(output_path, save_name + ".star"), overwrite=True)


def save_configfile(output_path, config):
    """Save the config as .txt and .cfg in the output directory."""
    with open(os.path.join(output_path, "config.cfg"), "w") as fp:
        config.config.write(fp)
    with open(os.path.join(output_path, "config.txt"), "w") as fp:
        config.config.write(fp)
