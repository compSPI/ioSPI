"""Read density maps."""

import mrcfile


def read_density_map_from_mrc(path):
    """Return density map from an input .mrc file.

    Parameters
    ----------
    path : str
        File name for .mrc file to convert to density map
    """
    map_mrc = mrcfile.open(path)
    return map_mrc.data
