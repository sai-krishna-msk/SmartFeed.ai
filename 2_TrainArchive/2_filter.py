import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler



def get_scored(df, clap_percent=0.5, response_percent=0.5):
    """Computes weighted avergae of scaled values  claps and responses to generate popularity score

    Arguments:
        df {pd.DataFrame} -- DataFrame consisting of article data

    Keyword Arguments:
        clap_percent {float} -- Praportion of total claps contribution (default: {0.5})
        response_percent {float} -- Praportion of total responses contribution (default: {0.5})

    Returns:
        pd.DataFrame -- Dataframe with popularity score as new column
    """
    df_resp = df.copy()
    df_resp['total_claps_scaled'] = np.nan
    df_resp['total_responses_scaled'] = np.nan
    scaler = MinMaxScaler()
    df_resp[['total_claps_scaled', 'total_responses_scaled']] = scaler.fit_transform(
        df_resp[['total_claps', 'total_responses']])

    df_resp["score"] = ((df_resp["total_claps_scaled"]*clap_percent) +
                        (df_resp["total_responses_scaled"]*response_percent))
    return df_resp


def filter_files(data_dir, claps_percent, n_percent):
    """Select the top n_percent of rows in each tag's dataframe based on Cumilative score with top threshold 2000
    and at least 10000

    Arguments:
        data_dir {str} -- Path to the directory where all tag's data is saved
        claps_percent {float} -- Percent of praportion claps should have in cumilative score
        n_percent {float} -- top nth percent is selected
    """
    for file in os.listdir(data_dir):

        file_path = data_dir+file
        dest_path = file_path.split(".cs")[0]+"-top_sort.csv"

        df = pd.read_csv(file_path)

        top_n = int(n_percent*len(df))
        df_score = get_scored(df, claps_percent, 1-claps_percent)
        df_top_score = df_score.nlargest(top_n, 'score')

        if(df_top_score.shape[0] > 2000):
            df_top_score = df_score.nlargest(2000, 'score')

        if(df_top_score.shape[0] < 1000):
            df_top_score = df_score.nlargest(1000, 'score')

        df_top_score.to_csv(dest_path)
        print(f"{dest_path} saved")
        try:
            os.remove(file_path)
            print("Successfully removed {}")
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")


data_dir = 'dataset/'

claps_percent = 0.6

n_percent = 0.05

filter_files(data_dir, claps_percent, n_percent)
