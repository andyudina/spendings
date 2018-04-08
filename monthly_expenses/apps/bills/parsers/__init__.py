"""
Pluggable bills parsers
"""
import logging

from .test import TestParser


logger = logging.getLogger(__name__)
__PARSERS = {
    'test_parser': TestParser(),
    'default': TestParser()
}

def load_parser(name):
    """
    Helper to load parser by name
    Returns default parser if requested parser is not found
    """
    try:
        return __PARSERS[name]
    except KeyError:
        logger.exception(
            'Parser %s could not be found' % name)
        return __PARSERS['default']
