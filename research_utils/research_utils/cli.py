"""Command line interface for reasearch utils."""
import datetime
import logging

import click
import daiquiri

from research_utils.etl.data_loader import DataLoader

# Configure logging
daiquiri.setup(level=logging.INFO)
LOGGER = daiquiri.getLogger(__name__)

@click.group()
def main():
    """
    Welcome to the research utils CLI!
    To learn more about a command, use the --help flag
    """
    pass

@click.command('load-issues', help='Loads issues from Github into the database')
def load_issues():
    """Fetches issues from the Github API and loads them into the database."""
    data_loader = DataLoader()
    start = datetime.datetime.now()
    LOGGER.info('Started loading Github issues at {}.'.format(start))
    data_loader.load_issues()
    end = datetime.datetime.now()
    LOGGER.info('Finished loading Github issues at {}.'.format(start))
    seconds = (end - start).total_seconds()
    LOGGER.info('Loading issues took {} mins.'.format(seconds/60))
main.add_commant(load_issues)

if __name__ == '__main__':
    main()
