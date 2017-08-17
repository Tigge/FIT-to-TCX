FIT to TCX
==========

[![Travis branch](https://img.shields.io/travis/Tigge/FIT-to-TCX/master.svg)](https://travis-ci.org/Tigge/FIT-to-TCX)
[![Coveralls branch](https://img.shields.io/coveralls/Tigge/FIT-to-TCX/master.svg)](https://coveralls.io/r/Tigge/FIT-to-TCX?branch=master)

Requirements
------------

- python-fitparse -- A library to parse FIT files by David Cooper. You can get
  it from GitHub at <https://github.com/dtcooper/python-fitparse>.

  This library is marked as a dependency so using the installation instructions
  below should bring in this if you don't have it.

- python-lxml -- A library for reading and writing XML files. It uses the
  C libraries libxml2 and libxslt.

  This package *should* be available through your packaging system,
  so depending on your operating system you should be able to use
  `apt-get install python-lxml`, `yum install python-lxml` or similar.

  This library is marked as a dependency so using the installation instructions
  below should bring in this if you don't have it.

Installation
------------

Run `sudo python setup.py install` to install FIT to TCX. This will install
an `fittotcx` binary in `/usr/bin` or similar.

Usage
-----

Usage: `fittotcx FILE`

This program takes a FIT file and converts it into an TCX file and output
the result to the standard output. To save the result to a file, just pipe
the output to a file with `fittotcx filename.fit > filename.tcx`


Batch usage
-----------

Usage: `./batch.sh FILES`

This command takes a series of FIT files and converts it into TCX and outputs
the TCX files to the same directory as the FIT files is located in.  For
example, if you have your FIT files in a directory called Workouts in your home
directory, calling `./batch.sh ~/Workouts/*.fit` will convert all your files
at the same time.

