import requests
import pandas as pd
import numpy as np


import dropbox
import logging

from bs4 import BeautifulSoup
from calendar import monthrange


class ExtractArchive:
    """Extract Archive Articles given Tag and year
    """

    def __init__(self, tags, years, dropbox_token):
        """

        Arguments:
            tags {str/list} -- Name of the tags to be scrapped
            years {int/list} -- Corresponding Years to be Scrapped
            dropbox_token {str} -- DropBox token
        """

        if(isinstance(years, list)):
            self.years = years
        else:
            self.years = [years]

        if(isinstance(tags, list)):
            self.tags = tags
        else:
            self.tags = [tags]
        self.dropbox_token = dropbox_token
        self.logger = self._getLogger('ExtractArticlesLogger')

    def _getLogger(self, name, level=logging.INFO):
        """Initiates a logger

        Arguments:
            name {str} -- Name of the logger

        Keyword Arguments:
            level {str} -- Levek of logger (default: {logging.INFO})

        Returns:
            loggin.logger -- logger object
        """
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        logger = logging.getLogger(name)
        handler_console = logging.StreamHandler()
        handler_console.setFormatter(formatter)
        logger.addHandler(handler_console)
        logger.setLevel(level)

        return logger

    def _get_total_claps(self, card):
        try:
            claps = card.find("button", {
                "class": "button button--chromeless u-baseColor--buttonNormal js-multirecommendCountButton u-disablePointerEvents"}).text
            return claps
        except:
            return False

    def _get_total_responses(self, card):
        try:
            responses = card.find(
                "a", {"class": "button button--chromeless u-baseColor--buttonNormal"}).text
            return responses

        except:
            return False

    def _get_link(self, card):
        try:
            link = card.find(
                "a", {"class": 'link link--darken'})["data-action-value"]
            return link

        except:
            return False

    def _cntComment(self, card):
        """Checks if the given card belongs to a article or a comment

        Arguments:
            card { bs4 } -- Parsed HTML, of an article

        Returns:
            boolean -- True of a comment card or False
        """
        resp = card.findAll(
            "div", {"class": "u-textDarker u-noWrapWithEllipsis"})
        if(resp):
            return True
        return False

    def _parse_link(self, link):
        """Removes the part of article indicating to source

        Arguments:
            link {str} -- link

        Returns:
            str -- parsed link
        """
        try:
            return link.split("?")[0]
        except:
            return link

    def _parse_claps(self, claps):
        """Given String format of numbers, k for thousand convert into int

        Arguments:
            claps {str} -- String Format of claps

        Returns:
            int -- total claps in numeric form
        """
        try:
            num = claps
            if("," in claps):
                claps = claps.replace(",", "")

            if("K" in claps or "k" in claps):
                if("K" in claps):
                    num = float(claps.split("K")[0])
                else:
                    num = float(claps.split("k")[0])
                return int(num*1000)

            elif("M" in claps or "m" in claps):
                if("M" in claps):
                    num = float(claps.split("M")[0])
                else:
                    num = float(claps.split("m")[0])
                return int(num*1000000)
        except:
            return claps

    def _parse_responses(self, responses):
        try:
            if(responses == 0):
                return responses
            return self._parse_claps(responses.split(" ")[0])
        except:
            return responses

    def _ExtractMonthly(self, tag, year, month):
        data_dict = {"link": list(), "total_claps": list(),
                     "total_responses": list()}
        class_ = "streamItem streamItem--postPreview js-streamItem"
        start_day = monthrange(year, month)[0]
        end_day = (monthrange(year, month)[1])+1
        if(month < 10):
            month = "0"+str(month)

        for day in range(start_day, end_day):
            self.logger.info(
                f"Extracting  day {day} article of tag {tag} of year {year} and month {month}")
            if(day < 10):
                day = "0"+str(day)
            url = f"https://medium.com/tag/{tag}/archive/{year}/{month}/{day}"
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            for card in (soup.findAll("div", {"class": class_})):
                if(not self._cntComment(card)):
                    link = self._get_link(card)
                    if(link):
                        total_claps = self._get_total_claps(card)
                        if(total_claps):
                            total_responses = self._get_total_responses(card)
                            if(not total_responses):
                                total_responses = 0
                            data_dict["total_responses"].append(
                                self._parse_responses(total_responses))
                            data_dict["link"].append(self._parse_link(link))
                            data_dict["total_claps"].append(
                                self._parse_claps(total_claps))
        return data_dict

    def _save(self, data_dict, tag, year, month):
        """Sends data to dropbox

        Arguments:
            data_dict {dict } -- Data Dictionary of scraped articles
            tag { str} -- Name of the tag
            year {int} -- Year of articles  scraped
            month {int} -- Month of articles scraped
        """
        file_path = f"/datasets/{tag}/{tag}-{year}-{month}.csv"
        try:
            dataFrame = pd.DataFrame.from_dict(data_dict).to_csv(index=False)
            dbx = dropbox.Dropbox(self.dropbox_token)
            db_bytes = bytes(dataFrame, 'utf8')
            dbx.files_upload(
                f=db_bytes,
                path=file_path,
                mode=dropbox.files.WriteMode.overwrite)
            self.logger.info(
                f"Sucessfully saved data of {tag}, of year {year}, month{month}")
        except Exception as e:
            self.logger.error(f"Failed to save {month} data: {e}")

    def run(self):
        """Main function which scrapes content on monthly basis for each year
        """
        for tag in self.tags:
            for year in self.years:
                for month in range(1, 13):
                    self.logger.info(
                        f"Started Extraction process for tag {tag}, year {year}, month {month}")
                    data_dict = self._ExtractMonthly(tag, year, month)
                    self._save(data_dict, tag, year, month)
