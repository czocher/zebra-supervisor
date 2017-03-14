# -*- coding: utf-8 -*-

from django.test import TestCase, override_settings

from django.utils.translation import activate

from judge.templatetags.error_code_to_str import error_code_to_str


class TemplatetagsTestCase(TestCase):

    def setUp(self):
        # Disable translation for the tests
        activate('en-en')

    def test_error_code_to_known_codes(self):
        """error_code_to_str should transform known error codes."""

        self.assertTrue('Ok' in error_code_to_str(0))
        self.assertTrue('Abnormal' in error_code_to_str(6))
        self.assertTrue('Floating' in error_code_to_str(8))
        self.assertTrue('Timelimit' in error_code_to_str(9))
        self.assertTrue('Segmentation' in error_code_to_str(11))
        self.assertTrue('Compilation' in error_code_to_str(127))

    def test_error_code_to_str_unknown_codes(self):
        """error_code_to_srt should not transform unknown error codes."""
        self.assertEquals(100, error_code_to_str(100))
        self.assertEquals(200, error_code_to_str(200))
