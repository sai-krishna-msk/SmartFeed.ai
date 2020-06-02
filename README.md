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
Scarcity of information is equally  bad as Excess of it

Sheer Volume of newsletters which flood our inboxes overwhelms us into not sticking with the habit of reading

Though there are implicit feedback mechanism on Reading Website Which based on your read-time and others interaction filter out personalized content for you, Wouldn't it be nice to have ubiquitous service/platform where we can explicitly tell a service the type of content their recommendations for us should reflect and have these delivered the very next day

This project is an attempt to address it.

<hr>

# Introduction
SmartFeed serves users every day with a collection of articles related to topics you have subscribed,(5 Articles per topic),  with the objective to ensure keeping you reading feed interesting and worthwhile by aligning them to user preferences based on the explicit feedback given.

<hr>


	 
# How to use the Service
1. Signup to smartfeed.ai [here](https://smartfeed-ai.herokuapp.com/signup)

   

2. Subscribe to the topics,(*Highly recommended to limit it to no more than 3 Topics ,as more than 15 articles a day just feels overwhelming*)

   

3. You would be receiving an email with an invitation to join the slack channel(make sure to use the same username used to subscribe), This is the medium chosen to get explicit feedback from you(the user)
![img](https://paper-attachments.dropbox.com/s_C44986F842155EEDF9274ADEA66CC474C9EBFA55B5A44BC9DDB17C60F799EA88_1589905059089_rsz_slack_subs.jpg)



4. Every day you would be receiving your feed as an email in and around 6:30(IST) in the morning from [smartfeed.ai@gmail.com](mailto:smartfeed.ai@gmail.com), which will have your feed of the day, a  300-word Summary and keywords of the corresponding article are intended to assist you in deciding whether to open the article or skip it

![img](https://paper-attachments.dropbox.com/s_C44986F842155EEDF9274ADEA66CC474C9EBFA55B5A44BC9DDB17C60F799EA88_1589905071506_rsz_email.jpg)

- If you happen to come across an article which you liked reading and would want your feed to reflect this type of articles(it can be from the feed sent to you  or anywhere on the internet) then you can add the link to “favored” channel on slack(sounds like quite a hassle to open slack and paste URL but Android makes it pretty handy )

![img](https://paper-attachments.dropbox.com/s_C44986F842155EEDF9274ADEA66CC474C9EBFA55B5A44BC9DDB17C60F799EA88_1589905080083_pjimage.jpg)

Anywhere in your phone given slack is downloaded share option can be accessed  from gmail, chrome, WhatsApp

<hr>

# Components
There are 5 components of the system

* Flask Web-APP 

    * For users to signup and subscribe to related topics

* Slack Bot 

    * To collect user feedback and push it to the database

* Scraper 

    * which scrapes medium articles every day for each tag 

* Recommendation Engine

	*  It assigns a score for each article scraped and generates 
    recommendations based on these scores(Detailed procedure is mentioned below)

* Feed Sender 

     * which sends the recommendations generated for each 
   user to their respective emails 
	 

<hr>


# Recommendation Engine Implementation
5 Articles being sent to users are simple not just the Top-5 most similar articles user liked in the past, They have the following characteristics

Articles are divided based on two factors freshness and similarity

**Freshness** : 

There are two categories of articles you get for each tag/topic

- Archive edition, Its a collection of all articles for a tag from the past two years

- Daily-edition, its a  is a collection of articles for a tag from the previous day

**Similarity**  

Based on the articles user liked in the past, there are two types

- **Parallel Articles** :  These  articles are the one's which are most similar to the articles you have liked

- **Perpendicular Articles** : These articles are the one's which are most dissimilar articles(Topic wise) from which you have liked


Following are the distribution of the number of articles over the categories 

**Archive Edition: 2 articles**

- 1 Parallel article
- 1 Perpendicular article

**Daily Edition: 3 articles**

- 2 Parallel article
- 1 Perpendicular article

<br>



**Note** The reason the  concept of perpendicular articles exists is to introduce novelty or diversify our exposure to different topics, failing to do so may lead to an echo chamber of preference.

<br>

**The underlining concept used resembles Content-Based Filtering, though it can be considered a hybrid approach**

Each article scrapped is assigned a score, This score is a weighted average of multiple - signals(Semantic similarity and  number of claps ,responses combined ) which indicates how likely user would find the article interesting(readable)

**Claps and responses**

- In medium Claps are similar to likes with one major difference, Each user can clap as many times as he/she wants, Which makes it an unreliable as metric to measure popularity because of the pay model of medium to their writers (more about this [here](https://help.medium.com/hc/en-us/articles/213477928-Medium-Rules))

- Responses which are same as comments(as we know it on other platforms)

Both the number of claps and responses are Scaled using MinaxScaler to have a range between 0 to 1 and are combined with a weight of 70% for claps and 30% for comments and the resultant score is called ClapRespScore indicating the popularity of the article

```
ClapRespScore = (total_claps_scaled*0.7 + total_responses_scaled*0.3)
```

<br>

**Topic Similarity** 

LDA(Latent Dirichlet Allocation) has been used to extract features from the article

- Techniques like simple(TF-IDF) and more sophisticated like Doc2Vec were experimented with  but they were not suitable for the given use case

- LDA on a high level is an unsupervised learning algorithm which for given n topics(as hyperparameter)  tries to estimate the probability distribution of each article over these topics, So for each article, we would be getting a list of n-numbers ranging from 0 to 1, we can consider this as a feature vector

- Each article would be mapped with a feature vector where each basis vector in it is a probability that this article belongs to this topic, As it is fair to interpret these probability distribution as a vector we can exploit concepts from linear algebra(Like measuring similarity between vectors (articles) using various measures)

- Cosine Distance is being calculated between the articles to determine their similarity(Though there are other measures such as Nearest Neighbors which uses Euclidean distance. but for our use case of also getting topics which are completely unrelated(perpendicular articles as we call them) cosine would make a lot more sense mathematically)

<br>

#### **Combining Cosine similarity(Topic similarity) with ClapRespScore(Popularity Score)**

<br>


**For** **Calculating** **Parallel Articles** (ie: Most similar articles), 

- To obtain the most similar articles to the user's feedback, Following is the combination used

```
Parallel_Article_rank = cosin_sim*0.8+ClapRespScore*0.2
```

<br>

**For Calculating Perpendicular Articles** **(Most** **Dissimilar)**

- Our objective is to get articles that are completely  dissimilar from the one’s user liked(the reason is mentioned above),  For this we can find an article whose feature vector is perpendicular to the user’s liked article.

- In case you're wondering why perpendicular vector indicate dissimilarity a simple answer would be ,X(Horizontal line)and Y(Vertical) axis are perpendicular to each other, there is no 'verticalness' in the x-axis and horizontal aspect in y-axis which is reflected in the numerical representation of their vectors of [1,0] and [0,1] Representing independence 

- We want articles with cosine distance of zero or close to zero, to obtain this we can simple subtract 1 from actual cosine similarity 

```
Perpend_Article_rank = (1-cosin_sim))*0.8+ClapRespScore*0.2
```

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

- Currently, Articles are being scraped only from medium, In future other regularly updated RSS feeds can be added

- Pipeline can be built which periodically analyzes user logs and mines some sought of patterns and trends

- Given sufficiently large users 
	- based on the logs user's can be clustered and we can use the preferences of  median of each cluster for their respective cluster's recommendations
	-  Collaborative filtering also could be implemented

- User conversations on slack channels can be monitored and used in making recommendations(with consent)

- User Dashboard can be embedded into Web-App summarizing user favored feeds periodically (monthly or weekly)

- Instead of just using explicit feedback in form of article URL's, user can be allowed to post other form of content(You-tube Search history or web search history) from which latent features can be extracted and transformed to our vector space to enhance recommendations

- Apart from the accuracy of our LDA model we can track the emails sent to the user to identify his/her relative user interaction with recommended articles, this could be a good KPI(key performance indicator)



