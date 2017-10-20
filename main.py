"""
Module to crawl the poderopedia website.
"""
import argparse

from dotenv import load_dotenv

from person_scrapper import PoderopediaPersonScrapper
from company_scrapper import PoderopediaCompanyScrapper
from organization_scrapper import PoderopediaOrganizationScrapper

def main():
    """
    Main function.
    Called when the script is called directly from cmd line.
    """
    # load environment variables from .env
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    #parse cmd line arguments
    parser = argparse.ArgumentParser(description='Command line to download data from poderopedia')
    parser.add_argument('-p', '--persons', action='store_true', help='recover people information')
    parser.add_argument('-c', '--companies', action='store_true', help='recover companies information')
    parser.add_argument('-o', '--organizations', action='store_true', help='recover organizations information')
    args = parser.parse_args()

    if not (args.persons or args.companies or args.organizations):
        parser.error('Please add one of --persons or --companies or --organizations')

    if args.persons:
        person_scrapper = PoderopediaPersonScrapper()
        person_scrapper.setup()
        person_scrapper.persons()
    if args.companies:
        company_scrapper = PoderopediaCompanyScrapper()
        company_scrapper.setup()
        company_scrapper.companies()
    if args.organizations:
        organization_scrapper = PoderopediaOrganizationScrapper()
        organization_scrapper.setup()
        organization_scrapper.organizations()

if __name__ == '__main__':
    main()

