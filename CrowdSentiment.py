from flask import Flask,render_template, redirect, request
import numpy as np
import tweepy
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import re

app = Flask(__name__)

@app.route('/sentiment', methods = ['GET','POST'])
def sentiment():
    hashtag = request.form.get('hashtag')

    if hashtag == "":
        error = "Please Enter any one value"
        return render_template('hashtag.html', error=error)



    #======================Insert Twitter API Here==========================
    consumerKey = "vPKr3YYkZEqwzerZr2L0nwbKJ"
    consumerSecret = "ywvEBawEtnnvzrlrVnZQF2vRxDPa4CmCCSB87sv9MCLQ99V11F"
    accessToken = "1416380854717329419-DgcBir4ZrGOUYiCMVTDnbB8gGKBgso"
    accessTokenSecret = "L2X1f90V9QIPz8IOBSuGahRJ8Tbok0XOaXzmqQXzAjmnf"
    #======================Insert Twitter API End===========================

    authenticate = tweepy.OAuthHandler(consumerKey, consumerSecret)
    authenticate.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(authenticate, wait_on_rate_limit = True)

    def cleanTxt(text):
        text = re.sub('@[A-Za-z0–9]+', '', text) #Removing @mentions
        text = re.sub('#', '', text) # Removing '#' hash tag
        text = re.sub('RT[\s]+', '', text) # Removing RT
        text = re.sub('https?:\/\/\S+', '', text) # Removing hyperlink
        return text
    def getSubjectivity(text):
        return TextBlob(text).sentiment.subjectivity
    def getPolarity(text):
        return TextBlob(text).sentiment.polarity
    def getAnalysis(score):
            if score < 0:
                return 'Negative'
            elif score == 0:
                return 'Neutral'
            else:
                return 'Positive'

    if not hashtag == "":
        # hash tag coding
        msgs = []
        msg =[]
        for tweet in tweepy.Cursor(api.search, q=hashtag).items(500):
            msg = [tweet.text]
            msg = tuple(msg)
            msgs.append(msg)

        df = pd.DataFrame(msgs)
        df['Tweets'] = df[0].apply(cleanTxt)
        df.drop(0, axis=1, inplace=True)
        df['Subjectivity'] = df['Tweets'].apply(getSubjectivity)
        df['Polarity'] = df['Tweets'].apply(getPolarity)
        df['Analysis'] = df['Polarity'].apply(getAnalysis)
        positive = df.loc[df['Analysis'].str.contains('Positive')]
        negative = df.loc[df['Analysis'].str.contains('Negative')]
        neutral = df.loc[df['Analysis'].str.contains('Neutral')]

        positive_per = round((positive.shape[0]/df.shape[0])*100, 1)
        negative_per = round((negative.shape[0]/df.shape[0])*100, 1)
        neutral_per = round((neutral.shape[0]/df.shape[0])*100, 1)

        return render_template('pourcentage.html', name=hashtag,positive=positive_per,negative=negative_per,neutral=neutral_per)

@app.route('/')
def home():
    return render_template('hashtag.html')

app.run(debug=True)
