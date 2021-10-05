"""Test cryo_datasets."""

import numpy as np
import torch

from ..ioSPI.iotools import cryo_dataset


class TestDataset:
    """Test Dataset."""

    @staticmethod
    def test_normalize_torch():
        """Test test_normalize_torch."""
        dataset = torch.Tensor(
            [[3.0, 7.0, 2.0, 7.0], [3.0, 0.0, 8.0, 3.0], [6.0, 7.0, 4.0, 2.0]]
        )
        dataset = dataset.reshape((1, 4, 3))
        result = cryo_dataset.normalize_torch(dataset)
        expected = torch.Tensor(
            [
                [0.375, 0.875, 0.25, 0.875],
                [0.375, 0.0, 1.0, 0.375],
                [0.75, 0.875, 0.5, 0.25],
            ]
        ).reshape((1, 4, 3))

        assert torch.equal(result, expected)
        assert type(result) is torch.Tensor

    @staticmethod
    def test_split_dataset():
        """Test test_split_dataset."""
        frac_val = 0.2
        batch_size = 20
        dataset = torch.Tensor(np.ones((2000, 1, 64, 64)))
        tr_s, ts_s, tr_l, ts_l = cryo_dataset.split_dataset(
            dataset, batch_size, frac_val
        )
        assert len(tr_s) == 1600
        assert len(ts_s) == 400
        assert len(tr_l) == 80
        assert len(ts_l) == 20
        assert type(tr_l) is torch.utils.data.dataloader.DataLoader
        assert type(ts_l) is torch.utils.data.dataloader.DataLoader
        assert type(tr_s) is torch.utils.data.dataset.Subset
        assert type(ts_s) is torch.utils.data.dataset.Subset

    @staticmethod
    def test_hinted_tuple_hook():
        """Test test_hinted_tuple_hook."""
        dic1 = {"items": [4, 6], "__tuple__": True}
        list1 = [4, 6]
        assert cryo_dataset.hinted_tuple_hook(dic1) == (4, 6)
        assert cryo_dataset.hinted_tuple_hook(list1) == [4, 6]

    @staticmethod
    def test_open_dataset():
        """Test test_open_dataset."""
        path = "./tests/test_iotools/data_test_cryo_dataset.npy"
        dataset1 = cryo_dataset.open_dataset(path, size=64, is_3d=False)
        dataset2 = cryo_dataset.open_dataset(path, size=32, is_3d=False)
        assert type(dataset1) is torch.Tensor
        assert dataset1.shape == torch.Size([1, 1, 64, 64])
        assert dataset2.shape == torch.Size([1, 1, 32, 32])

    @staticmethod
    def test_load_parameters():
        """Test test_load_parameters."""
        path = "./tests/test_iotools/vae_parameters.json"
        parameters = cryo_dataset.load_parameters(path)
        assert len(parameters) == 5
        assert "skip_z" in parameters[2].keys()
        assert "enc_c" in parameters[2].keys()
        assert "is_3d" in parameters[2].keys()
        assert "img_shape" in parameters[2].keys()
