"""Test Plotter extension"""
import pytest
import sys
from plotter import Plot
from inkex.tester import ComparisonMixin, TestCase
from inkex.tester.filters import CompareReplacement


@pytest.mark.skipif(sys.platform == "win32", reason="termios not available on Windows")
class TestPlotter(ComparisonMixin, TestCase):
    """Test the plotter extension"""

    stderr_output = True
    effect_class = Plot
    compare_filter_save = True
    compare_filters = [CompareReplacement((";", "\n"))]
    old_defaults = (
        "--serialFlowControl=0",
        "--force=24",
        "--speed=20",
        "--orientation=90",
    )
    comparisons = [
        ("--serialPort=[test]",) + old_defaults,  # HPGL
        ("--serialPort=[test]", "--commandLanguage=DMPL") + old_defaults,
        ("--serialPort=[test]", "--commandLanguage=KNK") + old_defaults,
    ]
