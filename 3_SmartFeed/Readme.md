**To simply run the system**

**Replace following place holders in config.py**

```python
SEND_GRID_KEY
FROM_EMAIL
cloud_config
```

then run the following

```bash
python SmartFeed.py
```

**To reset the application run**

```bash
python tests/reset_feature_matrix.py
```



ArticleParser.py: Given url of article extracts all the required features

config.py: Consists of All external configurations required for system to run(like firebase keys etc)

DocRecommendor.py: Recommendation Engine responsible for generating recommendations for given user profile

FeedSender.py responsible for sending the feed to users via email

LDAModel.py responsible for training the LDA model

ScrapeDaily.py: Responsible for Scraping the daily edition of articles

SmartFeed.py: Manages all the components and runs the pipeline

utils.py: Consists code to initiate logger for all the modules

