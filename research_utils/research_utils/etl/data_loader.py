"""Module for pulling contributor information from Github."""
import logging
import re
import uuid

import daiquiri
import requests
import pandas as pd

from research_utils import Database
from research_utils.etl.github import Github

CURATED_LISTS = {
    'javascript': 'sorrycc/awesome-javascript',
    'java': 'akullpp/awesome-java',
    'python': 'vinta/awesome-python',
    'php': 'ziadoz/awesome-php',
    'cpp': 'fffaraz/awesome-cpp'
}

class DataLoader:
    """Class for loading Github data into the Postgres database."""
    def __init__(self, username=None, password=None, sleep=True):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)
        self.database = Database()
        self.github = Github(username=username, password=password, sleep=sleep)

    def load_packages(self, truncate=False):
        """Loads the list of most popular Python packages into the DB."""
        if truncate:
            self.database.truncate_table('packages')

        for language in CURATED_LISTS:
            markdown = get_popular_package_md(CURATED_LISTS[language])
            packages = parse_package_md(markdown)
            github_packages = find_github_packages(packages, language)
            self.database.load_items(github_packages, 'packages')

    def _load_package_issues(self, organization, package):
        """Loads the issues for the specified package into the database."""
        msg = 'Loading issues for {}/{}'.format(organization, package)
        self.logger.info(msg)

        package_id = self._get_package_id(organization, package)
        issues = self.github.get_issues(organization, package)

        for issue in issues:
            self.database.delete_item(item_id=issue['id'], table='issues')

            if issue['labels']:
                labels = [x['name'] for x in issue['labels']]
            else:
                labels = []
            if issue['assignee']:
                assignee = issue['assignee']['id']
            else:
                assignee = None
            if issue['assignees']:
                assignees = [x['id'] for x in issue['assignees']]
            else:
                assignees = []

            item = {
                'id': issue['id'],
                'package_id': package_id,
                'organization': organization,
                'package': package,
                'user_id': issue['user']['id'],
                'user_login': issue['user']['login'],
                'issue_number': issue['number'],
                'title': issue['title'],
                'created_at': issue['created_at'],
                'updated_at': issue['updated_at'],
                'closed_at': issue['closed_at'],
                'labels': labels,
                'assignees': assignees,
                'assignee': assignee,
                'pull_request': 'pull_request' in issue
            }
            try:
                self.database.load_item(item=item, table='issues')
            except:
                import ipdb; ipdb.set_trace()

    def _get_package_id(self, organization, package):
        """Pulls the package id for the specified package."""
        sql = """
            SELECT id
            FROM {schema}.packages
            WHERE org_name = '{organization}'
            AND package_name = '{package}'
        """.format(schema=self.database.schema, organization=organization,
                   package=package)
        df = pd.read_sql(sql, self.database.connection)
        if len(df) > 0:
            return df.loc[0]['id']
        else:
            return None

def find_github_packages(packages, language):
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
                'url': url,
                'language': language
            }
            github_packages.append(item)
    return github_packages

def get_popular_package_md(repo):
    """Pulls a markdown file with a curated list of popular
    open source Python packages."""
    url = 'https://raw.githubusercontent.com/{}/master/README.md'.format(repo)
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
