"""
Test set for finnish checks parser
"""
from django.test import TestCase

from apps.bills.parsers.fi import FIParser


class FIParserTestCase(TestCase):
    """
    Test parsing of different types of checks
    """

    def setUp(self):
        self.parser = FIParser()

    def test_parse_groceries_check(self):
        """
        Validate parsing results for groceries check
        """

    def test_parse_parmacy_check(self):
        """
        Validate parsing results for pharmacy check
        """

    def test_parse_post_office_check(self):
        """
        Validate parsing results for post office check
        """

    def test_parse_department_store_check(self):
        """
        Validate parsing results for department store check
        """

    def test_parse_bakery_check(self):
        """
        Validate parsing results for bakery check
        """
 
