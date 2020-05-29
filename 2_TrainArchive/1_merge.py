import os
import numpy as np
import pandas as pd
import shutil


def parseDataSet(data_dir, clear=False):
    """Merge Articles data of each tag of different years into one csv file

    Arguments:
        data_dir {str} -- path of directory where dataset is stored

    Keyword Arguments:
        clear {bool} -- After merging if True delete raw data (default: {False})
    """
    for tag_dir in os.listdir(data_dir):
        df_temp = pd.DataFrame()
        tag_dir_path = os.path.join(data_dir, tag_dir)
        dest_path = os.path.join(data_dir, f"{tag_dir}.csv")
        print(f"Processing {tag_dir} tag")
        for data_file in os.listdir(tag_dir_path):
            file_path = os.path.join(tag_dir_path, data_file)
            df = pd.read_csv(file_path)
            df_temp = pd.concat([df_temp, df])

        df_temp.to_csv(dest_path)
        print(f"Saved {tag_dir} data to {dest_path}")
        if(clear):
            try:
                shutil.rmtree(tag_dir_path)
                print(f"Deleted {tag_dir} folder")
            except Exception as e:
                print(f"Error while removing {tag_dir} folder: {e}")


curre_dir = (os.getcwd().replace("\\", '/'))+'/dataset/Arhive(2k18-2k19)/'
parseDataSet(curre_dir, True)
