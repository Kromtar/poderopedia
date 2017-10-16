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

# constant values
PODEROPEDIA_BASE_URL = 'http://www.poderopedia.org'
PODEROPEDIA_INIT_URLS = [
    PODEROPEDIA_BASE_URL + '/cl',
    PODEROPEDIA_BASE_URL + '/cl/directorio/general/persona'
]
PODEROPEDIA_DIRECTORIO_URL = PODEROPEDIA_BASE_URL + '/poderopedia/directorio/'
PODEROPEDIA_PERSONA_PATH = 'service_personselect_letter.load/0/{}/false/{}/service_persona'
PODEROPEDIA_PERSONA_ELEMENT = 'service_persona'
PODEROPEDIA_PERSONA_LOCATION = PODEROPEDIA_BASE_URL + '/cl/directorio/general/persona'
PODEROPEDIA_PERSONA_REF = PODEROPEDIA_BASE_URL + '/cl/directorio/general/persona'

PODEROPEDIA_COMPANY_PATH = 'service_empresaselect_letter.load/0/{}/false/{}/service_empresa'

def cc_to_us(name):
    """
    Converts a camel case label into underscore format.
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def text_strip(cell):
    """
    Captures the text from a cell and returns a stripped version
    of it.
    """
    return re.sub('\s+', ' ', cell.text.lower().replace('\n','')).strip()

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

class PoderopediaRequester(object):
    """
    Base class for requests to the poderopedia website
    """

    def __init__(self):
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.8,es;q=0.6',
            'DNT': '1',
            'Host': 'www.poderopedia.org',
            'Referer': PODEROPEDIA_PERSONA_REF,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
            'web2py-component-element': PODEROPEDIA_PERSONA_ELEMENT,
            'web2py-component-location': PODEROPEDIA_PERSONA_LOCATION,
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.logger = logging.getLogger('poderopedia')
        self.logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)
        self.parser = etree.HTMLParser(encoding='utf-8')


class PoderopediaScrapper(PoderopediaRequester):

    def __init__(self):
        super(PoderopediaScrapper, self).__init__()
        self.engine = create_engine("mysql+pymysql://poder:0p3d14@192.168.0.105/poderopedia?charset=utf8")
        meta = MetaData()
        meta.reflect(bind = self.engine)
        self.person_table = meta.tables['person']
        self.company_table = meta.tables['company']
        self.connection_table = meta.tables['connection']
        self.connection = self.engine.connect()
        self.session = None

    def __xpath_value(self, root, path):
        element = root.xpath(path)
        if element:
            element = element[0].text
            self.logger.debug('Data: {}'.format(element))
            return element
        return None

    def __xpath_html(self, root, path):
        element = root.xpath(path)
        if element:
            element = etree.tostring(element[0], pretty_print=True)
            self.logger.debug('Profile: {}'.format(element))
            return element
        return None

    def __process_source(self, element):
        source = element.find('a')
        if source is not None:
            return element.get('data-content')
        return None

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
                    response = self.session.get(elements_url) #, headers=self.headers)
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

    def persons(self):
        self.elements('persons')

    def companies(self):
        self.elements('companies')

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

    def process_persons(self, persons):
        """
        Crawl the information of people that is available at the website.
        """
        self.process_elements(persons, self.person_table, self.extract_person, ['personal_data', 'family', 'couple', 'friend', 'classmate', 'advisor', 'organization'])

    def process_companies(self, companies):
        """
        Crawl the information of companies that is available at the website.
        """
        self.process_elements(persons, self.company_table, self.extract_company, ['personal_data', 'person', 'organization'])

    def extract_person(self, root):
        """
        Extracts all the information of a person existing in the website.
        """
        person = {}
        info = root.xpath('.//li/h4/a')
        if info:
            link = info[0].get('href', None)
            name = info[0].get('title', None)
            if link and name:
                stmt = select([func.count(self.person_table.c.idperson)]).where(self.person_table.c.path == link)
                results = self.connection.execute(stmt).fetchall()
                if results[0][0] > 0:
                    self.logger.debug('{} already exists'.format(name))
                    return None
                self.logger.debug('Querying {1}: {0}'.format(link, name))
                response = self.session.get(PODEROPEDIA_BASE_URL + link)
                content = response.content
                html_tree = etree.HTML(content, parser=self.parser)
                connections = html_tree.xpath('//div[@id="conexiones"]')
                if connections:
                    personal_data = self.extract_personal_data(connections[0])
                    person['personal_data'] = personal_data if personal_data else {}
                    person['personal_data']['path'] = link

                    family = self.extract_relatives(connections[0])
                    person['family'] = family if family else []
                    for item in person['family']:
                        item.update({'source_path': link})

                    couple = self.extract_couples(connections[0])
                    person['couple'] = couple if couple else []
                    for item in person['couple']:
                        item.update({'source_path': link})

                    friend = self.extract_friendship(connections[0])
                    person['friend'] = friend if friend else []
                    for item in person['friend']:
                        item.update({'source_path': link})

                    classmate = self.extract_classmates(connections[0])
                    person['classmate'] = classmate if classmate else []
                    for item in person['classmate']:
                        item.update({'source_path': link})

                    advisor = self.extract_advisors(connections[0])
                    person['advisor'] = advisor if advisor else []
                    for item in person['advisor']:
                        item.update({'source_path': link})

                    organization = self.extract_organizations(connections[0])
                    person['organization'] = organization if organization else []
                    for item in person['organization']:
                        item.update({'source_path': link})
        return person

    def extract_company(self, root):
        """
        Extracts all the information of an company existing in the website.
        """
        company = {}
        info = root.xpath('.//li/h4/a')
        if info:
            link = info[0].get('href', None)
            name = info[0].get('title', None)
            if link and name:
                stmt = select([func.count(self.company_table.c.path)]).where(self.company_table.c.path == link)
                results = self.connection.execute(stmt).fetchall()
                if results[0][0] > 0:
                    self.logger.debug('{} already exists'.format(name))
                    return None
                self.logger.debug('Querying {1}: {0}'.format(link, name))
                response = self.session.get(PODEROPEDIA_BASE_URL + link)
                content = response.content
                html_tree = etree.HTML(content, parser=self.parser)
                connections = html_tree.xpath('//div[@id="conexiones"]')
                if connections:
                    company_data = self.extract_personal_data(connections[0])
                    company['company_data'] = company_data if company_data else {}
                    company['company_data']['path'] = link

                    person = self.extract_persons(connections[0])
                    company['person'] = person if person else []
                    for item in company['person']:
                        item.update({'source_path': link})

                    organization = self.extract_participation(connections[0])
                    company['organization'] = organization if organization else []
                    for item in company['organization']:
                        item.update({'source_path': link})
        return company

    def extract_personal_data(self, root):
        """
        Extracts the personal information of a person existing in the website.
        """
        personal_data = {}
        self.logger.debug('Extracting personal information')

        personal_data['date_of_birth'] = to_date(self.__xpath_value(root, '//h5[@class="perfil-details"]'))
        personal_data['abstract'] = self.__xpath_value(root, '//p[@class="perfil-details"]')
        personal_data['last_update'] = to_date(self.__xpath_value(root, '//span[@class="actualizado"]'))

        rows = root.xpath('.//*[@id="collapse1"]/div/form/table/tr')
        for row in rows:
            label = row.xpath('.//td[@class="w2p_fl"]/label')
            if not label:
                continue
            key = label[0].get('for', None)
            idx = key.index('_') + 1
            key = cc_to_us(key[idx:])
            value = self.__xpath_value(row, './/td[@class="w2p_fw"]')
            personal_data[key] = value

        personal_data['profile'] = self.__xpath_html(root, '//div[@id="perfil"]')
        return personal_data

    def extract_relatives(self, root):
        """
        Extracts the relatives of a person existing in the website.
        """
        return self.extract_data(root, '//div[@id="familiy"]', 'family')

    def extract_couples(self, root):
        """
        Extracts the information of couples of a person existing in the website.
        """
        return self.extract_data(root, '//div[@id="conyuge"]', 'couple')

    def extract_friendship(self, root):
        """
        Extracts the information of friends and close people
        of a person existing in the website.
        """
        return self.extract_data(root, '//div[@id="P2P"]', 'friend')

    def extract_classmates(self, root):
        return self.extract_data(root, '//div[@id="P2P_comp"]', 'classmate')

    def extract_advisors(self, root):
        return self.extract_data(root, '//div[@id="P2P_asesor"]', 'advisor')

    def extract_organizations(self, root):
        return self.extract_data(root, '//div[@id="P2O"]', 'organization')

    def extract_participation(self, root):
        return self.extract_data(root, '//div[@id="O2O"]', 'organization')

    def extract_persons(self, root):
        return self.extract_data(root, '//div[@id="P2O"]', 'person')

    def extract_data(self, root, path, tag):
        data = []
        element = root.xpath(path)
        if element:
            url = PODEROPEDIA_BASE_URL + element[0].get('data-w2p_remote', None)
            if url:
                self.logger.debug('Querying {} from {}'.format(tag, url))
                try:
                    response = self.session.get(url)
                    response.raise_for_status()
                    content = response.content
                    html_tree = etree.HTML(content, parser=self.parser)
                    if html_tree is None:
                        return data
                    rows = html_tree.xpath('.//*[starts-with(@id, "collapse")]/div/table/tr')
                    for row in rows:
                        target = target_name = target_path = relationship = None
                        when = where = where_name = where_path = source = None
                        row_id = row.get('id', '')
                        cells = row.getchildren()
                        idx = 0
                        while idx < len(cells) - 1:
                            try:
                                cell_text = text_strip(cells[idx])
                            except AttributeError:
                                cell_text = ''
                            if cell_text == 'con' or cell_text == 'de':
                                idx = idx + 1
                                target = cells[idx].find('a')
                                if target is not None:
                                    target_path = target.get('href', None)
                                    target_name = text_strip(target)
                            elif cell_text == 'es' or cell_text == 'fue':
                                when = cell_text
                                idx = idx + 1
                                relationship = text_strip(cells[idx])
                            elif cell_text == 'por':
                                idx = idx + 1
                                relationship = text_strip(cells[idx])
                                idx = idx + 1
                                where = cells[idx].find('a')
                                if where is not None:
                                    where_path = where.get('href', None)
                                    where_name = text_strip(where)
                            elif cell_text == 'en':
                                idx = idx - 1
                                relationship = text_strip(cells[idx])
                                idx = idx + 2
                                target = cells[idx].find('a')
                                if target is not None:
                                    target_path = target.get('href', None)
                                    target_name = text_strip(target)
                            elif cell_text.startswith('desde'):
                                when = cell_text
                            elif 'es pasado' in cell_text:
                                when = cell_text
                            else:
                                try:
                                    ignore = int(cell_text)
                                    when = cell_text
                                except ValueError:
                                    potential_date = cell_text.split(' ')[0]
                                    try:
                                        ignore = datetime.strptime(potential_date, '%d-%m-%Y')
                                        when = cell_text
                                    except ValueError:
                                        try:
                                            ignore = datetime.strptime(potential_date, '%m-%Y')
                                            when = cell_text
                                        except ValueError:
                                            pass
                            idx = idx + 1
                        source = self.__process_source(cells[idx])
                        entry = {
                            'type': tag,
                            'target_path': target_path,
                            'relationship': relationship,
                            'when': when,
                            'where': '{}[{}]'.format(where_name, where_path)
                                     if where is not None else None,
                            'source': source
                        }
                        data.append(entry)
                        self.logger.debug('{}: {}'.format(tag, entry))
                except (requests.exceptions.HTTPError, etree.ParserError):
                    self.logger.info('Something bad happened', exc_info=True)
        return data

def main():
    """
    Main function.
    Called when the script is called directly from cmd line.
    """
    scrapper = PoderopediaScrapper()
    scrapper.setup()
    #scrapper.persons()
    scrapper.companies()

if __name__ == '__main__':
    main()

