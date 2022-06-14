"""Unit tests for the notebooks."""

import glob
import os
import subprocess
import tempfile

import pytest

NOTEBOOKS_DIR = "notebooks"
NOTEBOOKS_TO_SKIP = os.path.join(NOTEBOOKS_DIR, "download_and_upload_with_osf.ipynb")


def _exec_notebook(path):
    """Execute notebook at path.

    Parameters
    ----------
    path : str
        Relative path of the notebook.
        E.g. notebooks/particle_metadata.ipynb
    """
    file_name = tempfile.NamedTemporaryFile(suffix=".ipynb").name
    args = (
        f"jupyter nbconvert --to notebook --execute "
        f"--ExecutePreprocessor.timeout=1000 "
        f"--ExecutePreprocessor.kernel_name=python3 --output {file_name} {path}"
    )
    subprocess.run(args, shell=True)


paths = sorted(glob.glob(f"{NOTEBOOKS_DIR}/*.ipynb"))


@pytest.mark.parametrize("path", paths)
def test_notebook(path):
    """Test the notebook at path by executing it.

    Parameters
    ----------
    path : str
        Relative path of the notebooks.
        E.g. notebooks/particle_metadata.ipynb
    """
    if path in NOTEBOOKS_TO_SKIP:
        pytest.skip()
    _exec_notebook(path)
