# FIT to TCX tests
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

from __future__ import absolute_import, division, print_function

import fittotcx.program as f2t
import unittest
import glob
import lxml.etree

from fitparse import FitParseError


class Simple(unittest.TestCase):
    def test_convert_check_results(self):
        converted = f2t.documenttostring(f2t.convert("tests/test.fit"))
        with open("tests/test.tcx") as tcx:
            result = f2t.documenttostring(lxml.etree.parse(tcx))
        self.assertEqual(converted, result)

    def test_convert_check_success(self):
        for fn in glob.glob("python-fitparse/tests/files/*.fit"):
            with self.subTest(fn):
                try:
                    f2t.convert(fn)
                except FitParseError:
                    # If fitparse can't parse it, it's not our fault
                    pass
