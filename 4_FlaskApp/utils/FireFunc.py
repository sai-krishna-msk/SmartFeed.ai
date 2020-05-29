from utils.config import email_config, invite_url
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def parse_email(raw_email):
    """
    Parses email to be
    in suitable format as 
    userId """
    raw_email = raw_email.replace(".",'')
    return raw_email.split("@")[0]

def anySubs(UserDetails):
    """
    Checks if the user has any subscriptions yet
    """

    if('subscriptions' in UserDetails.keys()):
        return True
    return False



def get_pubs(db):
    """
    returns all the publication details
    """
    try:
        return (db.child("TagRecords").get()).val()

    except Exception as e:
        return False


def getUserPubs(db,userID):
    """
    returns list of publications
    user is subscribed to
    """

    userDetails = (db.child("UserDetails").child(parse_email(userID)).get()).val()
    if(anySubs(userDetails)):
        return  userDetails["subscriptions"]
    return False



def updateUserPubs(db,userID,Pubs):
    """
    updates the user subscriptions
    """
    try:
        db.child("UserDetails").child(parse_email(userID)).update({"subscriptions":Pubs})
        return True 

    except Exception as e:
        return False


    pass


def createUser(db,raw_email,first_name, last_name,slack_username,publications=[]):
    """
    fills details of the new user created 
    """
    try:

        resp = db.child("UserDetails").child(parse_email(raw_email)).set({'FirstName':first_name, 'LastName':last_name, 'SlackUsername':slack_username,
                                            'subscriptions':publications, 'email':raw_email})
        return True

    except Exception as e:
        return False


def validSlackUsername(DB,slack_username):

    users = DB.child("UserDetails").get().val()

    usernames = [users[user]['SlackUsername'] for user in users]

    if( usernames and slack_username in usernames ):
        return False

    return True 


def get_email_content(slack_username):
    content = "" 
    content = f"""
                <div style="text-align:center;">
                        <img src="https://i.ibb.co/RSh7ZrF/logo-2.png">
                        </div>
    


                <br><br>
                <p>Click below to subsribe to the slack channel with <strong>{slack_username}</strong> as your username</p>
                
               <button style="border-radius:12px;padding:12px 28px; margin-left:10%">  <a href="{invite_url}">Join Slack</a></button>
                """
    return content




def sendEmail(email, slack_username):
    content = get_email_content(slack_username)
    message = Mail(
    from_email='smartfeed.ai@gmail.com',
    to_emails=email,
    subject='Smart Feed Subscription Confirmation Email ',
    html_content=content)
    try:
        sendgrid_client = SendGridAPIClient(email_config["SEND_GRID_KEY"])
        response = sendgrid_client.send(message)
        print(f"Successfully Sent an email to {slack_username}")
    except Exception as e:
        print(f"Failed to send Email to {slack_username}")