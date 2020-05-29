**After Scraping the tags from the previous step and downloading the zip file into datasets**

**unzip the file and run each script in chronological order to get the trained archive models and their respective feature matrices**

1_marge.py: To merge datasets of different years related to one tag into a a csv file

2_filter.py: To select top n_precent of articles based on the cumulative score of total Claps and total responses

3_getText.py: To extract the text from the article url's scraped for training

4_train.py: To Train and save the LDA models along with all the components required to use the model such as count vectorizer and feature matrices 

5_valid.py: To validate if the order of the feature matrices saved aligns with the order of links stored