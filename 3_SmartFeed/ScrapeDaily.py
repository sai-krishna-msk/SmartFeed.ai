import requests 
from bs4 import BeautifulSoup
from calendar import monthrange
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


from utils import getLogger
from ArticleParser import ArticleParser

logger = getLogger("ScrapeDaily")

class ScrapeDaily:
    """Scrapes Articl's metada for a given tag and a date

    Args:
        tag(str): Name of the tag
        date(str): Date of article's to be scraped

    Attributes:
        scrape_class(str): Value for class of div which contains the metadata
        url(str): URL where collection of article's for given date are present
        data_sict(dict): Placeholder for metadata we are about to scrape

     """
    def __init__(self,tag, date):
        self.tag = tag
        self.date = self._getValidDate(date) 
        self.scrape_class="streamItem streamItem--postPreview js-streamItem"
        self.url  =f"https://medium.com/tag/{self.tag}/archive/{self.date}"
        self.data_dict = {"link":list(), "total_claps":list(), "total_responses":list(), "text":list()}



  

    def _getValidDate(self, date):
        return date 

    def _get_total_claps(self, card):
        """ Get total claps for the article """
        try:
            claps = card.find("button",{"class":"button button--chromeless u-baseColor--buttonNormal js-multirecommendCountButton u-disablePointerEvents"}).text
            return claps
        except:
            return False

    def _get_total_responses(self, card):
        """ Get total responses for the article """
        try:
            responses = card.find("a", {"class":"button button--chromeless u-baseColor--buttonNormal"}).text
            return responses

        except:
            return False

    def _get_link(self, card):
        """ Get link of the article """
        try:
            link = card.find("a", {"class":'link link--darken' })["data-action-value"]
            return link

        except:
            return False

    def _cntComment(self, card):
        """ checks if the current card is an article or a comment(False incase of a comment) """
        resp = card.findAll("div", {"class":"u-textDarker u-noWrapWithEllipsis"})
        if(resp):
            return True 
        return False 

    def _parse_link(self, link):
        """ Parses the link, removing the source as archive """
        try:
            return link.split("?")[0]
        except:
            return link

    def _parse_claps(self, claps):
        """ Converts Claps which is in string as K for thousands into integer"""
        try:
            if("," in claps):
                claps = claps.replace(",","")

            if("K" in claps):
                num = float(claps.split("K")[0])
                return int(num*1000)

            if("k" in claps):
                num = float(claps.split("k")[0])
                return int(num*1000)
            return int(claps)
        except:
            return claps

    def _parse_responses(self, responses):
        """ Parses number of responses from string to integer"""
        try:
            if(responses==0):
                return responses
            return self._parse_claps(responses.split(" ")[0])
        except:
            return responses


    def _extract(self):
        """ extract each article's metadata from the url """
        logger.info(f"Extracting {self.tag} content of date: {self.date}")
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')
        for i,card in enumerate((soup.findAll("div", {"class": self.scrape_class}))):

            if(not self._cntComment(card)):

                link = self._get_link(card)
                
                if(link):
                    total_claps = self._get_total_claps(card)
                    if(not total_claps):
                        total_claps =1
                    else:
                        total_claps = self._parse_claps(total_claps)+1

                    total_responses = self._get_total_responses(card)
                    if( not total_responses):
                        total_responses = 1
                    else:
                        total_responses=self._parse_responses(total_claps)+1
                    try:
                        parsed_article = ArticleParser(link)
                        self.data_dict["total_responses"].append(total_responses)
                        self.data_dict["link"].append(self._parse_link(link))
                        self.data_dict["total_claps"].append(total_claps)
                        self.data_dict["text"].append(parsed_article.fetchArticleText())
                    except Exception as e:
                        logger.error(f'Failed to download {link} article: {e}')

        logger.info(f"successfully Extracted {self.tag}")
        

    def _scoreFeed(self, clap_percent=0.7, response_percent=0.3):
        """"
        creates a metric which is a combination of total claps and responses
        Giving us popularity of the article 
        """
        data_dict_df = pd.DataFrame.from_dict(self.data_dict)
        data_dict_df['total_claps_scaled'] = np.nan
        data_dict_df['total_responses_scaled'] = np.nan
        data_dict_df['ClapRespScores'] = np.nan

        scaler = MinMaxScaler()
        data_dict_df[["total_claps_scaled", "total_responses_scaled"]] =  scaler.fit_transform(
                                                                                        data_dict_df[["total_claps","total_responses"]]
                                                                                                            )

        data_dict_df["ClapRespScore"] = ((data_dict_df["total_claps_scaled"]*clap_percent) + (data_dict_df["total_responses_scaled"]*response_percent))



        
       
        # self.data_dict=  {"links":data_dict_df["link"].values.tolist(), "ClapRespScore":data_dict_df["ClapRespScore"].values.tolist(),
        #                 "text":data_dict_df["text"].values.tolist(),}

        return data_dict_df

    def _filter(self, df):

        clap_25 = np.quantile(df.total_claps.values.tolist(), 0.25)
        quant_25 = df[df['total_claps']>clap_25]

        quant_25.drop(['total_claps', 'total_responses'], axis=1, inplace=True)

        return quant_25



    def getFeed(self):
        """ Performs all operations in order """
        self._extract() 

        self.data_dict  = self._scoreFeed()

        self.data_dict = self._filter(self.data_dict)

        
        return self.data_dict

