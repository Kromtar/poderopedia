"""
Module to crawl the persons available at the poderopedia website.
"""

from lxml import html, etree
from sqlalchemy import MetaData, Table, create_engine, exists, func, select

from scrapper import PoderopediaScrapper
from utils import cc_to_us, to_date, text_strip, xpath_value, xpath_html, process_source

class PoderopediaCompanyScrapper(PoderopediaScrapper):
    """
    Scrapper for the companies that are listed at poderopedia.
    """

    def __init__(self):
        super(PoderopediaCompanyScrapper, self).__init__()
        self.company_table = self.meta.tables['company']
        self.connection = self.engine.connect()
        self.session = None

    def companies(self):
        """
        Method to retrieve the list of companies in the current page
        """
        self.elements('companies')

    def process_companies(self, companies):
        """
        Crawl the information of companies that is available at the website.
        """
        self.process_elements(
            companies,
            self.company_table,
            self.extract_company,
            ['company_data', 'member', 'organization']
        )

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
                stmt = select([
                        func.count(self.company_table.c.path)
                    ]).where(
                        self.company_table.c.path == link
                    )
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
                    company_data = self.extract_element_data(connections[0])
                    company['company_data'] = company_data if company_data else {}
                    company['company_data']['path'] = link

                    person = self.extract_persons(connections[0])
                    company['member'] = person if person else []
                    for item in company['member']:
                        item.update({'source_path': link})

                    organization = self.extract_participation(connections[0])
                    company['organization'] = organization if organization else []
                    for item in company['organization']:
                        item.update({'source_path': link})
        return company

    def extract_data(self, root, path, tag):
        """
        Method that traverse a table extracting all the relevant information
        about a person.
        """
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
                            if cell_text == 'es' or cell_text == 'fue':
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
                        source = process_source(cells[idx])
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

