"""Module for pulling contributor information from Github."""
import getpass
import logging
import json
import re

import daiquiri
import datetime
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError
import time

CURATED_LISTS = {
    'javascript': 'sorrycc/awesome-javascript',
    'java': 'akullpp/awesome-java',
    'python': 'vinta/awesome-python',
    'php': 'ziadoz/awesome-php',
    'cpp': 'fffaraz/awesome-cpp'
}

class Github:
    def __init__(self, username=None, password=None, sleep=True):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        if not username or not password:
            print('Enter your Github username: ')
            username = input()
            print('Enter your Github password: ')
            password = getpass.getpass()
        self.username = username
        self.password = password

        self.base_url = 'https://api.github.com'
        self.sleep = sleep

    def get(self, url):
        """Makes an authenticated request to the Github API."""
        auth = HTTPBasicAuth(self.username, self.password)
        try:
            response = requests.get(url, auth=auth)
        except ConnectionError:
            msg = 'Connection error for {}. Trying again.'.format(url)
            self.logger.warning(msg)
            response = self.get(url)

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

        if self.sleep:
            time.sleep(1) # To keep under the Github rate limit
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
