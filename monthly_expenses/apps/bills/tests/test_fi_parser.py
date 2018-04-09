# -*- coding: utf-8 -*-
"""
Test set for finnish checks parser
"""
from unittest import skip

from django.test import TestCase

from apps.bills.parsers.fi import FIParser


class FIParserTestCase(TestCase):
    """
    Test parsing of different types of checks
    """

    def setUp(self):
        self.parser = FIParser()
        self.maxDiff = True

    def compare_parsing_result_and_expected_result(
            self, check_text, expected_result):
        """
        Helper to validate parsing results of 
        passed text vs expected_result
        """
        result = self.parser.\
            get_datetime_and_spendings_from_bill(check_text)
        self.assertDictEqual(
            result, expected_result)

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
        EXPECTED_RESULT = {
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
            }
        self.compare_parsing_result_and_expected_result(
            CHECK, EXPECTED_RESULT)

    def test_parse_parmacy_check(self):
        """
        Validate parsing results for pharmacy check
        """
        CHECK = """
                TOOLON APTEEKI
                KAMPIN KESKUS
            KAMPINKUJA 2, 00100 HKI
               Puh (00) 00 00 00
           MA-PE 0-0, LA 0-0, SU 12-16

        03.04.2018 00:00:00   KASS1    RE

        SALUS FLORADIX 500    V3    26.21
        ---------------------------------
        Yhteensä                    26.21
        Maksukortti                 26.21

        Alv        veroton vero    veroll
        V3 14.00%    22.99 3.22     26.21
        Yhteensä     22.99 3.22     26.21

        CARD TRANSACTION

        Card:                  MASTERCARD

        Creadit/Charge          26.21 EUR

                       KIITOS!
        """
        EXPECTED_RESULT = {
            'date': '2018-04-03 00:00:00',
            'items': [
                {
                    'item': 'SALUS FLORADIX',
                    'quantity': 1,
                    'amount': 26.21
                }
            ]

        }
        self.compare_parsing_result_and_expected_result(
            CHECK, EXPECTED_RESULT)

    def test_parse_post_office_check(self):
        """
        Validate parsing results for post office check
        """
        CHECK = """
        Posti Oy
        Posti Ab
        00000 HELSINKI
        00000 HELSINGFORS
        Y-0000000-9
        ---------------------------------
        Kavikekuori
            1   x   1.80         1.80 * F
        Postimerkki 2.10€
            1   x   2.10         2.10   9
                           -----------
        YHTEENSÄ              3.90

        CARD TRANSACTION

        Card                   MASTERCARD
        PayPass Contactless
        ---------------------------------
        26/03/2018 00:00 RQt
        """
        EXPECTED_RESULT = {
            'date': '2018-03-26 00:00:00',
            'items': [
                {
                    'item': 'Kavikekuori',
                    'quantity': 1,
                    'amount': 1.8,
                },
                {
                    'item': 'Postimerkki',
                    'quantity': 1,
                    'amount': 2.1,
                }
            ]
        }
        self.compare_parsing_result_and_expected_result(
            CHECK, EXPECTED_RESULT)

    def test_parse_department_store_check(self):
        """
        Validate parsing results for department store check
        """
        CHECK = """
        PRISMA MALMINTORI, puhelin 000 00 00000
        HOK-Elanto Liiketoiminta Oy, 0000000-3
            Aoinna ma-la 7-23 ja su 07-23
        B KB M000551/7654   00:00    31-03-2018

        DRY ROASTED PEANUTS                1.15
        SEASALT&CIDERINEG CHIPS            1.79
        MUSTIKKAMEHU                       1.75
        ROASTED ALMONDS                    1.69
                                         ------
        YHTEENSÄ                           8.07
        CARD TRANSACTION

        Card:                        Mastercard                                 
        """
        EXPECTED_RESULT = {
            'date': '2018-03-31 00:00:00',
            'items': [
                {
                    'item': 'DRY ROASTED PEANUTS',
                    'quantity': 1,
                    'amount': 1.15
                },
                {
                    'item': 'SEASALT&CIDERINEG CHIPS',
                    'quantity': 1,
                    'amount': 1.79
                },
                 {
                    'item': 'MUSTIKKAMEHU',
                    'quantity': 1,
                    'amount': 1.75
                },
                {
                    'item': 'ROASTED ALMONDS',
                    'quantity': 1,
                    'amount': 1.69
                },               
            ]
        }
        self.compare_parsing_result_and_expected_result(
            CHECK, EXPECTED_RESULT)

    def test_parse_bakery_check(self):
        """
        Validate parsing results for bakery check
        """
        CHECK = """
        Kanniston leipomo  Paiväys  28.3.2018
        Testkatu 00           AIka   00:00:00
        00000 HELSINKI      Kuitti   11111111
        Puh 000 000000       Kassa     KASSA0
        Kerta-asiakas       Y-tunn  0000000-0

        1   Ruisleipa iso
            1 kpl 3.80EUR   Yht      3.80 EUR
        Verton                       3.33 EUR
        Alv 14%                      0.47 EUR

        Yhteensä                     3.80 EUR


        Teitä paiveli: Myyjä 1
            Tervetuloa uudellen II


        EXPLANATION PURCHASE
        CARD Mastercard
        USAGE: CREDIT CARD
        ----------------------------
        CHARGE    3.80 EUR
        ----------------------------
        CUSTOMER RECEIPT 28.03.2018 00:00:00
        """
        EXPECTED_RESULT = {
           'date': '2018-03-28 00:00:00',
           'items': [
               {
                   'item': 'Ruisleipa iso',
                   'quantity': 1,
                   'amount': 3.8
               },
           ]
        }
        self.compare_parsing_result_and_expected_result(
            CHECK, EXPECTED_RESULT) 
