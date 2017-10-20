"""
Utility methods for helping scrapper.
"""

from datetime import datetime
from lxml import html, etree

import re

def cc_to_us(camel_cased):
    """
    Converts a camel case label into underscore format.
    """
    under_scored = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_cased)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', under_scored).lower()

def text_strip(cell):
    """
    Captures the text from a cell and returns a stripped version
    of it.
    """
    return re.sub(r'\s+', ' ', cell.text.lower().replace('\n', '')).strip()

def to_date(text):
    """
    Converts a string into datetime
    """
    if text:
        try:
            return datetime.strptime(re.sub('[^0-9-]', '', text), '%d-%m-%Y')
        except ValueError:
            try:
                return datetime.strptime(re.sub('[^0-9-]', '', text), '%m-%Y')
            except ValueError:
                try:
                    return datetime.strptime(re.sub('[^0-9-]', '', text), '%Y')
                except ValueError:
                    return None
    return None

def xpath_value(root, path, logger=None):
    """
    Method that goes to the defined path inside root and extract
    the text value of that element
    """
    element = root.xpath(path)
    if len(element):
        element = element[0].text
        if logger is not None:
            logger.debug('Value: {}'.format(element))
        return element
    return None

def xpath_html(root, path, logger=None):
    """
    Method that goes to the defined path inside root and extract
    the HTML code of that element
    """
    element = root.xpath(path)
    if len(element):
        element = etree.tostring(element[0], pretty_print=True)
        if logger is not None:
            logger.debug('HTML: {}'.format(element))
        return element
    return None

def process_sources(element):
    """
    Method used to extract a link from an a element
    """
    sources = element.findall('a')
    if len(sources) > 0:
        return ';'.join([s.get('data-content', s.get('href', None)) for s in sources])
    return None
