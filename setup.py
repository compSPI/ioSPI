"""Create instructions to build the ioSPI package."""

import setuptools

requirements = []

setuptools.setup(
    name="iospi",
    maintainer="Frederic Poitevin",
    version="0.0.1",
    maintainer_email="frederic.poitevin@stanford.edu",
    description="Single particle imaging I/O package",
    long_description=open("README.md", encoding="utf8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/compSPI/ioSPI.git",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
)
