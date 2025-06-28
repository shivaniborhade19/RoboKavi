# coding=utf-8
from dxf_outlines import DxfOutlines
from inkex.tester import ComparisonMixin, InkscapeExtensionTestMixin, TestCase
from inkex.tester.filters import WindowsTextCompat
from inkex.elements._parser import load_svg

from inkex.utils import AbortExtension


class DFXOutlineBasicTest(ComparisonMixin, InkscapeExtensionTestMixin, TestCase):
    effect_class = DxfOutlines
    comparisons = [
        (),
        ("--id=p1", "--id=r3"),
        ("--POLY=true",),
        ("--ROBO=true",),
    ]
    compare_filters = [WindowsTextCompat()]


class DXFDeeplyNestedTest(TestCase):
    """Check that a deeply nested SVG raises an AbortExtension"""

    @staticmethod
    def create_deep_svg(amount):
        """Create a very deep svg and test getting ancestors"""
        svg = '<svg xmlns="http://www.w3.org/2000/svg">'
        for i in range(amount):
            svg += f'<g id="{i}">'
        svg = load_svg(svg + ("</g>" * amount) + "</svg>")
        return svg

    def test_deeply_nested(self):
        "Run test"
        ext = DxfOutlines()
        ext.parse_arguments([])
        ext.document = self.create_deep_svg(1500)
        ext.svg = ext.document.getroot()
        with self.assertRaisesRegex(AbortExtension, "Deep Ungroup"):
            ext.effect()
