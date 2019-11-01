"""Command line interface for reasearch utils."""
import datetime
import logging
import pickle

import click
import daiquiri
import pandas as pd

from research_utils.analytics.stakeholder_network import StakeholderNetwork
from research_utils.analytics.lda import TopicModel
from research_utils.database.database import Database
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
main.add_command(load_issues)

@click.command('build-networks', help='Builds the SH networks and stores them in the DB.')
def build_networks():
    """Builds stakeholders networks and stores them in the postgres table."""
    database = Database()
    sql = """
        SELECT DISTINCT a.package, a.organization, a.crowd_pct
        FROM open_source.crowd_percentage a
        INNER JOIN open_source.issue_comments b
        ON (a.package = b.package
        AND a.organization = b.organization)
        INNER JOIN open_source.issue_contributors c
        ON c.issue_id = b.issue_id
    """
    df = pd.read_sql(sql, database.connection)
    msg = 'Creating stakeholder networks for {} packages'.format(len(df))
    LOGGER.info(msg)
    for i in df.index:
        LOGGER.info('Creating network for project number {}'.format(i+1))
        row = dict(df.loc[i])
        network = StakeholderNetwork(row['organization'], row['package'])
        msg = '{}/{} -- Gini: {}'.format(network.organization,
                                         network.package,
                                         network.gini)
        LOGGER.info(msg)
        network.delete_network()
        network.load_network(crowd_pct=row['crowd_pct'])
        network.load_user_centralities()
main.add_command(build_networks)

@click.command('build-topic-models', help='Builds LDA models to measure issue diversity')
def build_topic_models():
    """Builds LDA models that will be used to measure the amount of diversity
    is the requirements for a GitHub project."""
    for num_topics in [10, 25, 50, 100, 200]:
        LOGGER.info('Building topic model with {} topics'.format(num_topics))
        topic_model = TopicModel(num_topics=num_topics)
        df = topic_model.get_issues()
        topic_model.train_model(df)
        topic_model.compute_similarity_matrix()
        topic_model.save()
        df['topics'] = topic_model.get_df_topics(df)
        filename = '/home/matt/topic_models/topic_model_results_{}_topics.pickle'.format(num_topics)
        with open(filename, 'wb') as f:
            pickle.dump(df, f)
main.add_command(build_topic_models)

@click.command('compute-document-diversity')
def compute_document_diversity():
    """Computes document diversity for the packages based on the LDA models."""
    for num_topics in [10, 25, 50]:
        LOGGER.info('Loading doc diversity for {} topics'.format(num_topics))
        topic_model = TopicModel(num_topics=num_topics, load=True)
        inputs = topic_model.load_topic_model_results()
        diversity_scores = topic_model.compute_diversity(inputs)
        topic_model.load_document_diversity(diversity_scores)
main.add_command(compute_document_diversity)

if __name__ == '__main__':
    main()
