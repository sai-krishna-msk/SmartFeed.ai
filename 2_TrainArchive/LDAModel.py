
import warnings
import math
import time

import pandas as pd
import numpy as np
import pickle

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from scipy import spatial
from pathlib import Path

from utils import getLogger

logger = getLogger("LDAModel")


class LDAModel():
    """Model Class used for training and loading models
    """

    def __init__(self, mode=None, edition=None, tag=None, texts=None, features=None, model=None, vectorizer=None, n_features=100000,
                 min_df=5, max_df=0.5, stop_words='english', lda_mode='online', verbose=1):
        """

        Keyword Arguments:
            mode {str} -- Either train or load mode (default: {None})
            edition {str} -- Either Archive or Daily (default: {None})
            tag {str} -- name of the tag (default: {None})
            texts {list} -- list of texts for training (default: {None})
            features {list} -- list of topic distributions or features for input text (default: {None})
            model {Model} -- LDA model  (default: {None})
            vectorizer {CountVectorizer} -- Counter Vectorizer Object (default: {None})
            n_features {int} -- Number of features to consider (default: {100000})
            min_df {int} -- Lower threshold of document Frequency for ingnoring (default: {5})
            max_df {float} -- Upper threshold of Document Frequency for ignoring (default: {0.5})
            stop_words {str} -- Set of stop words to use for preprocessing (default: {'english'})
            lda_mode {str} --  mode of LDA Training (default: {'online'})
            verbose {int} -- Verbose (default: {1})

        """

        self.mode = mode
        self.tag = tag
        self.model_path = f"models/{edition}/{tag}/"

        if(mode == 'load'):
            self.model, self.vectorizer, self.features = self._load_topic_model()

        elif(mode == 'train'):
            if(not texts):
                raise Exception(
                    "Text needs to be provided if Model intialized in train mode")
            self.texts = texts
            self.features = features
            self.model = model
            self.n_features = n_features
            self.min_df = min_df
            self.max_df = max_df
            self.stop_words = stop_words
            self.lda_mode = lda_mode
            self.verbose = verbose

        else:
            raise Exception("Enter a valid mode")

    def train(self, n_topics=None, lda_max_iter=5):
        """Train the LDA model and get features of text used to train

        Keyword Arguments:
            n_topics {int} -- Number of topics to consider for each document (default: {None})
            lda_max_iter {int} -- Number of itteration of training (default: {5})

        """
        if(self.mode == 'load'):
            raise Exception(
                "The model was not intialized for training purpose")

        if n_topics is None:
            estimated = max(1, int(math.floor(math.sqrt(len(self.texts) / 2))))
            n_topics = min(400, estimated)
            logger('n_topics automatically set to %s' % (n_topics))

        self.n_topics = n_topics
        self.lda_max_iter = lda_max_iter

        if self.verbose:
            logger.info('preprocessing texts...')

        self.vectorizer = CountVectorizer(max_df=self.max_df, min_df=self.min_df,
                                          max_features=self.n_features, stop_words=self.stop_words)

        x_train = self.vectorizer.fit_transform(self.texts)

        alpha = 5./self.n_topics
        beta = 0.01
        if self.verbose:
            logger.info('fitting model...')
        self.model = LatentDirichletAllocation(n_components=self.n_topics, max_iter=self.lda_max_iter,
                                               learning_method=self.lda_mode, learning_offset=50.,
                                               doc_topic_prior=alpha, topic_word_prior=beta,
                                               verbose=self.verbose, random_state=0)
        self.model.fit(x_train)

        if self.verbose:
            logger.info("Building Feature Matrix for text")

        self.features = self.predict(self.texts)

    def predict(self, texts):
        """For given text generate probabilites of topic distribution

        Arguments:
            texts {str/list} -- Input text

        Returns:
            list -- list of features which are topic distributions probabilities
        """
        if(isinstance(texts, str)):
            texts = [texts]
        transformed_texts = self.vectorizer.transform(texts)
        X_topics = self.model.transform(transformed_texts)
        return X_topics

    def simmilarity_score(self, fet1, fet2):
        """Caluclating Cosine simmilarty between two features

        Arguments:
            fet1 {list} -- First Feature Vector 
            fet2 {list} -- Second Feature Vector

        Returns:
            float -- Cosine Simmilarity score
        """
        return (1 - spatial.distance.cosine(fet1, fet2))

    def _get_ind(self, text):
        """Returns index of feature vectors to which it is the closest

        Arguments:
            text {str} -- text of the article

        Returns:
            int -- index 
        """
        scores = []
        feature = self.predict(text)
        for feature_ in self.get_feature_vectors:
            scores.append(self.simmilarity_score(feature_, feature))

        return scores.index(max(scores))

    def evaluate(self):
        """Evaluate the train model
        """
        logger.info("Evaluatig the model")
        cnt = 0
        for i, text in enumerate(self.texts):
            ind = self._get_ind(text)
            if(ind == i):
                cnt += 1
        return(cnt/len(self.texts))

    @property
    def get_feature_vectors(self):
        return self.features

    def save(self):
        """save LDA model components Including actual model, feature vectors and CountVectorizer used
        """

        try:

            Path(self.model_path).mkdir(parents=True, exist_ok=True)

            with open(self.model_path+self.tag+'.vectorizer', 'wb') as f:
                pickle.dump(self.vectorizer, f)

                with open(self.model_path+self.tag+'.model', 'wb') as f:
                    pickle.dump(self.model, f)

                with open(self.model_path+self.tag+'.features', 'wb') as f:
                    pickle.dump(self.features, f)

        except Exception as e:
            logger.error(
                f"Could not save the model to {self.model_path+self.tag}: {e}")

    def _load_topic_model(self):
        """Loads components required for using LDAModel Class 

        Returns:
            Model  -- Return LDA model, vectorizer and feature vectors
        """
        try:
            with open(self.model_path+self.tag+'.vectorizer', 'rb') as f:
                vectorizer = pickle.load(f)

            with open(self.model_path+self.tag+'.model', 'rb') as f:
                model = pickle.load(f)

            with open(self.model_path+self.tag+'.features', 'rb') as f:
                features = pickle.load(f)

            return model, vectorizer, features

        except Exception as e:
            logger.error(
                f"Failed to load the model from {self.model_path}: {e}")
