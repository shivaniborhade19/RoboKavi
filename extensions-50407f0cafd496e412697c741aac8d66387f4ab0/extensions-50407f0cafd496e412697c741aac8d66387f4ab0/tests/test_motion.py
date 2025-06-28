# coding=utf-8
from motion import Motion
from inkex.tester import ComparisonMixin, TestCase
from inkex.tester.filters import CompareNumericFuzzy, CompareWithPathSpace


class MotionBasicTest(ComparisonMixin, TestCase):
    effect_class = Motion
    compare_filters = [CompareNumericFuzzy(), CompareWithPathSpace()]
    comparisons = [
        ("--id=c3", "--id=p2"),
    ]


class MotionSubpathsTest(ComparisonMixin, TestCase):
    """Tests the motion extension on paths with (a) transforms and (b) multiple closed subpaths
    (b): see https://gitlab.com/inkscape/extensions/-/issues/266"""

    compare_file = "svg/motion_tests.svg"
    effect_class = Motion
    compare_filters = [CompareNumericFuzzy(), CompareWithPathSpace()]
    comparisons = [
        (
            "--magnitude=2",
            "--angle=45",
            "--fillwithstroke=True",
            "--id=path23053",
            "--id=path28636",
        )
    ]
