"""Test dataset."""
import dataset as ds
import torch
import numpy as np


class TestDataset:
    def test_normalization_linear(self):
        dataset = torch.Tensor([[3., 7., 2., 7.], [3., 0., 8., 3.],
                                [6., 7., 4., 2.]])
        dataset = dataset.reshape((1, 4, 3))
        result = ds.normalization_linear(dataset)
        expected = torch.Tensor([[0.375, 0.875, 0.25, 0.875],
                                 [0.375, 0., 1., 0.375],
                                 [0.75, 0.875, 0.5, 0.25]]).reshape((1, 4, 3))

        assert torch.equal(result, expected)
        assert type(dataset) is torch.Tensor

    def test_split_dataset(self):
        frac_val = 0.2
        batch_size = 20
        dataset = torch.Tensor(np.ones((2000, 1, 64, 64)))
        tr_s, ts_s, tr_l, ts_l = ds.split_dataset(
            dataset, batch_size, frac_val)
        assert len(tr_s) == 1600
        assert len(ts_s) == 400
        assert len(tr_l) == 80
        assert len(ts_l) == 20
        assert type(tr_l) is torch.utils.data.dataloader.DataLoader
        assert type(ts_l) is torch.utils.data.dataloader.DataLoader
        assert type(tr_s) is torch.utils.data.dataset.Subset
        assert type(ts_s) is torch.utils.data.dataset.Subset

    def test_hinted_tuple_hook(self):
        dic1 = {"items": [4, 6], "__tuple__": True}
        list1 = [4, 6]
        assert ds.hinted_tuple_hook(dic1) == (4, 6)
        assert ds.hinted_tuple_hook(list1) == [4, 6]

    def test_open_dataset(self):
        dataset1 = ds.open_dataset("data_test.npy", new_size=64, is_3d=False)
        dataset2 = ds.open_dataset("data_test.npy", new_size=32, is_3d=False)
        assert type(dataset1) is torch.Tensor
        assert dataset1.shape == torch.Size([1, 1, 64, 64])
        assert dataset2.shape == torch.Size([1, 1, 32, 32])

    def test_load_parameters(self):
        parameters = ds.load_parameters("vae_parameters.json")
        assert len(parameters) == 5
        assert "skip_z" in parameters[2].keys()
        assert "enc_c" in parameters[2].keys()
        assert "is_3d" in parameters[2].keys()
        assert "img_shape" in parameters[2].keys()
