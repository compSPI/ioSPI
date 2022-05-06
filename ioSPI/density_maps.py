"""Read density maps."""

import mrcfile
import math
import numpy as np


def read_density_map_from_mrc(path, make_cubic=False):
    """Return density map from an input .mrc file.

    Parameters
    ----------
    path : str
        File name for .mrc file to convert to density map
    make_cubic : bool
        If true, pads the map to reach a cubic array
    """
    map_mrc = mrcfile.open(path)
    data = map_mrc.data
    if make_cubic:
        cube_length = max(data.shape)
        cubic_data = np.pad(data,
                            ((math.floor((cube_length - data.shape[0])/2.),
                              math.ceil((cube_length - data.shape[0])/2)),
                             (math.floor((cube_length - data.shape[1])/2.),
                              math.ceil((cube_length - data.shape[1])/2)),
                             (math.floor((cube_length - data.shape[2])/2.),
                              math.ceil((cube_length - data.shape[2])/2))),
                            'minimum')
        data = cubic_data
    return data
