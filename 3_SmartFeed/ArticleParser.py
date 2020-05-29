from newspaper import Article, Config
import time


class ArticleParser:
  """
  Class for Parsing a article given using it's url

  Args:
    url->str(), url for the article
  """

  def __init__(self, url):
    self.url = url
    try:
      self.article_obj = self._getArticleObj()
    except:
      time.sleep(0.7)
      self.article_obj = self._getArticleObj()


  def _getArticleObj(self):
    config = Config()
    config.keep_article_html = True
    article = Article(self.url, config=config)
    article.download()
    article.parse()
    article.nlp()
    return article

  def fetchArticleText(self):
    """ To get  the text of the article """
    return self.article_obj.text 

  def fetchArticleTitle(self):
    """ To get  the title of the article """
    return self.article_obj.title

  def fetchArticleImage(self):
    """ To get  the image of the article """
    return self.article_obj.top_image

  def fetchArticleKeywords(self):
    """ To get  the keywords of the article """
    return self.article_obj.keywords


  def parseArticleKeywords(self, tags_lis):
    """ To parse the keywords in a form suitable to send an email
    Args:
      tag_lis->list(), List of keywords
     """
    resp = ""
    for i,tag in enumerate(tags_lis):

        resp=resp+f"<em>{tag.title()}</em>, "

        if((i+1)==len(tags_lis)):
            return f"<strong>KeyWords: </strong>{resp}<em>{tag.title()}</em>"

    return resp


  def fetchArticleSummary(self):
    """ To get the article summary """
    return self.article_obj.summary 


  def parseArticleSummary(self,summary,n=30):
    """ To parse the article summary in a form suitable for an email
    Agrs:
      summary->str(), Summary of the article as sting
      n->int(), Number of characters to limit the summary to
    """

    summary_arr=summary.split(" ")
    summary_parsed='<strong>Summary:</strong>'
    for i in range(min(len(summary_arr),n)):
        summary_parsed =summary_parsed+summary_arr[i]+" "
    return (summary_parsed+".....")
