<img src="images/logo-2.png">

# Contents
- **Problem Statement**
- **Introduction**
- **How to use the Service**
- **Components**
- **Recommendation Engine Implementation**
- **Navigating Code**
- **Further Improvements**

<hr>

# Problem Statement

Scarcity of information is equally bad as Excess of it.

Sheer volume of newsletters that flood our inbox overwhelms us into not sticking with the habit of reading.

Though there are implicit feedback mechanisms on several blogs, Which based on our read-time and other interaction with the content, serve us with personalized content.
Wouldn't it be nice to have a ubiquitous service/platform where we can be explicit about the type of content we prefer and the system reflecting on it immediately?

This project is an attempt to address exactly that.

<hr>

# Introduction
SmartFeed.ai serves you every day with a collection of 5 articles related to topics you have subscribed, with the intent of keeping your feed interesting and worthwhile by aligning them to your preferences based on the explicit feedback given by you(user).
<hr>



# Components

There are 3 main components of the system

**Web-APP**
- It acts as a portal where the user interacts with the service.
- User is required to signup to the service with email (Firebase Handles authentication).
- User can subscribe and unsubscribe to different topics of choice.

**FeedManager**

A pipeline which Coordinates and Manages three integral components of the system

- Scraper: This service scrapes articles from medium daily for each topic.
- Recommendation Engine: It assigns a score for each article scraped, based on these scores recommendations are generated.
- Feed Sender: Sends the recommendations generated for each user to their respective emails.


