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
        self.maxDiff = True

    def test_parse_groceries_check(self):
        """
        Validate parsing results for groceries check
        """
        CHECK = """
        ALEPA HELSINGINKATU, puhelin 000 0000000
         HOK-ELanto Liiketominta Oy,   1111111-3

        2 K2 M000030/0440 20:00       06-06-2018

        HEAT&EAT MOROCCAN FALAFEL           3.35
        NECTARINE RASIA ALPINE              2.85
        RAJEUUSTO PEHMEA                    4.17
            3 KPL      1.39 EUR/KPL
        BANAANI CHIQUITA                    1.67
            1.050 KG   1.59 EUR/KG
        ----------------------------------------
        YHTEENSA                           29.30
        CARD TRANSACTION

        CARD:                         Mastercard

        Credit/Charge:                     29.33



        Bonus siirtyu digiailkaan!
        Lataa S-mobiili
        s-mobiili.fi
        """
        result = self.parser.\
            get_datetime_and_spendings_from_bill(CHECK)
        self.assertDictEqual(
            result, {
                'date': '2018-06-06 00:00:00',
                'items': [
                    {
                        'item': 'HEAT&EAT MOROCCAN FALAFEL',
                        'amount': 3.35,
                        'quantity': 1
                    },
                    {
                        'item': 'NECTARINE RASIA ALPINE',
                        'amount': 2.85,
                        'quantity': 1
                    },
                    {
                        'item': 'RAJEUUSTO PEHMEA',
                        'amount': 4.17,
                        'quantity': 3
                    },
                    {
                        'item': 'BANAANI CHIQUITA',
                        'amount': 1.67,
                        'quantity': 1
                    },
                ]
            })

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
 
