[![Test](https://github.com/compSPI/ioSPI/actions/workflows/test.yml/badge.svg)](https://github.com/compSPI/ioSPI/actions/workflows/test.yml)
[![Lint](https://github.com/compSPI/ioSPI/actions/workflows/lint.yml/badge.svg)](https://github.com/compSPI/ioSPI/actions/workflows/lint.yml)
[![Codecov](https://codecov.io/gh/compSPI/ioSPI/branch/master/graph/badge.svg?token=OBVOV3ZM1O)](https://codecov.io/gh/compSPI/ioSPI)
[![DeepSource](https://deepsource.io/gh/compSPI/ioSPI.svg/?label=active+issues&show_trend=true&token=4kJgheTFBCQhy6ItFV2Qp4cA)](https://deepsource.io/gh/compSPI/ioSPI/?ref=repository-badge)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6099894.svg)](https://doi.org/10.5281/zenodo.6099894)

# About

Welcome to the Python package: `ioSPI`: Methods and tools to read and write data in all formats. ioSPI Also provides methods to use other SPI tools developed outside of compSPI.

# Download

First create a conda environment with the required dependencies using the `enviroment.yml` file as follows:

    conda env create --file environment.yml

Then download:

    git clone https://github.com/compSPI/ioSPI.git

# Contribute

We strongly recommend installing our pre-commit hook, to ensure that your code follows our Python style guidelines. 
To do so, just run the following command line at the root of this repository:

    pre-commit install

With this hook, your code will be automatically formatted with our style conventions. If the pre-commit hooks black and isort mark "Failed" upon commit, this means that your code was not correctly formatted, but has been re-formatted by the hooks. Re-commit the result and check that the pre-commit marks "Passed".

Note that the hooks do not reformat docstrings automatically. If hooks failed with an error related to the documentation, you should correct this error yourself, commit the result and check that the pre-commit marks "Passed".

See our [contributing](https://github.com/compspi/compspi/blob/master/docs/contributing.rst) guidelines!
