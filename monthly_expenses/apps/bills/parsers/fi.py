# -*- coding: utf-8 -*-
"""
Parser for finnish checks based on simple regex
"""
import logging
import re

from .base import BaseParser


logger = logging.getLogger(__name__)


class FIParser(BaseParser):
    """
    Parse test checks images with simple structure
    """

    def _process_line(self, line, *args, **kwargs):
        """
        Process bill line
        Returns item or None if item can not be parsed
        If item is found, line information should be in format:
        {
            'item': 'item-name [string]',
            'quantity': 'item-quantity [int]',
            'amount': 'item-amount [float]'    
        }
        """
        if len(args) == 1:
            return self._process_double_lines(line, args[0])
        else:
            return self._process_single_line(line)

    def _process_double_lines(
            self, first_line, second_line):
        """
        Try extract amount, quantity and name from two sequential lines
        """
        try:
            (
                name, 
                first_line_amount, 
                first_line_quantity
            ) = self._parse_first_bill_line(first_line)
        except ValueError:
            logger.exception(
                'Can not parse first line %s' % first_line)
            return None
        second_line_amount = None
        second_line_quantity = None
        try:
            (
                second_line_amount,
                second_line_quantity
            ) = self._parse_second_bill_line(second_line)
        except ValueError as e:
            logger.debug(
                'Falied to parse second line '
                '%s. Original exception: %s' % (second_line, str(e)))
        amount = first_line_amount or second_line_amount
        quantity = second_line_quantity or first_line_quantity
        if not name or not amount or not quantity:
            logger.error(
                'Can not parse lines %s '
                'Result: name - %s, amount - %s, quantity - %s' % (
                        str([first_line, second_line]),
                        name, amount, quantity))
            return None
        return {
            'item': name,
            'amount': amount,
            'quantity': quantity
        }

    def _process_single_line(self, line):
        """
        Parse single line passed
        """
        try:
            (
                name, 
                amount, 
                quantity
            ) = self._parse_first_bill_line(line)
        except ValueError:
            logger.exception(
                'Can not parse first line %s' % line)
            return None
        if not name or not amount or not quantity:
            logger.error(
                'Can not parse line %s' % line)
            return None
        return {
            'item': name,
            'amount': amount,
            'quantity': quantity
        }

    def _parse_first_bill_line(
            self, line):
        """
        Use regex to get amount, quantity and item name
        information from bill
        """
        # Try find name
        name_match = re.search(
            '^([\d ]+)?([a-zA-Z&\s]+)', line)
        if not name_match:
            raise ValueError(
                'Can not find item name. Line %s' % line)
        name = name_match.group(2).strip()
        line_after_name = line.split(name)[-1]
        # if there some not space symbols in the beginning
        # of the left line, we should remove them
        # cause they are probably numeric leftovers of the item name
        # which is ok to skip
        line_after_name = re.sub(r'^[\S]+', '', line_after_name)
        # Try find amount
        amount = self._get_amount(line_after_name)
   
        return (
                name,
                amount,
                1 # quantity - fi checks don't have quantity on the fist line
            )

    def _parse_second_bill_line(self, line):
        """
        Try parse quantity and amount from second bill line
        """
        quantity_match = re.search(
            '^([\d ]+)(kpl|KPL)?', line.strip())
        if not quantity_match:
            raise ValueError(
                'Can not find quantity. Line "%s"' % line)
        quantity = quantity_match.group(1)
        if quantity:
            line = line.split(quantity)[-1]
        amount = self._get_amount(line)
        return (
                amount,
                int(quantity.strip())
            )

    def _get_amount(self, line):
        """
        Extract amount from bill line
        """
        for word in line.split()[::-1]:
            try:
                return float(word.replace(',', '.'))
            except ValueError as e:
                logger.debug(
                    'Word %s does not contain amount. '
                    'Original error: %s' % (word, e))
        return None

    def _is_total_line(self, line):
        """
        Check if line has total anount of the check
        """
        return \
            'yhteensä' in line.lower() or \
            'yhteensa' in line.lower()
