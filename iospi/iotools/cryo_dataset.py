"""Open datasets and process them to be used by a neural network."""

import functools
import json
import os

import h5py
import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, random_split

CUDA = torch.cuda.is_available()

KWARGS = {"num_workers": 1, "pin_memory": True} if CUDA else {}


def open_dataset(path, size, is_3d):
    """Open datasets and process data in order to make tensors.

    Parameters
    ----------
    path : string
        Path (myfile.h5 or myfile.npy).
    size : int
        Length of the image side.
    is_3d : boolean
        If 2d or 3d.

    Returns
    -------
    dataset: torch,
        Greyscale images.
    """
    if not os.path.exists(path):
        raise OSError
    if path.lower().endswith(".h5"):
        data_dict = h5py.File(path, "r")
        all_datasets = data_dict["particles"][:]
    else:
        all_datasets = np.load(path)
    dataset = np.asarray(all_datasets)
    img_shape = dataset.shape
    n_imgs = img_shape[0]
    new_dataset = []
    if is_3d:
        dataset = torch.Tensor(dataset)
        dataset = normalize_torch(dataset)
        if len(dataset.shape) == 4:
            dataset = dataset.reshape((len(dataset),) + (1,) + img_shape[1:])
    else:
        if len(img_shape) == 3:
            for i in range(n_imgs):
                image = Image.fromarray(dataset[i]).resize([size, size])
                new_dataset.append(np.asarray(image))
        elif len(img_shape) == 4:
            for i in range(n_imgs):
                image = Image.fromarray(dataset[i][0]).resize([size, size])
                new_dataset.append(np.asarray(image))
        dataset = torch.Tensor(new_dataset)
        dataset = normalize_torch(dataset)
        if len(img_shape) != 4:
            dataset = dataset.reshape((img_shape[0], 1, size, size))
    return dataset


def normalize_torch(dataset, scale="linear"):
    """Normalize a tensor.

    Parameters
    ----------
    dataset : torch tensor
        Images.
    scale : string
        Methods of normalization.

    Returns
    -------
    dataset : torch tensor
        Normalized images.
    """
    if scale == "linear":
        for i, data in enumerate(dataset):
            min_data = torch.min(data)
            max_data = torch.max(data)
            if max_data == min_data:
                raise ZeroDivisionError
            dataset[i] = (data - min_data) / (max_data - min_data)
    return dataset


def split_dataset(dataset, batch_size, frac_val):
    """Separate data in train and validation sets.

    Parameters
    ----------
    dataset : torch tensor
        Images.
    batch_size : int
        Batch_size.
    frac_val : float
        Ratio between validation and training datasets.

    Returns
    -------
    trainset : tensor
        Training images.
    testset : tensor
        Test images.
    trainloader : tensor
        Ready to be used by the NN for training images.
    testloader : tensor
        Ready to be used by the NN for test images.
    """
    n_imgs = len(dataset)
    n_val = int(n_imgs * frac_val)
    trainset, testset = random_split(dataset, [n_imgs - n_val, n_val])

    trainloader = DataLoader(trainset, batch_size=batch_size, shuffle=True, **KWARGS)
    testloader = DataLoader(testset, batch_size=batch_size, shuffle=False, **KWARGS)
    return trainset, testset, trainloader, testloader


def hinted_tuple_hook(obj):
    """Transform a list into tuple.

    Parameters
    ----------
    obj : *
        Value of a dic.

    Returns
    -------
    tuple,
        Transform the value of a dic into dic.
    obj : *
        Value of a dic.
    """
    if "__tuple__" in obj:
        return tuple(obj["items"])
    return obj


def load_parameters(path):
    """Load metadata for the VAE.

    Parameters
    ----------
    path : string
        Path to the file( myfile.json).

    Returns
    -------
    paths : dic
        Path to the data.
    shapes: dic
        Shape of every dataset.
    constants: dic
        Meta information for the vae.
    search_space: dic
        Meta information for the vae.
    meta_param_names: dic
        Names of meta parameters.
    """
    with open(path) as json_file:
        parameters = json.load(json_file, object_hook=hinted_tuple_hook)
        paths = parameters["paths"]
        shapes = parameters["shape"]
        constants = parameters["constants"]
        search_space = parameters["search_space"]
        meta_param_names = parameters["meta_param_names"]
        constants["conv_dim"] = len(constants["img_shape"][1:])
        constants["dataset_name"] = paths["simulated_2d"]
        constants["dim_data"] = functools.reduce(
            (lambda x, y: x * y), constants["img_shape"]
        )
        return paths, shapes, constants, search_space, meta_param_names
