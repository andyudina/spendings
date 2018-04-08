"""
Test parser based on simple regex
"""
import logging

from .base import BaseParser


logger = logging.getLogger(__name__)


class TestParser(BaseParser):
    """
    Parse test check images with simple structure
    """

    def _process_line(self, line, **kwargs):
        """
        Process bill line
        Returns flag, that states if item information found
        and line information.
        If item is found, line information should be in format:
        {
            'item': 'item-name [string]',
            'quantity': 'item-quantity [int]',
            'amount': 'item-amount [float]'    
        }
        """
        try:
            item = self._get_item_from_line(line)
            return True, item
        except ValueError as e:
            logger.debug(
                'Line "%s" does not have information about bill items. '
                'Original error: %s' % (line, e))
            return False, None

    def _get_item_from_line(self, line):
        """
        Try to parse item from bill line.
        Raise ValueError if no item found
        """
        import re
        match = re.search('^([a-zA-Z\s]+)([\d]+)', line)
        if not match:
            raise ValueError('Can not find item name and quantity')
        # Currently only one currency is supported (EUR)
        item = match.group(1).strip()
        quantity = int(match.group(2))
        # Find amount in last part of line
        # Assume that it's the last value in line
        amount = None
        line_by_words = line.split()
        for word in line_by_words[::-1]:
            try:
                amount = float(word.replace(',', '.'))
                break
            except ValueError as e:
                logger.debug(
                    'Word %s does not contain amount. '
                    'Original error: %s' % (word, e))
        if amount is None:
            raise ValueError('Amount not found for item')
        return {
            'item': item,
            'quantity': quantity,
            'amount': amount
        }

    def _get_total_line(self):
        """
        Return symbol or string, stating that we reach "total"
        section in bill. SHould be defined by each parser
        """
        return 'total'
