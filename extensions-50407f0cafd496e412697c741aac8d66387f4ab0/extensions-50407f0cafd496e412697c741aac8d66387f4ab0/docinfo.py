#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2012 Jabiertxo Arraiza, jabier.arraiza@marker.es
# Copyright (C) 2016 su_v, <suv-sf@users.sf.net>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""Document information"""

import inkex

from inkex.localization import inkex_gettext as _


class DocInfo(inkex.EffectExtension):
    """Show document information"""

    def effect(self):
        namedview = self.svg.namedview
        self.msg(_(":::SVG document related info:::"))
        self.msg(
            _("version: {}").format(
                self.svg.get("inkscape:version", _("New Document (unsaved)"))
            )
        )
        self.msg(_("width: {}").format(self.svg.viewport_width))
        self.msg(_("height: {}").format(self.svg.viewport_height))
        self.msg(_("viewbox: {}").format(str(self.svg.get_viewbox())))
        self.msg(
            _("document-units: {}").format(
                namedview.get("inkscape:document-units", "None")
            )
        )
        self.msg(_("units: ") + namedview.get("units", "None"))
        self.msg(_("Document has {} guides").format(len(namedview.get_guides())))
        for i, grid in enumerate(namedview.findall("inkscape:grid")):
            self.msg(
                _("Grid number {}: Units: {}").format(i + 1, grid.get("units", "None"))
            )
        if len(namedview.get_pages()) > 1:
            self.msg(_("Document has {} pages").format(len(namedview.get_pages())))
            for i, page in enumerate(namedview.get_pages()):
                self.msg(
                    _("Page number {}: x: {} y: {} width: {} height: {}").format(
                        i + 1,
                        page.get("x"),
                        page.get("y"),
                        page.get("width"),
                        page.get("height"),
                    )
                )
        else:
            self.msg(_("This is a single page document."))


if __name__ == "__main__":
    DocInfo().run()
