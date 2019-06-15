"""Class for constructing stakeholder networks, producing analytics
and storing plots."""
import itertools
import logging
import os
import pickle

import daiquiri
import networkx as nx
import numpy as np
import pandas as pd

from research_utils.database.database import Database

class StakeholderNetwork:
    """Builds out the stakeholder network. If overwrite=False, then
    the class will look for a save version of the stakeholder network
    first. Otherwise, the network information will be pulled from
    the database."""
    def __init__(self, organization, package, overwrite=False):
        self.database = Database()
        self.path = os.path.dirname(os.path.realpath(__file__))

        self.organization = organization
        self.package = package
        self.network = self.build_network()
        self.gini = self.compute_gini()

    def get_links(self):
        """Pulls links from the database that are used to build
        the stakeholder network."""
        sql = """
            SELECT *
            FROM open_source.issue_comments
            WHERE organization = '{}' AND package = '{}'
        """.format(self.organization, self.package)
        df = pd.read_sql(sql, self.database.connection)
        return df

    def build_network(self):
        """Builds a networkx graph from a dataframe of links."""
        network = nx.Graph()
        df = self.get_links()
        issues = df.groupby('issue_number')
        for issue_number, issue in issues:
            users = list(issue['user_id'].unique())
            pairs = itertools.combinations(users, 2)
            for pair in pairs:
                network.add_edge(*pair)
        return network

    def compute_gini(self):
        """Computes the gini coefficient for the network."""
        if self.network:
            degrees = [self.network.degree(x) for x in self.network.nodes]
            gini_coefficient = gini(degrees)
        else:
            gini_coefficient = None
        return gini_coefficient

    def load_network(self):
        """Loads the network into the database."""
        item = {
            'organization': self.organization,
            'package': self.package,
            'gini_coefficient': self.gini,
            'stakeholder_network': pickle.dumps(self.network)
        }
        self.database.load_item(item, 'stakeholder_networks')
    
    def delete_network(self):
        """Loads the network into the database."""
        sql = """
            DELETE FROM open_source.stakeholder_networks
            WHERE organization = '{}' AND package = '{}'
        """.format(self.organization, self.package)
        self.database.run_query(sql)

def gini(x):
    """Computes the Gini coefficient for a discrete distribution."""
    mad = np.abs(np.subtract.outer(x, x)).mean()
    # Relative mean absolute difference
    rmad = mad/np.mean(x)
    # Gini coefficient
    g = 0.5 * rmad
    return g
