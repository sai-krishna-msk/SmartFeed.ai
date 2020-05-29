from config import args
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from ArticleParser import ArticleParser
from utils import getLogger

logger  = getLogger("Feed Mail")

class FeedMail:
  """"Sends Recommended feed as email to the user 

  Args:
    user_email(str): Email of the user to which feed us to be sent
    recommendations(dict): Recommendations of the corresponding user

  Attributes:
    from_email(str): Email of smartfeed.ai
    key(str): SendGrid API's key
    html_content(str): Consists the body of the email
    subject(str): Consists the subject of the email


  """
  def __init__(self, user_email, recommendations):
    self.recommendations = recommendations
    self.to_email = user_email
    self.from_email = args["FROM_EMAIL"]
    self.key = args["SEND_GRID_KEY"]
    self.html_content = self._parseEmailContent(self.recommendations)
    self.subject = self._getEmailSubject()


  def _parseEmailContent(self,recommendations):
    """ For given list of recommendations parses it into presentable html format for email"""
    html_content = ''
    for edition in recommendations:
      html_content = html_content+f"""<h1>{edition.title()}-Feed</h1>"""
      for tag in recommendations[edition]:
        html_content = html_content +f"""<h2>{tag.title()}</h2>"""
        for link in recommendations[edition][tag]:
          article_obj = ArticleParser(link)
          html_content = html_content + f""" <a href="{link}"> <h2><strong>{article_obj.fetchArticleTitle()}</strong></h2></a>
                                                {article_obj.parseArticleKeywords(article_obj.fetchArticleKeywords())}
                                                <div><img src="{article_obj.fetchArticleImage()}"</div><br>
                                                <div>{article_obj.parseArticleSummary(article_obj.fetchArticleSummary())}</div> 
                                                <hr><br><br>"""

    return html_content

  def _getEmailSubject(self):
    """ Subject of the email """
    return "Your Feed for the day"


  def pushEmail(self):
    """ Sends the email using the Send Grid API """
    message = Mail(
          from_email=self.from_email,
          to_emails=self.to_email,
          subject=self.subject,
          html_content=self.html_content)

    try:
      sendgrid_client = SendGridAPIClient(self.key)
      response = sendgrid_client.send(message)
      logger.info(f"Email Successfully sent to {self.to_email}")
    except Exception as e:
      logger.error(f"Feed could not be sent to {self.to_email}")
