from LDAModel import LDAModel
import time

import warnings
import math
import time

import pandas as pd
import numpy as np
import pickle

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from scipy import spatial
import os


from newspaper import Article


feature_matrix_dir = "feature_matrices/archive"


def get_text(url):
    """Extract text from article's url

    Arguments:
        url {str} -- url of the articl

    Returns:
        str -- text
    """
    article = Article(url=url)
    article.download()
    article.parse()
    return article.text


def validate_all():
    """Validating if topic distribution stores in our models is n the same order as articles present in our 
    feature matrix
    """
    for file_ in os.listdir(feature_matrix_dir):
        tag = file_.split(".c")[0]
        print(f"Validating: {tag}")
        feature_matrix = os.path.join(feature_matrix_dir, file_)
        df = pd.read_csv(feature_matrix)
        model = LDAModel(edition='archive', tag=tag, mode='load')
        rank_one = 0
        for i, url in enumerate(df.link):
            text = get_text(url)
            feature = model.predict(text)
            score = model.simmilarity_score(
                feature, model.get_feature_vectors[i])
            if(score == 1):
                rank_one += 1

        print(f'Accuracy of {tag} is {rank_one/len(df)}')
        print('\n')


curr = time.time()

validate_all()

print(f"Time taken: {time.time()-curr}")
