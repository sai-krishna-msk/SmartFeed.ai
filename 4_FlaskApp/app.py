from functools import wraps
import sys
import os
import json
import time

from flask import Flask, render_template, redirect, request, url_for, session, flash
import pyrebase
import requests

from utils import FireFunc as fire
from utils.config import cloud_config




app = Flask(__name__)
app.secret_key = "winteriscoming"
firebase = pyrebase.initialize_app(cloud_config)
AUTH = firebase.auth()
DB = firebase.database()

def checkUserSession():
    if ( "logged_in" in session and  session["logged_in"]==True) :
        return True

    return False






@app.route('/')
def dashboard():
    subscriptions=[]
    PUBLICATION = fire.get_pubs(DB)
    if(checkUserSession()):
        subscriptions= fire.getUserPubs(DB,session["email"])

        if(not subscriptions):

            subscriptions=[]

    return render_template('index.html', publications=PUBLICATION , userPubs = subscriptions)


@app.route("/login", methods=["GET", "POST"])
def login():

    if(checkUserSession()):
        return redirect('/')

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            user = AUTH.sign_in_with_email_and_password(email, password)
            user_id = user['idToken']
            user_email = email
            session['user'] = user_id
            session["email"] = user_email
            session['logged_in'] = True
            session.modified = True
            return redirect("/") 

        except Exception as e:
            flash("Invalid Email or password", "error")
            return render_template("login.html" )  

    return render_template("login.html")


@app.route("/logout")
def logout():
    AUTH.current_user = None
    session['user'] = None 
    session["email"] = None
    session.clear()
    session['logged_in'] = False
    session.modified = True
    return redirect("/")



@app.route("/signup", methods=["GET", "POST"])
def signup():
    if(checkUserSession()):
        return redirect('/')

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        slack_username = (request.form["slackUsername"]).lower()
        first_name = request.form["firstName"]
        last_name = request.form["lastName"]


        if(not fire.validSlackUsername(DB,slack_username)):
            flash("Slack Username has been taken, try another one")
            return redirect('/signup')

        try:
            AUTH.create_user_with_email_and_password(email, password)
            fire.createUser(DB,email,first_name, last_name,slack_username)
            fire.sendEmail(email, slack_username)
            flash("Successfully registered !")
            return redirect("/login") 

        except requests.exceptions.HTTPError as e:
            error_message = json.loads(e.args[1])['error']['message']
            flash(f"{error_message}")
            return redirect("/signup")  


        except Exception as e:
            flash("Invalid details, kindly provide appropriate details !")
            return render_template("signup.html")

    return render_template("signup.html")


@app.route("/forgotPassword", methods=["GET", "POST"])
def forgotPassword():

    if(checkUserSession()):
        return redirect('/')

    if request.method == "POST":
        email = request.form["email"]
        

        try:
            AUTH.send_password_reset_email(email)
            flash("Check you email")
            return redirect("/login") 

        except requests.exceptions.HTTPError as e:
            error_message = json.loads(e.args[1])['error']['message']
            flash(f"{error_message}")
            return redirect('/login')  

    return render_template("forgotPassword.html")






@app.route('/<pub>/<action>')
def updatePub(pub , action):

    if(not checkUserSession()):
        flash("You need to login for that !")
        return redirect('/login')

    user_email  =  session["email"]
    userPubs = fire.getUserPubs(DB,user_email)
    if(userPubs):
        userPubs = [tag for tag in userPubs if tag ]
    else:
        userPubs=[]

    try:
        if(action=='subscribe'):
            userPubs.append(pub)
            flash(f"Successfully Subscribed to {pub}")
            fire.updateUserPubs(DB,user_email,userPubs)

        else:
            userPubs.remove(pub)
            flash(f"Successfully Unsubscribed to {pub}")
            fire.updateUserPubs(DB,user_email,userPubs)

    except Exception as e:
        print(f"Error when adding publications: {e}")
        flash(f"Not Allowed !")


    return redirect('/')


  

@app.route('/admin',  methods=["GET", "POST"])
def addPubs():
    if session['email']!='smartfeed.ai@gmail.com':
        return redirect('/')

    if request.method=="POST":
        name = request.form["tag_name"]
        pub_url = request.form["tag_url"]
        category = request.form["tag_category"]
        try:
            DB.child("TagRecords").child(name).set({'tag_url':pub_url, 'category':category})
            flash(f"Successfully Added {name}")
            return redirect('/admin')

        except Exception as e:
            flash(f"Failed to add {name}: {e}")
            return redirect('/admin')

    return render_template('post_pub.html')




@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run()