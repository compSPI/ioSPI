[![Test](https://github.com/compSPI/ioSPI/actions/workflows/test.yml/badge.svg)](https://github.com/compSPI/ioSPI/actions/workflows/test.yml)
[![Lint](https://github.com/compSPI/ioSPI/actions/workflows/lint.yml/badge.svg)](https://github.com/compSPI/ioSPI/actions/workflows/lint.yml)
[![Codecov](https://codecov.io/gh/compSPI/ioSPI/branch/master/graph/badge.svg?token=OBVOV3ZM1O)](https://codecov.io/gh/compSPI/ioSPI)
[![DeepSource](https://deepsource.io/gh/compSPI/ioSPI.svg/?label=active+issues&show_trend=true&token=4kJgheTFBCQhy6ItFV2Qp4cA)](https://deepsource.io/gh/compSPI/ioSPI/?ref=repository-badge)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6099894.svg)](https://doi.org/10.5281/zenodo.6099894)

# About

Welcome to the Python package: `ioSPI`: Methods and tools to read and write data in all formats. ioSPI Also provides methods to use other SPI tools developed outside of compSPI.

# Download

Clone the repository:

    git clone https://github.com/compSPI/ioSPI.git
    cd ioSPI
    
Create a conda environment with the required dependencies using the `enviroment.yml` file:

    conda env create --file environment.yml
    conda activate ioSPI

# Contribute

We strongly recommend installing our pre-commit hook, to ensure that your code
follows our Python style guidelines. To do so, just run the following command line at the root of this repository:

    pre-commit install

With this hook, your code will be automatically formatted with our style conventions. If the pre-commit hooks black and isort mark "Failed" upon commit, this means that your code was not correctly formatted, but has been re-formatted by the hooks. Re-commit the result and check that the pre-commit marks "Passed".

Note that the hooks do not reformat docstrings automatically. If hooks failed with an error related to the documentation, you should correct this error yourself, commit the result and check that the pre-commit marks "Passed".

See our [contributing](https://github.com/compspi/compspi/blob/master/docs/contributing.rst) guidelines!

## Note on Pull Requests from Forks

Note that PRs from forks of ioSPI outside the compSPI organization (e.g. other than the main [compSPI/ioSPI](https://github.com/compSPI/ioSPI) repo), will fail on tests, due to an authentication feature that is only available on the main compSPI repo. In order to work around this, please make a feature branch off the main[compSPI/ioSPI](https://github.com/compSPI/ioSPI) repo.
  1. `git clone https://github.com/compSPI/ioSPI.git`.
  2. `git branch iospi_new_feature`.
  3. Develop feature.
  4. PR from `compSPI:iospi_new_feature` to `compSPI:master`.

If you already have developed a feature branch on your own fork, then you can PR into a fresh branch off master. Then do another PR from within the compSPI organization to the master branch.
  1. Fork the repo to `your_account`, i.e. `https://github.com/your_account/ioSPI`.
  2. `git clone https://github.com/your_account/ioSPI.git`.
  3. `git branch iospi_new_feature`.
  4. Develop feature.
  5. Make a fresh branch of `compSPI/ioSPI` off of master, e.g. called `compspiorg_iospi_new_feature`.
  6. PR from `your_account:iospi_new_feature` to `compSPI:compspiorg_iospi_new_feature`.
  7. Once merged, PR from `compSPI:compspiorg_iospi_new_feature` to `compSPI:master`.
  8. These tests should not have authentication issues since they are within branches on the compSPI organization. You can continue comitting to `compSPI:compspiorg_iospi_new_feature`, and not touch `your_account:iospi_new_feature`.
