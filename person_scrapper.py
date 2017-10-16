"""
Module to crawl the persons available at the poderopedia website.
"""

from datetime import datetime
from lxml import html, etree
from sqlalchemy import MetaData, Table, create_engine, exists, func, select

import requests

from scrapper import PoderopediaScrapper
from utils import cc_to_us, to_date, text_strip, xpath_value, xpath_html, process_source

class PoderopediaPersonScrapper(PoderopediaScrapper):
    """
    Scrapper for the persons that are listed at poderopedia.
    """

    def __init__(self):
        super(PoderopediaPersonScrapper, self).__init__()
        self.person_table = self.meta.tables['person']
        self.connection = self.engine.connect()
        self.session = None

    def persons(self):
        """
        Method to retrieve the list of persons in the current page
        """
        self.elements('persons')

    def process_persons(self, persons):
        """
        Crawl the information of people that is available at the website.
        """
        self.process_elements(
            persons,
            self.person_table,
            self.extract_person,
            ['personal_data', 'family', 'couple', 'friend', 'classmate', 'advisor', 'organization']
        )

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
                stmt = select(
                        [func.count(self.person_table.c.idperson)]
                    ).where(
                        self.person_table.c.path == link
                    )
                results = self.connection.execute(stmt).fetchall()
                if results[0][0] > 0:
                    self.logger.debug('{} already exists'.format(name))
                    return None
                self.logger.debug('Querying {1}: {0}'.format(link, name))
                response = self.session.get(self.PODEROPEDIA_BASE_URL + link)
                content = response.content
                html_tree = etree.HTML(content, parser=self.parser)
                connections = html_tree.xpath('//div[@id="conexiones"]')
                if connections:
                    personal_data = self.extract_element_data(connections[0])
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

    def extract_data(self, root, path, tag):
        """
        Method that traverse a table extracting all the relevant information
        about a person.
        """
        data = []
        element = root.xpath(path)
        if element:
            url = self.PODEROPEDIA_BASE_URL + element[0].get('data-w2p_remote', None)
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
                        source = process_source(cells[idx])
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
        """
        Extracts the information of classmates of a person existing in the website.
        """
        return self.extract_data(root, '//div[@id="P2P_comp"]', 'classmate')

    def extract_advisors(self, root):
        """
        Extracts the information of advisors of a person existing in the website.
        """
        return self.extract_data(root, '//div[@id="P2P_asesor"]', 'advisor')

    def extract_organizations(self, root):
        """
        Extracts the information of companies and organizations
        a person existing in the website had worked or collaborated with.
        """
        return self.extract_data(root, '//div[@id="P2O"]', 'organization')
