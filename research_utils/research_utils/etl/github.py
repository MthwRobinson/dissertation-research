"""Module for pulling contributor information from Github."""
import getpass
import logging
import json
import re
import uuid

import daiquiri
import datetime
import requests
from requests.auth import HTTPBasicAuth
import time

from research_utils import Database

CURATED_LISTS = {
    'javascript': 'sorrycc/awesome-javascript',
    'java': 'akullpp/awesome-java',
    'python': 'vinta/awesome-python',
    'php': 'ziadoz/awesome-php',
    'cpp': 'fffaraz/awesome-cpp'
}

class Github:
    def __init__(self, username=None, password=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)
        self.database = Database()

        if not username or not password:
            print('Enter your Github username: ')
            username = input()
            print('Enter your Github password: ')
            password = getpass.getpass()
        self.username = username
        self.password = password

        self.base_url = 'https://api.github.com'

    def get(self, url):
        """Makes an authenticated request to the Github API."""
        auth = HTTPBasicAuth(self.username, self.password)
        response = requests.get(url, auth=auth)
        if response.status_code == 403:
            headers = response.headers
            if headers['X-RateLimit-Remaining'] == 0:
                # Determine how much time until the rate limit resets
                reset_ts = float(headers['X-RateLimit-Reset'])
                reset_time = datetime.datetime.fromtimestamp(reset_ts)
                now = datetime.datetime.now()
                sleep_time = (reset_time - now).total_seconds()

                # Sleep until the rate limit resets and try the
                # API call again
                msg = 'Rate limit exceeded. Sleeping for {}s'.format(sleep_time)
                self.logger.info(msg)
                time.sleep(sleep_time)
                response = requests.get(url, auth=auth)
        #time.sleep(1) # To keep under the Github rate limit
        return response

    def get_issues(self, organization, package):
        """Pull a list of issues for the specified organization and package."""
        url = '{}/repos/{}/{}/issues?state=all'.format(self.base_url,
                                                       organization,
                                                       package)
        issues = self._traverse_response(url)
        return issues

    def get_issue_comments(self, organization, package, issue_number):
        """Pulls the specified issue number."""
        url = '{}/repos/{}/{}/issues/{}/comments'.format(self.base_url,
                                                         organization,
                                                         package,
                                                         issue_number)
        response = self.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None

    def get_contributors(self, organization, package):
        """Pulls a list of contributors for a package."""
        url = '{}/repos/{}/{}/stats/contributors?sort=total&direction=desc'.format(self.base_url,
                                                         organization,
                                                         package)
        response = self.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None

    def _traverse_response(self, url):
        """Traverses a response that is split over multiple pages."""
        items = []
        response = self.get(url)
        status = response.status_code
        if status == 200:
            while True:
                items += json.loads(response.text)
                headers = response.headers
                links = requests.utils.parse_header_links(headers['Link'])
                next_page = [x for x in links if x['rel'] == 'next']
                if next_page:
                    url = next_page[0]['url']
                    response = self.get(url)
                else:
                    break
        else:
            msg = 'Bad request (status code {}) for {}'.format(status, url)
            self.logger.warning(msg)
            items = None
        return items

    def load_packages(self, truncate=False):
        """Loads the list of most popular Python packages into the DB."""
        if truncate:
            self.database.truncate_table('packages')

        for language in CURATED_LISTS:
            markdown = get_popular_package_md(CURATED_LISTS[language])
            packages = parse_package_md(markdown)
            github_packages = find_github_packages(packages, language)
            self.database.load_items(github_packages, 'packages')

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
