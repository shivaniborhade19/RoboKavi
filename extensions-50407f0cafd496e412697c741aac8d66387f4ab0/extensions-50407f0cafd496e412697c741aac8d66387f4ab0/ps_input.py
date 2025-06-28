#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2008 Stephen Silver
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
#
"""
Simple wrapper around ps2pdf
"""

import sys
import os

import inkex
from inkex.command import call, which


class PostscriptInput(inkex.CallExtension):
    """Load Postscript/EPS Files by calling ps2pdf program"""

    input_ext = "ps"
    output_ext = "pdf"
    multi_inx = True

    def add_arguments(self, pars):
        pars.add_argument("--crop", type=inkex.Boolean, default=False)

    def call(self, input_file, output_file):
        crop = "-dEPSCrop" if self.options.crop else None
        if sys.platform == "win32":
            params = [
                "-q",
                "-P-",
                "-dSAFER",
                "-dNOPAUSE",
                "-dBATCH",
                "-sDEVICE#pdfwrite",
                "-dCompatibilityLevel#1.4",
                crop,
                "-sOutputFile#" + output_file,
                input_file,
            ]
            gs_execs = ["gswin64c", "gswin32c"]
            gs_exec = None
            for executable in gs_execs:
                try:
                    which(executable)
                    gs_exec = executable
                except:
                    pass
            if gs_exec is None:
                if "PYTEST_CURRENT_TEST" in os.environ:
                    gs_exec = "gswin64c"  # In CI, we have neither available,
                    # but there are mock files for the 64 bit version
                else:
                    raise inkex.AbortExtension()
            call(gs_exec, *params)
        else:
            call("ps2pdf", crop, input_file, output_file)


if __name__ == "__main__":
    PostscriptInput().run()
