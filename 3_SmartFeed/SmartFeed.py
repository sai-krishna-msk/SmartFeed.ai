from datetime import datetime, timedelta
import time
import pyrebase

import schedule

from config import args
from utils import getLogger
from ScrapeDaily import ScrapeDaily
from LDAModel import LDAModel
from DocRecommendor import DocRecommender
from FeedSender import FeedMail
logger = getLogger("FeedRecommendor")

class SmartFeedManager:
    """ Manages all the operations of the smart feed 
    Agrs:
        cloud_config(dict): Consists of necessory keys to access DataBase as admin

    Properties:

        db(pyrebase obj): Database object
        users(dict): Consists of User details 
        tags(dict): Consists of tag details
        daily_feed(dict): Place holder for current date's feed 
        date(datetime obj): Current Date's object
    """

    def __init__(self, cloud_config):
        self.db = self._initCloudBD(cloud_config)
        self.users= self._load_user_details()
        self.tags = self._load_tags_info()
        self.dailyFeed = self._initDailyFeed()
        self.date= (datetime.now() - timedelta(days=2))


    def _initCloudBD(self, cloud_config):
        """
        Initializes Cloud Configuation
        returns database object
        """
        try:
            firebase = pyrebase.initialize_app(cloud_config)
            db = firebase.database()
            logger.info("Successfully Connection Establishes with DB")
        except Exception as e:
            logger.error(f"Failed to Establish Connection with DB: {e}")

        return db


    def _load_user_details(self):
        """
        load User subscription details
        
        """
        try:
            users = (self.db.child("UserDetails").get()).val()
            logger.info("loaded user subscription details to cloud")
            return users
        except Exception as e:
            logger.error(f"Failed to load user subscription details to cloud: {e}")


    def _load_tags_info(self):
        """
        Load Publication Details
        """
        try:
            tags = (self.db.child("TagRecords").get()).val()

            logger.info("loaded Tags Information Successfully to cloud")
            return tags

        except Exception as e:

            logger.error(f"Failed to load Tags Information to cloud: {e}")



    def _initDailyFeed(self):
        """ Create current date's feed placeholder to hold scrapped article's info"""
        daily_feed={}
        for tag in self.tags:
            

            for user in self.users:
                if('subscriptions' in self.users[user] and tag in self.users[user]['subscriptions']):
                    daily_feed[tag]= {}

                    if(not "recipients" in daily_feed[tag]):
                        daily_feed[tag]['recipients'] = {"recipients_email":list(), "recipients_username":list()}

                    daily_feed[tag]['recipients']['recipients_username'].append(self.users[user]['SlackUsername'])
                    daily_feed[tag]['recipients']['recipients_email'].append(self.users[user]['email'])
                   

        return daily_feed




    def dailyScrape(self):
        """Starts Scraping articles of tag's which user's are subscribed to"""
        date = str(self.date.strftime("%Y/%m/%d"))
        for tag in self.tags:
            if( tag in self.dailyFeed ):
                logger.info(f"Scrapping {tag} tag ")
                obj = ScrapeDaily(tag, date)
                self.dailyFeed[tag]["content"] = obj.getFeed()

    

    def dailyTrain(self):
        """ Traines a Doc2Vec model for each tag's articles""" 
        for tag in self.tags:
            if(tag in self.dailyFeed):
                model = LDAModel(mode = 'train', texts = self.dailyFeed[tag]["content"]["text"].values.tolist(), tag=tag, edition='daily', )
                model.train(n_topics=100)
                logger.info(f"Training Accuracy of {tag} is {model.evaluate()}")
                model.save()


    def _getUserProfile(self, UserDetails):
        """ Extract User's previous day's feedback info"""

        curr_date = str(self.date.strftime("%m-%d-%Y"))
        userProfile = {"username":str(), "subscriptions":list(), "feedback":list()}
        userProfile["username"] = UserDetails["SlackUsername"]
        userProfile["subscriptions"] = [tag for tag in UserDetails["subscriptions"] if(tag) ]

        feedback_list = self.db.child("favoured_feed").child(userProfile["username"]).get().val()

        if(feedback_list):
            for date in feedback_list:
                if(date.startswith(curr_date)):
                    userProfile["feedback"].append(feedback_list[date]["url"])

        return userProfile


    def getRecommendations(self):
        """Based on the previous days user's feedbakc and current day's aticles get reccomendations for each user """
        logger.info("Getting getRecommendations")
        for user in self.users:

            if("subscriptions" in self.users[user]):

                userProfile = self._getUserProfile(self.users[user])

                obj = DocRecommender(userProfile , self.dailyFeed)

                self.users[user]["recommendations"] =  obj.genRecommendations()


    def sendFeed2Users(self):
        """ Send the recommended feed to user via email"""
        logger.info("Sending Feed to Users")
        for user in self.users:
            if("subscriptions" in self.users[user]):
                mail_obj = FeedMail( self.users[user]["email"], self.users[user]["recommendations"])
                mail_obj.pushEmail()
      

    def Log2Cloud(self):
        """ Log the recommendations send to user to the cloud """
        logger.info("Logging Recommendations to Cloud")
        date =  str(self.date.strftime("%m-%d-%Y"))

        for user in self.users:
            if("subscriptions" in self.users[user]):
                try:
                    self.db.child("DailyFeedLog").child(date).child(self.users[user]["SlackUsername"]).set(self.users[user]["recommendations"])
                    logger.info(f"Successfully Logged {user} recommendations to cloud")
                except Exception as e:
                    logger.error(f"Failed to push recommendations log of {user} to cloud")

                


def run_smartFeed():
    """ Scheduler uses this function call to intiate the process at fixed time everyday"""
    smartFeed_obj = SmartFeedManager(args["cloud_config"])
    smartFeed_obj.dailyScrape()
    smartFeed_obj.dailyTrain()
    smartFeed_obj.getRecommendations()
    smartFeed_obj.sendFeed2Users()
    smartFeed_obj.Log2Cloud()



schedule.every().day.at("06:10").do(run_smartFeed)


while True:
    schedule.run_pending()
    time.sleep(1)


# run_smartFeed()


