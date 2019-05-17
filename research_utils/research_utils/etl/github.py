"""Module for pulling contributor information from Github."""
import logging
import re
import uuid

import daiquiri
import requests

from research_utils import Database

class Github:
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)
        self.database = Database()

    def load_packages(self, truncate=False):
        """Loads the list of most popular Python packages into the DB."""
        if truncate:
            self.database.truncate_table('packages')

        markdown = get_popular_package_md()
        packages = parse_package_md(markdown)
        github_packages = find_github_packages(packages)
        self.database.load_items(github_packages, 'packages')

def find_github_packages(packages):
    """Finds which packages are on Github and formats them for
    upload to the database."""
    github_packages = []
    for package in packages:
        url = packages[package]
        if url.startswith('https://github.com'):
            info = url.split('/')
            package_name = info[-1]
            org_name = info[-2]
            item = {
                'id': uuid.uuid4().hex,
                'package_name': package_name,
                'org_name': org_name,
                'url': url
            }
            github_packages.append(item)
    return github_packages

def get_popular_package_md():
    """Pulls a markdown file with a curated list of popular
    open source Python packages."""
    url = 'https://raw.githubusercontent.com/vinta/awesome-python/master/README.md'
    response = requests.get(url)
    return response.text

def parse_package_md(markdown):
    """Pulls URLs and package names out of the popular package markdown."""
    url_regex = re.compile(r'(?:__|[*])|\[(.*?)\)')
    results = url_regex.findall(markdown)
    packages = {}
    for result in results:
        if '](' in result:
            package = result.split('](')
            name = package[0]
            url = package[1]
            packages[name] = url
    return packages
