"""
Module to crawl the poderopedia website.
"""

from datetime import datetime
from random import randint
from time import sleep

import logging
import re
import string

from lxml import html, etree
from sqlalchemy import MetaData, Table, create_engine, exists, func, select

import requests

from utils import cc_to_us, to_date, text_strip, xpath_value, xpath_html, process_source

# constant values
PODEROPEDIA_BASE_URL = 'http://www.poderopedia.org'
PODEROPEDIA_INIT_URLS = [
    PODEROPEDIA_BASE_URL + '/cl',
    PODEROPEDIA_BASE_URL + '/cl/directorio/general/persona'
]
PODEROPEDIA_DIRECTORIO_URL = PODEROPEDIA_BASE_URL + '/poderopedia/directorio/'

PODEROPEDIA_PERSONA_PATH = 'service_personselect_letter.load/0/{}/false/{}/service_persona'
PODEROPEDIA_COMPANY_PATH = 'service_empresaselect_letter.load/0/{}/false/{}/service_empresa'

class PoderopediaRequester(object):
    """
    Base class for requests to the poderopedia website
    """

    def __init__(self):
        self.logger = logging.getLogger('poderopedia')
        self.logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)
        self.parser = etree.HTMLParser(encoding='utf-8')


class PoderopediaScrapper(PoderopediaRequester):
    """
    Base poderopedia.org scrapper.
    """

    def __init__(self):
        super(PoderopediaScrapper, self).__init__()
        self.engine = create_engine("mysql+pymysql://poder:0p3d14@192.168.0.105/poderopedia?charset=utf8")
        self.meta = MetaData()
        self.meta.reflect(bind = self.engine)
        self.connection_table = meta.tables['connection']

    def setup(self):
        """
        Creates a session to interact with the website.
        Basically it requests the homepage to store a Cookie for the session.
        """
        if self.session is None:
            self.session = requests.Session()
            for url in PODEROPEDIA_INIT_URLS:
                self.session.get(url)

    def elements(self, target):
        """
        Crawl the information of people that is available at the website.
        """
        if target == 'persons':
            url = (PODEROPEDIA_DIRECTORIO_URL + PODEROPEDIA_PERSONA_PATH)
        elif target == 'companies':
            url = (PODEROPEDIA_DIRECTORIO_URL + PODEROPEDIA_COMPANY_PATH)
        for char in string.ascii_lowercase:
            idx = 0
            while True:
                elements_url = url.format(idx, char)
                try:
                    response = self.session.get(elements_url)
                    response.raise_for_status()
                    content = response.content
                    html_tree = etree.HTML(content, parser=self.parser)
                    elements = html_tree.xpath('//ul[@class="faces-ul"]/li/ul[@class="info"]')
                    if not elements:
                        self.logger.info('finished with letter {}'.format(char))
                        break
                    if target == 'persons':
                        self.process_persons(elements)
                    elif target == 'companies':
                        self.process_companies(elements)
                    idx = idx + 1
                    sleep(randint(1, 10))
                except requests.exceptions.HTTPError:
                    self.logger.info('Something bad happened', exc_info=True)
                    self.logger.info('finished with letter {}'.format(char))
                    break

    def process_elements(self, elements, table, method, tags):
        """
        Crawl the information of elements that are available at the website.
        """
        for element in elements:
            full_information = method(element)
            if not full_information:
                continue
            trans = self.connection.begin()
            try:
                element_data = full_information.get(tags[0], None)
                if not element_data:
                    trans.rollback()
                    continue
                self.logger.debug('Inserting information {}'.format(element_data))
                self.connection.execute(
                    table.insert(),
                    [element_data]
                )
                for tag in tags[1:]:
                    tag_data = full_information.get(tag, [])
                    if tag_data:
                        self.logger.debug('Inserting {} {}'.format(tag, tag_data))
                        self.connection.execute(
                            self.connection_table.insert(),
                            tag_data
                        )
                trans.commit()
            except:
                trans.rollback()
                raise
            sleep(randint(1, 10))

    def extract_element_data(self, root):
        """
        Extracts the information of an element existing in the website.
        """
        element_data = {}
        self.logger.debug('Extracting personal information')

        element_data['date_of_birth'] = to_date(xpath_value(root, '//h5[@class="perfil-details"]'))
        element_data['abstract'] = xpath_value(root, '//p[@class="perfil-details"]')
        element_data['last_update'] = to_date(xpath_value(root, '//span[@class="actualizado"]'))

        rows = root.xpath('.//*[@id="collapse1"]/div/form/table/tr')
        for row in rows:
            label = row.xpath('.//td[@class="w2p_fl"]/label')
            if not label:
                continue
            key = label[0].get('for', None)
            idx = key.index('_') + 1
            key = cc_to_us(key[idx:])
            value = xpath_value(row, './/td[@class="w2p_fw"]')
            element_data[key] = value

        element_data['profile'] = xpath_html(root, '//div[@id="perfil"]')
        return element_data

