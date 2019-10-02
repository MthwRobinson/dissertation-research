"""Module for building topic models from GitHub issue bodies."""
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
import pandas as pd

from research_utils.database.database import Database

class TopicModel:
    """Class for applying and LDA topic model to the issues
    in the GitHub dataset and determining the level of diversity
    in the topics for a given package."""
    def __init__(self):
        self.database = Database()

        self.corpus = []
        self.bags_of_words = []
        self.dictionary = {}

    def get_issues(self, sample_size=None):
        """Pulls a list of issues, their titles and their bodies
        from the database."""
        sql = """
            SELECT *
            FROM open_source.issue_content
        """
        if sample_size:
            sql += " ORDER BY RANDOM() LIMIT {} ".format(sample_size)
        df = pd.read_sql(sql, self.database.connection)
        return df

    def _build_dictionary(self):
        """Builds a dictionary based on the corpus."""
        self.dictionary = gensim.corpora.Dictionary(self.corpus)
        # Filters out documents that appear in fewer than 15 documents
        # or in more than half the documents.
        self.dictionary.filter_extremes(no_below=15, no_above=.5)

    def _build_bags_of_words(self):
        """Uses the dictionary to create a bag of words out of each document."""
        self.bags_of_words = [self.dictionary.doc2bow(doc) for doc in self.corpus]

def lemmatize_stemming(text):
    """Changes third person words to first person and converts past and future
    tense to present tense for standardization."""
    stemmer = WordNetLemmatizer()
    return stemmer.lemmatize(text, pos='v')

def preprocess(text):
    """Removes stops words and any tokens that are too short."""
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result
