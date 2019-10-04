"""Module for building topic models from GitHub issue bodies."""
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer
import numpy as np
import pandas as pd

from research_utils.database.database import Database

class TopicModel:
    """Class for applying and LDA topic model to the issues
    in the GitHub dataset and determining the level of diversity
    in the topics for a given package."""
    def __init__(self):
        self.database = Database()

        self.tfidf = None
        self.lda_model = None
        self.dictionary = None

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

    def train_model(self, df, num_topics):
        """Trains an LDA topic model on the issues in the dataframe."""
        # Preprocess the content and convert the issues into bags of words
        # which we can turn into features for topic modeling
        df['all_content'] = df['title'] + ' ' + df['body']
        corpus = [_preprocess(x) for x in df['all_content'] if x]
        self.dictionary = _build_dictionary(corpus)
        bags_of_words = _build_bags_of_words(corpus, self.dictionary)

        # Train a TFIDF model on the corpus of issues. These will create
        # vectors that we can use for the topic modeling process.
        self.tfidf = gensim.models.TfidfModel(bags_of_words)
        corpus_tfidf = self.tfidf[bags_of_words]

        self.lda_model = gensim.models.LdaMulticore(corpus=corpus_tfidf,
                                                    id2word=self.dictionary,
                                                    num_topics=num_topics,
                                                    passes=3,
                                                    workers=3)

    def get_topics(self, text):
        """Returns the topics for a document."""
        corpus = [_preprocess(text)]
        bags_of_words = _build_bags_of_words(corpus, self.dictionary)
        corpus_tfidf = self.tfidf[bags_of_words]
        topics = self.lda_model[corpus_tfidf[0]]
        return topics

def _build_dictionary(corpus):
    """Builds a dictionary based on the corpus."""
    dictionary = gensim.corpora.Dictionary(corpus)
    # Filters out documents that appear in fewer than 15 documents
    # or in more than half the documents.
    # dictionary.filter_extremes(no_below=15, no_above=.5)
    return dictionary

def _build_bags_of_words(corpus, dictionary):
    """Uses the dictionary to create a bag of words out of each document."""
    bags_of_words = [dictionary.doc2bow(doc) for doc in corpus]
    return bags_of_words

def lemmatize_stemming(text):
    """Changes third person words to first person and converts past and future
    tense to present tense for standardization."""
    stemmer = WordNetLemmatizer()
    return stemmer.lemmatize(text, pos='v')

def _preprocess(text):
    """Removes stops words and any tokens that are too short."""
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result
