# **SmartFeed.ai**

 *[Content Recommendation System](https://smartfeed-ai.herokuapp.com/)*

# **Contents**

- [Problem Statement](#problem-statement)
- [Introduction](#introduction)
- [How to use Platform](#how-to-use)
- [Methodology](#methodology)
- [Navigating Code](#navigating-code)
- [Further Improvements](#further-improvements)

<hr>

# **Problem Statement**

*Scarcity of information is as bad as Excess of it* 

 Sheer Volume of newsletters which flood our inboxes overwhelms us into not sticking with the habit of reading

 

Though there are implicit feedback mechanism on Reading Website Which based on your read-time and others interaction  filter out personalized content for you, Wouldn't it be nice to have ubiquitous service/platform where we can explicitly tell a service the type of content their recommendations for us should reflect and have these delivered the very next day

This  project is an attempt addressing this.

<hr>

# **Introduction** 

**SmartFeed.ai** is a Article  Recommendation System, which serves you everyday with a collection of articles related to Topics you have subscribed,(5 Articles per topic).

The way it comes up with those 5 articles is with the objective to ensure keeping you reading feed interesting and worthwhile by aligning them to your preferences based on the explicit feedback given by the you(the user).

## **Characteristics of these 5 five articles**

Articles are divided based on two factors freshness and similarity

**Freshness** : 

- There are two categories of articles you get for each tag/topic

- -  Archive edition
  - Daily-edition 

- Archive Edition is a collection of all articles for a tag from past two years

- Daily Edition is a collection of articles for a tag from the previous day

**Similarity:**  

- Based on the articles user liked in the past, there are two types

- - **Parallel Articles** 
  - **Perpendicular Articles** 

- Parallel articles are the one's which are most similar to the articles you have liked

- Perpendicular articles are the one's which are most dissimilar articles(Topic wise) from which you have liked

If you're wondering about the names(parallel and perpendicular), They have to do with the fact that similarity is being calculated based on the cosine angle between the feature vectors of the articles(You can find out more about technicalities in the methodology section)

Following are the distribution of number of articles over the categories 

```
|   | parallel | perpendicular |
|----------|----------|---------------|
| Archive  | 1  | 1   |
| Daily  | 2  | 1   |
```

**Note** The reason we have concept of perpendicular articles is to introduce novelty or diversify our exposure to different topics, failing to do so may lead to a echo chamber of preference.

<hr>

# **How to use Platform**

1. Signup to smartfeed.ai [here](https://smartfeed-ai.herokuapp.com/signup)

   

1. Subscribe to the topics,(*Highly recommended to limit it to no more than 3 Topics ,as more than 15 articles a day just feels overwhelming*)

   

1. You would be receiving an email with an invitation to join the slack channel(make sure to use the same username used to subscribe), This is the medium chosen to get explicit feedback from you(the user)

![img](https://paper-attachments.dropbox.com/s_C44986F842155EEDF9274ADEA66CC474C9EBFA55B5A44BC9DDB17C60F799EA88_1589905059089_rsz_slack_subs.jpg)



4. Everyday you would be receiving your feed as an email in and around 6:30(IST) in the morning from [smartfeed.ai@gmail.com](mailto:smartfeed.ai@gmail.com), which will have your feed of the day

![img](https://paper-attachments.dropbox.com/s_C44986F842155EEDF9274ADEA66CC474C9EBFA55B5A44BC9DDB17C60F799EA88_1589905071506_rsz_email.jpg)

300 word Summary and keywords of the corresponding article are intended to assist you in deciding whether to open the article or skip it

 

 

5. If you come across an article which you liked reading and would want your feed to reflect this type of articles(it can be from the feed sent to you  or anywhere on the internet) then you can add the link to “favored” channel on slack(sounds like quite a hassle to open slack and paste url but Android makes it pretty handy )

![img](https://paper-attachments.dropbox.com/s_C44986F842155EEDF9274ADEA66CC474C9EBFA55B5A44BC9DDB17C60F799EA88_1589905080083_pjimage.jpg)

Any where in your phone given slack is downloaded share option can be accessed  from gmail, chrome, WhatsApp

<hr>

# Methodology

There are 4 components of our system

- **Scrapping Bot**

- **Slack Bot**

- **Recommendation Engine**

- **Flask Web-app**

- **Firebase real-time database**

## Scrapping Bot

- A bot which scrapes articles everyday for each tag/topic given to it

## Slack Bot

- There are specific Channels in slack Assigned for User Feedback named favoured and unfavoured

- Dumping Links in either of those would forward these articles to the database with timestamp of dump and user who did so

## Recommendation Engine

- The underlining concept used resembles Content Based Filtering, though it can be considered hybrid approach

- Each article scrapped is assigned a score, This score is a weighted average of multiple - signals(Semantic similarity and  number of claps ,responses combined ) which indicates how likely you would find the article interesting(readable)

**Claps and responses**

- In medium Claps are similar to likes with one radical difference which is each user can clap as many times as he/she wants, Which makes it a unreliable as metric to measure popularity because of the pay model of medium to their writers (more about this [here](https://help.medium.com/hc/en-us/articles/213477928-Medium-Rules))

- Responses which are same as comments(as we know it)

**Both the number of claps and responses are Scaled using MinaxScaler to have arange between 0 to 1 and are combined with 50%/0.5 weight of each**

```
ClapRespScore = (total_claps_scaled*0.5 + total_responses_scaled*0.5)
```

**Semantic Similarity** 

LDA(Latent Dirichlet Alocation) has been used to extract features from the article

- Techniques like simple(TF-IDF) and more sophisticated like Doc2Vec were experimented with  but they were not suitable for the given use case

- LDA on high level is an unsupervised learning algorithm which for given n topics(as hyperparameter)  tries to estimate probability distribution of each article over these topics, So for each article we would be getting a list of n-numbers ranging from 0 to 1, we can consider this as a feature vector

- Each article would be mapped with a feature vector where each basis vector in it is a probability that this articles belongs to this topic, As it is fair to interpret these probability distribution as a vector we can exploit concepts from linear algebra(Like measuring similarity between vectors (articles) using various measures)

- Cosine Distance is being calculated between the articles to determine their similarity(Though there are other measures such as Nearest Neighbors which uses of Euclidean distance. but for our use case of also getting topics which are completely unrelated(perpendicular articles as we call them) cosine would make a lot more sense mathematically)

**Combining Cosine similarity with ClapRespScore**

**For** **Calculating** **Parallel Articles** (ie: Most similar articles), 

- To obtain the most similar articles to the users feedback, Following is the combination used

```
Parallel_Article_rank = cosin_sim*0.8+ClapRespScore*0.2
```

**For Calculating Perpendicular Articles** **(Most** **Dissimilar)**

- Our objective is get articles which are completely  dissimilar from the one’s user liked(reason is mentioned above),  For this we can find article whose feature vector is perpendicular to user’s liked article .

- In case you're wondering why perpendicular vector indicate dissimilarity a simple answer would be , X(Horizontal line)and Y(Vertical) axis are perpendicular to each other, there is no 'verticalness' in x-axis and horizontal aspect in y-axis which is reflected in the numerical representation of their vectors of [1,0] and [0,1] Representing independence 

- We want articles with cosin distance of zero or close to zero, to obtain this we can simple subtract 1 from actual cosine similarity 

```
Perpend_Article_rank = (1-cosin_sim))*0.8+ClapRespScore*0.2
```

## Flask-Web-App

- Acts as an interface allowing users to subscribe,unsubscribe to the topic/tags

## Firebase Real-time DB

- Its the most easy to use and setup NO-SQL Cloud based Database, Which being used for
- Authentication 
- Storing User details
- Store User subscriptions, 
- Store Feedback from users 
- As log of articles being sent to user each day(for further analysis)

<hr>

# Navigating Code

On higher level chronological order to replicate the workflow reflects the chronology of the Directories

Since there are two distinct  types of Articles, Archive and Daily, Scraping and training for these articles are also different

Archive Articles are scrapped , trained once before deploying the model (updated once per year) and daily articles are scrapped and trained on the fly(Everyday)

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

  

- 4_FlaskApp: Consists of Web interface for users to singup and subscribe to topics of choice

<hr>

# **Further Improvements**

- Currently Articles are being scraped only from medium, In future other regularly updated RSS feeds can be added

- Pipeline can be built which periodically analyzes user logs and mines some sought of patterns and trends

- Given sufficiently large users 

- - based on the logs user's can be clustered and we can use the preferences of  median of each cluster for their respective cluster's recommendations
  - Collaborative filtering also could be implemented

- User conversations on slack channels can be monitored and used in making recommendations(with consent)

- User Dashboard can be embedded into Web-App summarizing user favored feeds periodically (monthly or weekly)

- Instead of just using explicit feedback in form of article url's, user can be allowed to post other form of content(You-tube Search history or web search history) from which latent features can be extracted and transformed to our vector space to enhance recommendations

- Apart from the accuracy of our LDA model we can track the emails sent to user to identify his/her relative user interaction with recommended articles, this could be a good KPI(key performance indicator)

<hr>
