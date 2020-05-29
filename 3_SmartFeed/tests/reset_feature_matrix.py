import os 
import pandas as pd


DIR = 'feature_matrices/'
for file in os.listdir(DIR):
    df = pd.read_csv(DIR+file)

    df = df[['link', 'ClapRespScore']]

    df.to_csv(DIR+file)