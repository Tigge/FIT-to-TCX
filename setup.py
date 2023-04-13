# This setup.py is just a shim to allow local installation from source
# ("pip install .") to continue working with setuptools<61.0.0.
#
# setuptools(>=61.0.0) adds standalone support for installation from
# pyproject.toml only, with no setup.py shim needed (see
# https://drivendata.co/blog/python-packaging-2023)

import setuptools

if __name__ == '__main__':
    setuptools.setup()