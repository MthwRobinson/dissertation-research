"""Module for building topic models from GitHub issue bodies."""
import logging
import os
import pickle

import daiquiri
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer
import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine

from research_utils.database.database import Database

HOME_PATH = os.path.expanduser('~')

daiquiri.setup(level=logging.INFO)
LOGGER = daiquiri.getLogger(__name__)

class TopicModel:
    """Class for applying and LDA topic model to the issues
    in the GitHub dataset and determining the level of diversity
    in the topics for a given package."""
    def __init__(self, num_topics):

        self.database = Database()
        self.model_path = os.path.join(HOME_PATH, 'topic_models')

        # Attributes related to the gensim topic model
        self.lda_model = None
        self.num_topics = num_topics
        self.tfidf = None
        self.dictionary = None
        self.topic_matrix = None
        self.similarity_matrix = None

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

    def train_model(self, df):
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
                                                    num_topics=self.num_topics,
                                                    passes=3,
                                                    workers=3)

    def get_topics(self, title, body):
        """Returns the topics for a document."""
        # Preprocess the document to get it into the form that
        # is required by the LDA model
        text = title + ' ' + body
        corpus = [_preprocess(text)]
        bags_of_words = _build_bags_of_words(corpus, self.dictionary)
        corpus_tfidf = self.tfidf[bags_of_words]

        # Determine the topic vector for the issue
        if len(corpus_tfidf) > 0:
            topics = self.lda_model.get_document_topics(corpus_tfidf[0],
                                                        minimum_probability=0.0000001)
        else:
            return None

        # Make sure there is an entry for every topic, because
        # the topic list that we write to the database depends
        # array index
        if len(topics) != self.num_topics:
            LOGGER.warning('There is not a score for every topic!')
            return None

        # Reformat the topic list so that we can upload it to Postgres
        cleaned_topics = []
        for topic in sorted(topics):
            # The second element of the tuple is the topic score
            cleaned_topics.append(float(topic[1]))

        return cleaned_topics

    def get_df_topics(self, df):
        """Computes a topic column for a dataframe of issues."""
        topics = []
        total_issues = len(df)
        for i in df.index:
            if i%50000 == 0:
                LOGGER.info('Computing topic for issue {}/{}'.format(i, total_issues))
            row = dict(df.loc[i])
            topic_vector = self.get_topics(row['title'], row['body'])
            topics.append(topic_vector)
        return topics

    def compute_similarity_matrix(self):
        """Computes a matrix where entry i,j is the consine similarity between
        topic i and topic j."""
        self.topic_matrix = self.lda_model.get_topics()
        similarity_matrix = []
        for i in range(self.num_topics):
            topic_similarities = []
            for j in range(self.num_topics):
                topic_similarities.append(self.get_similarity(i, j))
            similarity_matrix.append(topic_similarities)

        self.similarity_matrix = np.array(similarity_matrix)

    def get_similarity(self, i, j):
        """Computes the cosine similarity between two topics in an LDA model.
        Cosine similartiy is computed as 1 - cosine distance."""
        return 1 - cosine(self.topic_matrix[i, :], self.topic_matrix[j, :])

    def load_topics(self, issue_id, topics):
        """Stores the topics for the issue in postgres."""
        column = "topics_{}".format(self.num_topics)
        self.database.update_column(table='issues', item_id=issue_id,
                                    column=column, value=topics)

    def load_issue_topics(self, df):
        """Loads issue topics to the database for all issues in the dataframe."""
        total_issues = len(df)
        for i in df.index:
            if i%50000 == 0:
                LOGGER.info('Loading topic for issue {}/{}'.format(i, total_issues))
            row = dict(df.loc[i])
            self.load_topics(row['issue_id'], row['topics'])

    def save(self):
        """Saves the model to the model directory."""
        attrs = ['lda_model', 'tfidf', 'dictionary',
                 'topic_matrix', 'similarity_matrix']
        for attr in attrs:
            obj = getattr(self, attr)
            filename = 'lda_model_{}_{}.pickle'.format(self.num_topics, attr)
            full_path = os.path.join(self.model_path, filename)
            with open(filename, 'wb') as f:
                pickle.dump(obj, f)


def _build_dictionary(corpus):
    """Builds a dictionary based on the corpus."""
    dictionary = gensim.corpora.Dictionary(corpus)
    # Filters out documents that appear in fewer than 15 documents
    # or in more than half the documents.
    dictionary.filter_extremes(no_below=15, no_above=.3)
    return dictionary

def _build_bags_of_words(corpus, dictionary):
    """Uses the dictionary to create a bag of words out of each document."""
    bags_of_words = [dictionary.doc2bow(doc) for doc in corpus]
    bags_of_words = [x for x in bags_of_words if len(x) >= 5]
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
