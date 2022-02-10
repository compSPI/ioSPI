"""Read and write micrographs."""

import os

import h5py
import mrcfile
import numpy as np


def _populate_hdf5_with_dict(h5file, path, dic):
    """Recursively save dictionary contents to group.

    Parameters
    ----------
    h5file : h5py.File
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
            _populate_hdf5_with_dict(h5file, path + k + "/", v)
        else:
            raise ValueError("Cannot save %s type" % type(v))


def read_micrograph_from_mrc(path):
    """Return micrograph from an input .mrc file.

    Parameters
    ----------
    path : str
        File name for .mrc file to turn into micrograph
    """
    with mrcfile.open(path, "r", permissive=True) as mrc:
        micrograph = mrc.data
    if len(micrograph.shape) == 2:
        micrograph = micrograph[np.newaxis, ...]
    return micrograph


def write_data_dict_to_hdf5(path, data_dict):
    """Convert arbitrary dictionary data to hdf5 file format.

    Parameters
    ----------
    data_dict : dict
        Dictionary of data to save.
    path : str
        Relative path to h5 file.
    """
    dic = {"data": data_dict}
    with h5py.File(path, "w") as file:
        _populate_hdf5_with_dict(file, "/", dic)


def write_micrograph_to_mrc(path, micrograph, iterations):
    """Save the projection batch as an mrcs file in the output directory.

    Parameters
    ----------
    path: str
        path to save data
    micrograph: torch.Tensor
        projection from the simulator (batch_size,1, side_len, side_len)
    iterations: int
        iteration number of the loop. Used in naming the mrcs file.`
    """
    image_path = os.path.join(path, str(iterations).zfill(4) + ".mrcs")
    micrograph = micrograph.detach().cpu().numpy()
    with mrcfile.new(image_path, overwrite="True") as m:
        m.set_data(micrograph.astype("float32"))
