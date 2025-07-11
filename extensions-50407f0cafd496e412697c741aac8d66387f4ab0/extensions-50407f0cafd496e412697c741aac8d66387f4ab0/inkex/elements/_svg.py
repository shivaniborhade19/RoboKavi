# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 Martin Owens <doctormo@gmail.com>
#                    Thomas Holder <thomas.holder@schrodinger.com>
#                    Sergei Izmailov <sergei.a.izmailov@gmail.com>
#                    Windell Oskay <windell@oskay.net>
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
# pylint: disable=attribute-defined-outside-init
#
"""
Provide a way to load lxml attributes with an svg API on top.
"""

import random
import math

from lxml import etree

from ..css import ConditionalRule
from ..interfaces.IElement import ISVGDocumentElement

from ..deprecated.meta import DeprecatedSvgMixin
from ..units import discover_unit, parse_unit
from ._selected import ElementList
from ..transforms import BoundingBox
from ..styles import StyleSheets

from ._base import BaseElement
from ._meta import StyleElement

if False:  # pylint: disable=using-constant-test
    import typing  # pylint: disable=unused-import


class SvgDocumentElement(DeprecatedSvgMixin, ISVGDocumentElement, BaseElement):
    """Provide access to the document level svg functionality"""

    # pylint: disable=too-many-public-methods
    tag_name = "svg"

    def _init(self):
        self.current_layer = None
        self.view_center = (0.0, 0.0)
        self.selection = ElementList(self)
        self.ids = {}

    def tostring(self):
        """Convert document to string"""
        return etree.tostring(etree.ElementTree(self))

    def get_ids(self):
        """Returns a set of unique document ids"""
        if not self.ids:
            self.ids = set(self.xpath("//@id"))
        return self.ids

    def get_unique_id(self, prefix, size=None):
        """Generate a new id from an existing old_id"""
        ids = self.get_ids()
        if size is None:
            size = max(math.ceil(math.log10(len(ids) or 1000)) + 1, 4)
        new_id = None
        _from = 10**size - 1
        _to = 10**size
        while new_id is None or new_id in ids:
            # Do not use randint because py2/3 incompatibility
            new_id = prefix + str(int(random.random() * _from - _to) + _to)
        self.ids.add(new_id)
        return new_id

    def get_page_bbox(self):
        """Gets the page dimensions as a bbox"""
        return BoundingBox(
            (0, float(self.viewbox_width)), (0, float(self.viewbox_height))
        )

    def get_current_layer(self):
        """Returns the currently selected layer"""
        layer = self.getElementById(self.namedview.current_layer, "svg:g")
        if layer is None:
            return self
        return layer

    def getElement(self, xpath):  # pylint: disable=invalid-name
        """Gets a single element from the given xpath or returns None"""
        return self.findone(xpath)

    def getElementById(
        self, eid, elm="*", literal=False
    ):  # pylint: disable=invalid-name
        """Get an element in this svg document by it's ID attribute"""
        if eid is not None and not literal:
            eid = eid.strip()[4:-1] if eid.startswith("url(") else eid
            eid = eid.lstrip("#")
        return self.getElement(f'//{elm}[@id="{eid}"]')

    def getElementByName(self, name, elm="*"):  # pylint: disable=invalid-name
        """Get an element by it's inkscape:label (aka name)"""
        return self.getElement(f'//{elm}[@inkscape:label="{name}"]')

    def getElementsByClass(self, class_name):  # pylint: disable=invalid-name
        """Get elements by it's class name"""

        return self.xpath(ConditionalRule(f".{class_name}").to_xpath())

    def getElementsByHref(self, eid):  # pylint: disable=invalid-name
        """Get elements by their href xlink attribute"""
        return self.xpath(f'//*[@xlink:href="#{eid}"]')

    def getElementsByStyleUrl(self, eid, style=None):  # pylint: disable=invalid-name
        """Get elements by a style attribute url"""
        url = f"url(#{eid})"
        if style is not None:
            url = style + ":" + url
        return self.xpath(f'//*[contains(@style,"{url}")]')

    @property
    def name(self):
        """Returns the Document Name"""
        return self.get("sodipodi:docname", "")

    @property
    def namedview(self):
        """Return the sp namedview meta information element"""
        return self.get_or_create("//sodipodi:namedview", prepend=True)

    @property
    def metadata(self):
        """Return the svg metadata meta element container"""
        return self.get_or_create("//svg:metadata", prepend=True)

    @property
    def defs(self):
        """Return the svg defs meta element container"""
        return self.get_or_create("//svg:defs", prepend=True)

    def get_viewbox(self):
        """Parse and return the document's viewBox attribute"""
        try:
            ret = [float(unit) for unit in self.get("viewBox", "0").split()]
        except ValueError:
            ret = ""
        if len(ret) != 4:
            return [0, 0, 0, 0]
        return ret

    @property
    def viewbox_width(self) -> float:  # getDocumentWidth(self):
        """Returns the width of the `user coordinate system
        <https://www.w3.org/TR/SVG2/coords.html#Introduction>`_ in user units, i.e.
        the width of the viewbox, as defined in the SVG file. If no viewbox is defined,
        the value of the width attribute is returned. If the height is not defined,
        returns 0."""
        return self.get_viewbox()[2] or self.viewport_width

    @property
    def viewport_width(self) -> float:
        """Returns the width of the `viewport coordinate system
        <https://www.w3.org/TR/SVG2/coords.html#Introduction>`_ in user units, i.e. the
        width attribute of the svg element converted to px"""
        return self.to_dimensionless(self.get("width")) or self.get_viewbox()[2]

    @property
    def viewbox_height(self) -> float:  # getDocumentHeight(self):
        """Returns the height of the `user coordinate system
        <https://www.w3.org/TR/SVG2/coords.html#Introduction>`_ in user units, i.e. the
        height of the viewbox, as defined in the SVG file. If no viewbox is defined, the
        value of the height attribute is returned. If the height is not defined,
        returns 0."""
        return self.get_viewbox()[3] or self.viewport_height

    @property
    def viewport_height(self) -> float:
        """Returns the width of the `viewport coordinate system
        <https://www.w3.org/TR/SVG2/coords.html#Introduction>`_ in user units, i.e. the
        height attribute of the svg element converted to px"""
        return self.to_dimensionless(self.get("height")) or self.get_viewbox()[3]

    @property
    def scale(self):
        """Return the ratio between the viewBox width and the page width"""
        return self._base_scale()

    @property
    def inkscape_scale(self):
        """Returns the ratio between the viewBox width (in width/height units) and the
        page width, which is displayed as "scale" in the Inkscape document
        properties."""

        viewbox_unit = (
            parse_unit(self.get("width")) or parse_unit(self.get("height")) or (0, "px")
        )[1]
        return self._base_scale(viewbox_unit)

    def _base_scale(self, unit="px"):
        """Returns what Inkscape shows as "user units per `unit`" """
        try:
            scale_x = (
                self.to_dimensional(self.viewport_width, unit) / self.viewbox_width
            )
            scale_y = (
                self.to_dimensional(self.viewport_height, unit) / self.viewbox_height
            )
            value = max([scale_x, scale_y])
            return 1.0 if value == 0 else value
        except (ValueError, ZeroDivisionError):
            return 1.0

    @property
    def equivalent_transform_scale(self) -> float:
        """Return the scale of the equivalent transform of the svg tag, as defined by
        https://www.w3.org/TR/SVG2/coords.html#ComputingAViewportsTransform
        (highly simplified)"""
        return self.scale

    @property
    def unit(self):
        """Returns the unit used for in the SVG document.
        In the case the SVG document lacks an attribute that explicitly
        defines what units are used for SVG coordinates, it tries to calculate
        the unit from the SVG width and viewBox attributes.
        Defaults to 'px' units."""
        if not hasattr(self, "_unit"):
            self._unit = "px"  # Default is px
            viewbox = self.get_viewbox()
            if viewbox and set(viewbox) != {0}:
                self._unit = discover_unit(self.get("width"), viewbox[2], default="px")
        return self._unit

    @property
    def document_unit(self):
        """Returns the display unit (Inkscape-specific attribute) of the document"""
        return self.namedview.get("inkscape:document-units", "px")

    @property
    def stylesheets(self):
        """Get all the stylesheets, bound together to one, (for reading)"""
        sheets = StyleSheets(self)
        for node in self.xpath("//svg:style"):
            sheets.append(node.stylesheet())
        return sheets

    @property
    def stylesheet(self):
        """Return the first stylesheet or create one if needed (for writing)"""
        for sheet in self.stylesheets:
            return sheet

        style_node = StyleElement()
        self.defs.append(style_node)
        return style_node.stylesheet()
