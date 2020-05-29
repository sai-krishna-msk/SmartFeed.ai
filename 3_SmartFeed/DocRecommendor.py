import numpy as np 
import pandas as pd 
import warnings
from LDAModel import LDAModel
from ArticleParser import ArticleParser
from utils import getLogger
from scipy import spatial

logger = getLogger("Doc2VecReccomendor")

warnings.filterwarnings("ignore")

class DocRecommender:
    """ Recommendation engine of the Smart Feed, Given user information and Feed information Recommends Articles

    Args:
        user_profile(dict): Consists of User's username, Feedback(if any) and subscription details
        feature_matrix_daily(dict): Consists of required dates Feed information(link,text)

    Attributes:
        preproc(boolean): If preprocessing for the text is to be done or not
        tokenizer(Tokenizer): Regex tokenizer of nltk
        lemmatizer(WordNetLemmatizer): For lemmatization
        stop_words(set): Stop Words
        metric(str): Simmilarity metrics to compare embeddings of aticles
        recommendationDict(dict): Placeholder for our final recommendations
        arhive_log(dict): Stores which articles have we used up for the article from our archives
        recommendation_struct(dict): Number of Articles to be recommended for each edition and for each category
        user_feedback_profile(dict): Stores to which tag user feedback belongs to

    """
     
    def __init__(self, user_profile, feature_matrix_weekly, preproc=True):
        self.user_profile= user_profile
        self.preproc = preproc
        self.feature_matrix_weekly = feature_matrix_weekly
        self.recomendationsDict  = self._initRecommendationsDict()
        self.archive_log = {"link":list()}
        self.recommendation_struct={"archive":{"parallel":1, "perpendicular":1}, "daily":{"parallel":2, "perpendicular":1}}
        self.user_feedback_profile = self._builProfileRecommendations()


    def _initRecommendationsDict(self):

        RecommendationDict = {"archive":{}, "daily":{}}

        for tag in self.user_profile["subscriptions"]:
            RecommendationDict["archive"][tag] = list()
            RecommendationDict["daily"][tag] = list()

        return RecommendationDict


    def _getScore(self,text, tag):
        """  For a given text finds the cosine simmilarity of the closest text to it in given tag """
        model = LDAModel(mode='load' ,tag=tag, edition="archive")

        feature_vector = model.predict(text)
        scores = []
        for archive_feature in model.get_feature_vectors:
            scores.append(model.simmilarity_score(archive_feature , feature_vector))

        return max(scores)

    def _builProfileRecommendations(self):
        """Classifies user feedback into one of the tags based on the Cosine simmilarity of the closest article in each tag """
        user_feedback_profile = {}
        for tag in self.user_profile["subscriptions"]:
            user_feedback_profile[tag] = {"text":None}

        if("feedback" in self.user_profile):
            for feedback_link in self.user_profile["feedback"]:
                feedback_text = ArticleParser(feedback_link).fetchArticleText()
                simmilarity_score  = -2

                for tag in self.user_profile["subscriptions"]:

                    feedback_score = self._getScore(feedback_text, tag)

                    if( simmilarity_score < feedback_score):

                        if(not "score" in user_feedback_profile[tag]):

                            user_feedback_profile[tag] = {"text":feedback_text, "score":feedback_score}
                            simmilarity_score = feedback_score

                        elif(user_feedback_profile[tag]["score"]<feedback_score):

                            user_feedback_profile[tag] = {"text":feedback_text, "score":feedback_score}
                            simmilarity_score = feedback_score

        return user_feedback_profile



    def _cosine_simmilarity(self, curr_vector, comp_vector):

        return (1 - spatial.distance.cosine(curr_vector, comp_vector) )

    def _dot_product(self, curr_vector, comp_vector):

        return np.inner(curr_vector, comp_vector)




    def get_parallel(self, feature_matrix, simm_scores, n=1):
        """For Given list of article's cosine simmilarities, combines it with their popularity score and returns top n articles whose
        feature vectors are parallel(0 deg, ie:Methemetically most similar articles)"""
        top_articles = {"link":list(), "blog_score":list(), "ClapRespScore":list(), "score":list()}
        for link , ClapRespScore , score in zip(feature_matrix["link"], feature_matrix["ClapRespScore"],simm_scores):
            top_articles["link"].append(link)
            top_articles["ClapRespScore"].append(ClapRespScore)
            top_articles["blog_score"].append(score)
            top_articles["score"].append( (1*score)+(0*ClapRespScore) )

        return pd.DataFrame.from_dict(top_articles).nlargest(n, 'score')

    def get_perpendicular(self, feature_matrix, simm_scores, n=1):
        """For Given list of article's cosine simmilarities, combines it with their popularity score and returns top n articles whose
        feature vectors are perpendicular(90 deg, ie:Methemetically most dissimilar articles) """
        top_articles = {"link":list(), "blog_score":list(), "ClapRespScore":list(), "score":list()}
        for link , ClapRespScore , score in zip(feature_matrix["link"], feature_matrix["ClapRespScore"],simm_scores):
            perp_score = 1-score
            top_articles["link"].append(link)
            top_articles["ClapRespScore"].append(ClapRespScore)
            top_articles["blog_score"].append(perp_score)
            top_articles["score"].append( (1*perp_score) + (0*ClapRespScore)  )

        return pd.DataFrame.from_dict(top_articles).nlargest(n, 'score')

    # def get_opposite(self, feature_matrix, simm_scores, n=1):
    #     """For Given list of article's cosine simmilarities, combines it with their popularity score and returns top n articles whose
    #     feature vectors are opposite(180 deg, ie:Methemetically most complimentory articles) """
    #     top_articles = {"link":list(), "blog_score":list(), "ClapRespScore":list(), "score":list()}
    #     for link , ClapRespScore , score in zip(feature_matrix["link"], feature_matrix["ClapRespScore"],simm_scores):
    #         top_articles["link"].append(link)
    #         top_articles["ClapRespScore"].append(ClapRespScore)
    #         top_articles["blog_score"].append(score)
    #         top_articles["score"].append( (0.8*(-1*score))+(0.2*ClapRespScore) )

    #     return pd.DataFrame.from_dict(top_articles).nlargest(n, 'score')


    def _getSimmScores(self, text, tag, edition):
        """For given article find the cosine simmilairty scores with respective to all other articles of the corresponsing tag and edition """
        model = LDAModel(mode='load',tag=tag, edition=edition)
        simm_scores = []

        text_feature = model.predict(text)
        for feature in model.get_feature_vectors:
            simm_scores.append(self._cosine_simmilarity(text_feature, feature))

        return simm_scores


    def _updateLog(self, user,tag):
        """ 
        Update which articles have been sent out to user Check is user exist if yes then put one at article which  has been sent, If user does not exist then create a new user
        """
        feature_matrix = pd.read_csv(f"feature_matrices/{tag}.csv")

        if(user not in feature_matrix.columns):

            feature_matrix[user] = feature_matrix["link"].apply(lambda x: 1 if( x in self.archive_log["link"]) else 0)

        else:
            feature_matrix[user] = feature_matrix.apply(lambda row: 1 if( row.link in self.archive_log["link"] ) else row[user], axis=1  )
            
        feature_matrix.to_csv(f"feature_matrices/{tag}.csv", index=False)

    def _getArchiveFeatureMatrix(self, user, tag):
        """
        return the list of archive links of a tag, excluding links already sent
        """
       
        feature_matrix = pd.read_csv(f"feature_matrices/{tag}.csv")

        if(user in feature_matrix.columns.values):

           
            feature_matrix = feature_matrix[feature_matrix[user]==0]
            return feature_matrix

        return feature_matrix


    def _getRecommendations(self,  edition, feature_matrix_dict=None ):
        """
        For each tag user has subscribed to get recommendations
        """
        

        for tag  in self.user_profile["subscriptions"]:
            if(not tag):
                continue
            logger.info(f"Generating {tag} tag recommendations for {self.user_profile['username']} {edition} edition")


            if(edition=='daily'):

                feature_matrix = pd.DataFrame(feature_matrix_dict[tag]["content"])

            elif(edition=='archive'):
                feature_matrix= self._getArchiveFeatureMatrix(self.user_profile["username"], tag)

            
            if(self.user_feedback_profile[tag]["text"]):


                simm_score  = self._getSimmScores(self.user_feedback_profile[tag]["text"], tag, edition)


                df_parallel = self.get_parallel(feature_matrix , simm_score, n= self.recommendation_struct[edition]["parallel"])
                parallel_link = df_parallel["link"].values.tolist()
                
                df_perpend = self.get_perpendicular(feature_matrix , simm_score, n=self.recommendation_struct[edition]["perpendicular"])
                perpend_link = df_perpend["link"].values.tolist()


            else:
                # User having no preference

                parallel_link = feature_matrix.nlargest(self.recommendation_struct[edition]["parallel"], "ClapRespScore")["link"].values.tolist()
                
                text  = ArticleParser(parallel_link[0]).fetchArticleText()




                simm_score = self._getSimmScores(text, tag , edition)

                df_perpend = self.get_perpendicular(feature_matrix , simm_score, n=self.recommendation_struct[edition]["perpendicular"])
                perpend_link = df_perpend["link"].values.tolist()

            

            for link in parallel_link:  self.recomendationsDict[edition][tag].append(link)

            for link in perpend_link:   self.recomendationsDict[edition][tag].append(link)

            if(edition=='archive'):
                for link in parallel_link:  self.archive_log["link"].append(link)
                for link in perpend_link:   self.archive_log["link"].append(link)
                self._updateLog(self.user_profile["username"],tag)



    def genRecommendations(self):
        """ Calls all the functions in proper order and returns the recommendations """
        self._getRecommendations( 'daily', self.feature_matrix_weekly)
        self._getRecommendations("archive")
        
        return self.recomendationsDict


