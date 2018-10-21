"""
Module to crawl the persons available at the poderopedia website.
"""

from datetime import datetime
from lxml import html, etree
from sqlalchemy import func, select

import requests

from scrapper import PoderopediaScrapper
from utils import text_strip, process_sources

class PoderopediaOrganizationScrapper(PoderopediaScrapper):
    """
    Scrapper for the organizations that are listed at poderopedia.
    """

    def __init__(self):
        super(PoderopediaOrganizationScrapper, self).__init__()
        self.organization_table = self.meta.tables['organization']
        self.connection = self.engine.connect()
        self.session = None

    def organizations(self):
        """
        Method to retrieve the list of organizations in the current page
        """
        self.elements('organizations')

    def process_organizations(self, organizations):
        """
        Crawl the information of organizations that is available at the website.
        """
        self.process_elements(
            organizations,
            self.organization_table,
            self.extract_organization,
            ['organization_data', 'member', 'organization']
        )

    def extract_organization(self, root):
        """
        Extracts all the information of an organization existing in the website.
        """
        organization = {}
        info = root.xpath('.//li/h4/a')
        if info:
            link = info[0].get('href', None)
            name = info[0].get('title', None)
            if link and name:
                stmt = select([
                        func.count(self.organization_table.c.path)
                    ]).where(
                        self.organization_table.c.path == link
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
                    organization_data = self.extract_element_data(connections[0])
                    organization['organization_data'] = organization_data if organization_data else {}
                    organization['organization_data']['path'] = link

                    person = self.extract_persons(connections[0])
                    organization['member'] = person if person else []
                    for item in organization['member']:
                        item.update({'source_path': link})

                    related_organization = self.extract_participation(connections[0])
                    organization['organization'] = related_organization if related_organization else []
                    for item in organization['organization']:
                        item.update({'source_path': link})
        return organization

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
                            sources = cells[idx].xpath('.//*[@class="fuente"]')
                            if len(sources) > 0:
                                source = process_sources(cells[idx])
                            elif cell_text == 'es' or cell_text == 'fue':
                                when = cell_text
                                idx = idx - 1
                                target = cells[idx].find('a')
                                if target is not None:
                                    target_path = target.get('href', None)
                                    target_name = text_strip(target)
                                idx = idx + 2
                                relationship = text_strip(cells[idx])
                            elif cell_text == 'a' or cell_text == 'de':
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
                        entry = {
                            'type': tag,
                            'target_path': target_path,
                            'relationship': relationship,
                            'when': when,
                            'where': where,
                            'source': source
                        }
                        data.append(entry)
                        self.logger.debug('{}: {}'.format(tag, entry))
                except (requests.exceptions.HTTPError, etree.ParserError):
                    self.logger.info('Something bad happened', exc_info=True)
        return data

    def extract_participation(self, root):
        return self.extract_data(root, '//div[@id="O2O"]', 'organization')

    def extract_persons(self, root):
        return self.extract_data(root, '//div[@id="P2O"]', 'member')

