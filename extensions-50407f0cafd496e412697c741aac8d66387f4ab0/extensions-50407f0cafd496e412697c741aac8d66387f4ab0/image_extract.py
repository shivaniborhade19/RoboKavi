#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2005 Aaron Spike, aaron@ekips.org
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
Extract embedded images.
"""

import os
import inkex
from inkex import Image
from inkex.localization import inkex_gettext as _

try:
    from base64 import decodebytes
except ImportError:
    from base64 import decodestring as decodebytes


class ExtractImage(inkex.EffectExtension):
    """Extract images and save to filenames"""

    def add_arguments(self, pars):
        pars.add_argument(
            "-s",
            "--selectedonly",
            type=inkex.Boolean,
            help="Extract only selected images",
            default=True,
        )
        pars.add_argument(
            "--filepath", default="./images/", help="Location to save the images."
        )

    def effect(self):
        elems = (
            self.svg.selection.filter(Image)
            if self.options.selectedonly
            else self.svg.xpath("//svg:image")
        )

        for elem in elems:
            self.extract_image(elem)

    @staticmethod
    def mime_to_ext(mime):
        """Return an extension based on the mime type"""
        # Most extensions are automatic (i.e. extension is same as minor part of mime type)
        part = mime.split("/", 1)[1].split("+")[0]
        return "." + {
            # These are the non-matching ones.
            "svg+xml": ".svg",
            "jpeg": ".jpg",
            "icon": ".ico",
        }.get(part, part)

    def extract_image(self, node):
        """Extract the node as if it were an image."""
        xlink = node.get("xlink:href")
        if not xlink.startswith("data:"):
            return  # Not embedded image data

        # This call will raise AbortExtension if the document wasn't saved
        # and the user is trying to extract them to a relative directory.
        save_to = self.absolute_href(self.options.filepath, default=None)
        # Make the target directory if it doesn't exist yet.
        if not os.path.isdir(save_to):
            os.makedirs(save_to)

        try:
            data = xlink[5:]
            (mimetype, data) = data.split(";", 1)
            (base, data) = data.split(",", 1)
        except ValueError:
            inkex.errormsg(_("Invalid image format found"))
            return

        if base != "base64":
            inkex.errormsg(_("Can't decode encoding: {}").format(base))
            return

        file_ext = self.mime_to_ext(mimetype)

        pathwext = os.path.join(save_to, node.get("id") + file_ext)
        if os.path.isfile(pathwext):
            inkex.errormsg(
                _("Can't extract image, filename already used: {}").format(pathwext)
            )
            return

        self.msg(_("Image extracted to: {}").format(pathwext))

        with open(pathwext, "wb") as fhl:
            fhl.write(decodebytes(data.encode("utf-8")))

        # absolute for making in-mem cycles work
        node.set("xlink:href", os.path.realpath(pathwext))


if __name__ == "__main__":
    ExtractImage().run()
