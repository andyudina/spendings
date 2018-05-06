import logging


logger = logging.getLogger(__name__)


class BaseParser(object):
    """
    Base class for parsers.
    Highlevel logic for bills parsing.
    Processes text string
    Every parser should define own logic of parsing items
    information.
    """
    MIN_DATE_WORD_LENGTH = 6 # 2 - year, 1 - month, 1 - day, 2 - stop symbols


    def get_datetime_and_spendings_from_bill(self, bill_text):
        """
        Get datetime when bill was created and information about spendings:
        type, amount. Throws ValueError if date or items can not be found

        Returns dictionary with format:
        {
            'date': '%Y-%m-%d %H:%M:%S',
            'items': [
                {
                    'name': 'item-name [string]',
                    'quantity': 'item-quantity [int]',
                    'amount': 'item-amount [float]'
                }
            ]
        }
        """
        bill_by_lines = [
            line.strip() for line in bill_text.splitlines()
            if line.strip()]
        bill_by_words = [
            word.strip() for word in bill_text.split()]
        return {
            'date': self._find_date(bill_by_words),
            'items': self._find_items(bill_by_lines)
        }

    def _find_date(self, bill_words):
        """
        Find date of the bill.
        Returns date in format '%Y-%m-%d %H:%M:%S'
        """
        from dateutil import parser
        # WARING: 4 sumbols dates without stop symbols can not be used here
        for word in bill_words:
            if len(word) < self.MIN_DATE_WORD_LENGTH:
                logger.debug(
                    'Length of word %s is not enough to be date' % word)
                continue
            try:
                date = parser.parse(
                    word, dayfirst=True)
                return str(date)
            # not date - ok to skip
            except ValueError as e:
                logger.debug(
                    'Word %s is not date: %s' % (word, e))
            except OverflowError as e:
                logger.debug(
                    'Word %s is not date: %s' % (word, e))
        raise ValueError('No date found')

    def _find_items(self, bill_lines):
        """
        Find items of the bill.
        Returns list of items in format:
        [
            {
                'name': 'item-name [string]',
                'quantity': 'item-quantity [int]',
                'amount': 'item-amount [float]'
            }
        ]
        """
        items = []
        # Iterate over pairs of lines
        # Sometimes information about item can be splitted into two lines
        skip_line = False
        for line_index in range(len(bill_lines)):
            # We process pairs of lines
            # in case second line in pair was used
            # together with first line to parse the item
            if skip_line:
                logger.debug(
                    'Skipped line %s '
                    'Used to build previous item' % \
                    bill_lines[line_index])
                skip_line = False
                continue
            lines = bill_lines[line_index: line_index + 2]
            # don't proceed further that total sum line
            if self._is_total_line(lines[0]):
                logger.debug(
                    'Found total line: "%s"' % lines[0])
                break
            item, skip_line = self._process_line(*lines)
            if item:
                items.append(item)
        if not items:
            raise ValueError('No items found')
        return items

    def _process_line(self, line, *args, **kwargs):
        """
        Process bill line.
        Returns parsed item or None and flag that states 
        if next line need to be skipped
        If item is found, line information should be in format:
        {
            'name': 'item-name [string]',
            'quantity': 'item-quantity [int]',
            'amount': 'item-amount [float]'    
        }
        """
        raise NotImplementedError

    def _is_total_line(self, line):
        """
        Check if line has total anount of the check
        """
        return self._get_total_line() in line.lower()

    def _get_total_line(self):
        """
        Return symbol or string, stating that we reach "total"
        section in bill. SHould be defined by each parser
        """
        raise NotImplementedError