**Slack Bot**
- Slack is being used as a medium for collecting user feedback.
- Subscription to slack is done during the signup process to the service.
- The slack workspace consists of favoured and unfavoured channels, where users can dump the links of the articles they've liked and the type of content you would want your feed to reflect.
- When a user pasts a link in the channel, the bot is triggered and the respective link along with the username of the user are written to the DB.
<hr>


	 
# How to use the Service
1. Signup to smartfeed.ai [here](https://smartfeed-ai.herokuapp.com/)


2.You would be receiving an email with an invitation to join the slack channel(make sure to use the same username used to subscribe).

![img](https://paper-attachments.dropbox.com/s_C44986F842155EEDF9274ADEA66CC474C9EBFA55B5A44BC9DDB17C60F799EA88_1589905059089_rsz_slack_subs.jpg)


3. Subscribe to the topics of choice,(highly recommended to limit it to no more than 3 Topics, as more than 15 articles a day just feels overwhelming).


4.Every day you would be receiving your feed as an email in and around 6:30(IST) in the morning from smartfeed.ai@gmail.com, which will have your feed of the day, a 300-word summary and keywords of the corresponding article, Which are intended to assist you in deciding whether to even consider opening the article or skip it.

![img](https://paper-attachments.dropbox.com/s_C44986F842155EEDF9274ADEA66CC474C9EBFA55B5A44BC9DDB17C60F799EA88_1589905071506_rsz_email.jpg)


5. If you happen to come across an article which you liked reading and would want your feed to reflect(source of the article can be from the feed sent to you or anywhere on the internet) then you can add the link to "favoured" channel on slack(sounds like quite a hassle to open slack and paste URL but Mobile OS makes it pretty handy ).

![img](https://paper-attachments.dropbox.com/s_C44986F842155EEDF9274ADEA66CC474C9EBFA55B5A44BC9DDB17C60F799EA88_1589905080083_pjimage.jpg)

Anywhere in your phone given slack is downloaded share option can be accessed.
<hr>



# Recommendation Engine Implementation

The underlining concept used resembles 'Content-Based Filtering' though it can be considered a hybrid approach.

A collection of articles being recommended per topic is simply not the top-5 articles closest to the one's user liked in the past rather they have some characteristics/properties as a set.

Articles have two primary attributes based on which they are included in the recommendations "Freshness" and "Similarity".


**Freshness** This attribute has two values/types
- **Archive Edition** its a collection of top articles for a tag from the past two years.
- **Daily Edition** its a collection of articles for a tag scrapped from medium the previous day.

<br>
**Similarity** This attribute also has two values/types, Based on the articles user liked in the past, there are two types(Details as to how this is calculated is presented in the next section
- **Parallel Articles** These articles are the one's which are most similar to the articles user liked in the past.
- **Perpendicular Articles** These articles are the one's which are most dissimilar articles(Topic wise) from which the user has liked in the past.

<br>
Following is the distribution of the number of articles over the categories

**Archive Edition: 2 articles**
- 1 Parallel article
- 1 Perpendicular article

**Daily Edition: 3 articles**
- 2 Parallel article
- 1 Perpendicular article

**Total of 5 articles per tag**


**Note** Reason the concept of perpendicular articles exists is to introduce novelty or diversify our exposure to different types of contents(in the same topic), failing to do so may lead to an echo chamber of preference.
<hr>


# Similarity Metric Design

Each article scrapped is assigned a score, This score is a weighted average of multiple -signals(number of claps, number of responses combined and Semantic similarity ) which indicates how likely user would find the article interesting(readable).

The final similarity score is the composition of ClapRespScore and Cosine Similarity score, each of which is computed as follows

**Number of Claps and Responses**

These two attributes of an article are being used as proxies to how popular the articles are.
- In medium, claps are similar to 'likes' with one major difference, each user can clap as many times as he/she wants, which makes it an unreliable as metric to measure popularity because of the pay model of medium to their writers (more about this here).
- Responses which are same as comments on any social media platform

Both the number of claps and responses are scaled using MinaxScaler to have a range between 0 to 1 and are combined with a weight of 70% for claps and 30% for comments and the resultant score is called ClapRespScore indicating the popularity of the article.

```ClapRespScore = (total_claps_scaled*0.7 + total_responses_scaled*0.3)```

<br>

**Cosine Similarity**

To use any distance metric, we need to convert articles(which is in textual form) to Feature Vectors(numerical form).

LDA(Latent Dirichlet Allocation) is being used to get extract or transform an article into a feature vector
- Simple techniques like TF-IDF and sophisticated one's like Doc2Vec were experimented with but they were not suitable for the given use case.
- LDA on a high level is an unsupervised learning algorithm which for given n topics(as hyperparameter) estimates the probability distribution for each article over these topics.
- So for each article, we would be getting a list of n-numbers each ranging from 0 to 1, we can consider this as a feature vector, where Basis vector in it represents the probability that the corresponding article belongs to a particular latent topic.
- As articles can be represented as feature vectors, it unlocks the concepts from linear algebra(like measuring similarity between vectors (articles) using various measures).

Cosine Distance is being calculated between the articles to determine their similarity(though there are other measures such as 'Nearest Neighbors' but for this use-case which requires us to compute articles which are unrelated (perpendicular articles) cosine would be mathematically intuitive.

<br>

**Combining Similarity and popularity score**

As mentioned in Recommendation engine design section, articles can be divided into two types based on the similarity metrics, Parallel and perpendicular.

Following are the ways used to compute parallel and perpendicular articles

<br>

**For Calculating Parallel Articles (ie: Most similar articles),**
- To obtain the most similar articles to the user's feedback, Following is the combination used

```Parallel_Article_rank = cosin_simmilarity*0.8+ClapRespScore*0.2```

<br>

**For Calculating Perpendicular Articles (Most Dissimilar)**
- Our objective is to get articles that are completely dissimilar from the one's user liked, For this, we can find an article whose feature vector is perpendicular to the one's user has liked.
- In case you're wondering why perpendicular vector indicates dissimilarity, a simple answer would be X-axis(horizontal line)and Y-axis(vertical line) are perpendicular to each other, there is no 'verticalness' /vertical aspect in the x-axis and no horizontalness/horizontal aspect in the y-axis,  which is reflected in the numerical representation of their vectors of [1,0] and [0,1] and the dot product of those two vectors is 0, indicating independence.
- We want articles with cosine distance of zero or close to zero, to obtain this we can simple subtract 1 from actual cosine similarity.

```Perpend_Article_rank = (1-cosin_simmilarity))*0.8+ClapRespScore*0.2```
<hr>



# Navigating Code

On higher-level chronological order to replicate the workflow reflects the chronology of the Directories

Since there are two distinct  types of Articles, Archive and Daily, Scraping and training for these articles are also different

Archive Articles are scrapped, trained once before deploying the model (updated once per year) and daily articles are scrapped and trained on the fly(Everyday)

**Setting up the environment**

- There are two ways to do it, either one of them can be followed

  - Installing packages

    ```bash
    pip install -r requirements.txt
    ```

  - Replicating the conda environment

    ```bash
    conda env create -f cnt-rec.yml
    ```

    

- 1_ScrapeArchive: Consists of scripts related to scraping the content of articles

  

- 2_TrainArchive: Consists of Scripts to train the model on archive data

  

- 3_SmartFeed: Consists of Service which is being deployed

  

- 4_FlaskApp: Consists of Web interface for users to singnup and subscribe to topics of choice

<hr>


# **Further Improvements**

- Currently, articles are being scraped only from medium, In future other regularly updated RSS feeds can be added as sources.

- The pipeline can be built which periodically analyzes user logs and mines some sought of patterns and trends.

- Based on the logs, users can be clustered and we can use the preferences of the median of each cluster for their respective cluster's recommendations.

- With sufficiently large user base Collaborative filtering can be a possibility.

- User conversations on slack channels can be monitored(with consent) and used in making recommendations.

- User-Dashboard can be embedded into web-App summarizing user favoured feeds periodically (monthly or weekly).

- Instead of just using explicit feedback in the form of article's URL's, user can be allowed to post other forms of content(You-tube Search history or web search history) from which latent features can be extracted and transformed to our vector space to enhance recommendations.

- Apart from the accuracy of our LDA model, we can track the emails sent to the user to identify his/her relative user interaction with recommended articles, this could be a good KPI(key performance indicator).
