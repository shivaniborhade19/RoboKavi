# coding=utf-8

import os
from image_extract import ExtractImage
from inkex.tester import ComparisonMixin, InkscapeExtensionTestMixin, TestCase


class ExtractImageBasicTest(ComparisonMixin, InkscapeExtensionTestMixin, TestCase):
    stderr_protect = False
    effect_class = ExtractImage
    compare_file = "svg/images.svg"
    compare_file_extension = "png"
    comparisons = [
        ("--selectedonly=False",),
        ("--selectedonly=True", "--id=embeded_image01"),
    ]

    def test_all_comparisons(self):
        """Images are extracted to a file directory"""
        for args in self.comparisons:
            args += ("--filepath={}/".format(self.tempdir),)
            self.assertCompare(self.compare_file, None, args, "embeded_image01.png")
