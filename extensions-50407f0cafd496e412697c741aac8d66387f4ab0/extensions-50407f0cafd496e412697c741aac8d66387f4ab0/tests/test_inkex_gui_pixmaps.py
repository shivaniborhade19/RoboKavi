# coding=utf-8
#
# Copyright 2022 Martin Owens <doctormo@geek-2.com>
#
# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>
#
"""
Test pixmap and image handling from various sources.
"""

import os
import sys
import time
import pytest

from inkex.tester import TestCase
from inkex.utils import DependencyError

try:
    from inkex.gui.tester import MainLoopProtection
    from inkex.gui.pixmap import PixmapLoadError, PixmapFilter, OverlayFilter
    from inkex.gui import PixmapManager
except DependencyError:
    PixmapFilter = object
    PixmapManager = None


class NullFilter(PixmapFilter):
    required = ["underpants"]


@pytest.mark.skipif(PixmapManager is None, reason="PyGObject is required")
class GtkPixmapsTest(TestCase):
    """Tests all the pixmaps functionality"""

    def construct_manager(self, **kwargs):
        """Create a gtk app based on some inputs"""
        return type(
            "_PixMan",
            (PixmapManager,),
            {
                "pixmap_dir": self.datadir(),
                "missing_image": kwargs.pop("missing_image", None),
                "default_image": kwargs.pop("default_image", None),
                **kwargs,
            },
        )

    def test_filter(self):
        """Test building filters and errors"""
        null_filter = NullFilter(None, underpants=True)
        self.assertRaises(NotImplementedError, null_filter.filter, "not")

    def test_filter_overlay(self):
        """Test overlay filters"""

        class MyOverlayFilter(OverlayFilter):
            overlay = "application-default-icon"
            placement = (0.25, 0.25)

        pixmaps = self.construct_manager(filters=[MyOverlayFilter])("svg")
        image = pixmaps.get("colors.svg")
        self.assertTrue(image)

        pixmaps._filters[0].set_position(image, 0, 0)

    def test_load_file(self):
        """Test loading a filename"""
        pixmaps = self.construct_manager()("svg")
        self.assertTrue(pixmaps.get("colors.svg"))
        self.assertFalse(pixmaps.get("colors-no-file.svg"))

    def test_size_file(self):
        """Test resizing a file pixmap"""
        pixmaps = self.construct_manager()("svg", size=512, resize_mode=3)
        self.assertTrue(pixmaps.get("colors.svg"))
        self.assertRaises(PixmapLoadError, pixmaps.load_from_name, "no-file.svg")
        self.assertRaises(
            PixmapLoadError,
            pixmaps.load_from_name,
            os.path.join(self.datadir(), "ui", "window-test.ui"),
        )

    def test_load_name(self):
        """Test loading from a Gtk named theme icon"""
        pixmaps = self.construct_manager()()
        self.assertTrue(pixmaps.get("image-missing"))

    def test_load_data_svg(self):
        """Test loading a data svg"""
        pixmaps = self.construct_manager()(size=None, load_size=(128, 128))
        with open(os.path.join(self.datadir(), "svg", "colors.svg"), "r") as fhl:
            self.assertTrue(pixmaps.get(fhl.read()))
        self.assertRaises(PixmapLoadError, pixmaps.load_from_data, "<svg bad")

    def test_load_data_png(self):
        """Test loading a data png"""
        pixmaps = self.construct_manager()()
        with open(os.path.join(self.datadir(), "svg", "img", "green.png"), "rb") as fhl:
            self.assertTrue(pixmaps.get(fhl.read()))

    def test_load_default(self):
        pixmaps = self.construct_manager()()
        self.assertFalse(pixmaps.get(None))
        pixmaps = self.construct_manager(default_image="image-missing")()
        self.assertTrue(pixmaps.get(None))
        pixmaps = self.construct_manager(missing_image="image-missing")()
        self.assertTrue(pixmaps.get("bad-image"))
