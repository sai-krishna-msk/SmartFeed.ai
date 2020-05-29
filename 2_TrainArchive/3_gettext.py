

import os
import numpy as np
import pandas as pd
from newspaper import Article, Config


data_dir = 'dataset/'

CNT = 0
NAN = 0


def get_text(url):
    """Given URL of the article extract text from it

    Arguments:
        url {str} -- url of the article

    Returns:
        str -- Text of thr article
    """
    global CNT
    global NAN
    if(CNT % 100 == 0):
        print(CNT)
    config = Config()
    config.keep_article_html = True
    try:
        article = Article(url, config=config)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(e)
        NAN += 1
        return np.nan
    finally:
        CNT += 1


files = os.listdir(data_dir)
for file_ in files:
    print(file_)
    file_path = os.path.join(data_dir, file_)
    dest_path = file_path.split(".cs")[0]+"-text.csv"
    df = pd.read_csv(file_path)

    print("Before Extraction")
    print(df.shape[0])

    df['text'] = df["link"].apply(get_text)
    df.dropna(inplace=True)

    print("After Extraction")
    print(df.shape[0])
    print(f"Number of None's: {NAN}")
    df.to_csv(dest_path, index=False)
    print("removed {} with no text")
    os.remove(file_path)
