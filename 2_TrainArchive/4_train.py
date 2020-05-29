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

data_dir = "dataset/"
feature_matrix_dir = "feature_matrices/archive"


def train_all():
    """Train each of archive's tags and save the model along with features such as url and cumilative score
    """
    for file_ in os.listdir(data_dir):
        tag = file_.split(".c")[0]
        print(tag)
        print("With Preprocessing---------------------")
        file_path = os.path.join(data_dir, file_)
        feature_matrix = os.path.join(feature_matrix_dir, tag)

        df = pd.read_csv(file_path)
        df = df[~df['link'].duplicated()]
        df = df.dropna().reset_index().drop(
            ['index', 'Unnamed: 0', 'Unnamed: 0.1'], axis=1)

        model = LDAModel(mode='train', edition='archive',
                         tag=tag,  texts=df.text.values.tolist())
        model.train(n_topics=100)
        print(model.evaluate())
        model.save()

        df = df.drop('text', axis=1)
        df.to_csv(feature_matrix+".csv", index=False)

        print('\n')


curr = time.time()

train_all()

print(f"Time taken: {time.time()-curr}")
