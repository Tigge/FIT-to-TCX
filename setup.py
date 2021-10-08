#!/usr/bin/env python
#
# FIT to TCX distutils setup script
#
# Copyright (c) 2012, Gustav Tiger <gustav@tiger.name>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import absolute_import, print_function

from setuptools import setup

try:
    with open('README.md') as file:
        long_description = file.read()
except IOError:
    long_description = ''

setup(name='fit-to-tcx',
      version='0.1',

      description='FIT to TCX',
      long_description=long_description,

      author='Gustav Tiger',
      author_email='gustav@tiger.name',

      packages=['fittotcx'],
      entry_points={
          'console_scripts': ['fittotcx=fittotcx.program:main']
      },

      url='https://github.com/Tigge/FIT-to-TCX',

      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Healthcare Industry',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8'],

      dependency_links=['git+https://github.com/dtcooper/python-fitparse.git#egg=fitparse-1.2.0'],
      install_requires=['lxml', 'fitparse>=1.0.1'],

      test_suite='tests')
