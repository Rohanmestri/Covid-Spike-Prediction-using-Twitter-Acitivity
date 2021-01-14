#Import Server and Twitter Dependencies
import datetime
import tweepy
from flask import Flask, render_template,jsonify, request

#Import Tensorflow specific dependencies
import math
import pandas as pd
import numpy as np
import os
import pickle
import sys
import tensorflow as tf
from textprep import text_prep
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import model_from_json



#initialize flask 
app = Flask(__name__)




# defining the Twitter API keys for the application. Misuse of this information
# may lead to Twitter Account Suspension.
def authorize_tweepy():
    access_token = "<Enter Token>"
    access_token_secret = "<Enter Token Secret>"

    twitter_app_auth = {
        'consumer_key': '<Enter Consumer Key>',
        'consumer_secret': '<Enter Consumer Secret>'
    }

    auth = tweepy.OAuthHandler(twitter_app_auth['consumer_key'], twitter_app_auth['consumer_secret'])
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True)
    return api


# function which fetches the tweets from the twitter api
def get_tweets(latitude,longitude,radius):
    api = authorize_tweepy()

    # Predetermined query keywords. Explained in the paper
    keywords = ["restaurants","groceries","gym","mall","theatres","event","travelled","salon"]

    # Concatentate each query using the OR function
    q = ""
    for key in keywords:
       q += key + " OR "

    # Do not fetch "Retweets"
    q = q[:-4]
    q += " -filter:retweets"

    # Embed the Geocode and Radius info set by the user in the query
    gcode = latitude + "," + longitude + "," + radius + "km"
    cursor = tweepy.Cursor(api.search, q=q, lang="en", tweet_mode='extended', geocode = gcode).items(10000)
    tweets = [status._json for status in cursor]
    return tweets

    

# API call which handles POST requests
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def get_coordinates():
    # Raise an error if the incoming json does not have the correct format
    if not request.json or not 'latitude' in request.json or not 'longitude' in request.json:
        abort(400)

    print("Received the Coordinates: (" + request.json['latitude'] + "," + request.json['longitude'] + ")")
    print("Received the Radius: " + request.json['radius'] + " km")

    # Fetch Tweets in the user's neighborhood
    tweets = get_tweets(request.json['latitude'],request.json['longitude'],request.json['radius'])
    print("The Number of Fetched Tweets in the locality: " + str(len(tweets)))

    # Isolate only the textual part of the tweet for the NLP Classifier.
    tweets_list=[]
    for tweet in tweets:
          tweets_list.append(text_prep(tweet['full_text']))
    
    # Load Pretrained Models
    vec_pickle = open('tfidf_vectorizer.pkl',"rb")
    tfidf_vectorizer = pickle.load(vec_pickle)

    # Load Model and weights from json and h5 files respectively.
    x_test = tfidf_vectorizer.transform(tweets_list).toarray()
    json_file = open("tfidfmodel.json", 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights("tfidf_model.h5")
    print("Model Loaded Successfully")

    # Make predictions for valid tweets
    predicts = loaded_model.predict(x_test, batch_size=32,verbose=2)
    predicts=predicts.argmax(1)

    # Define the constants as declared in the paper
    total, count = 0, 0
    alpha, beta = 1/math.log(1000000), 1/math.log(1000000)

    # Loop over the valid tweets and do a summation of the weighted tweets
    for i,tweet in enumerate(tweets):
        if predicts[i]==1:
            # Equation as defined in the paper
            followers = math.log(2 + tweet['user']['followers_count'])
            favorites = math.log(2 + tweet['favorite_count'])
            score=(alpha*followers + beta*favorites)/2
            total=total+score
            count+=1

    print("The Total Number of Filtered Tweets: " + str(count))

    # Define the risk factor for a uniform area 
    total /= math.pow(int(request.json['radius'])*2,2)

    print("Sending the Risk Score as a JSON Response to the Client")
    
    # Define the format for the response json
    tweet = {
       'score':str(round(total, 3)),
    }

    # Return the jsonified response
    return jsonify(tweet), 201
    

# Run the app using the Ipv4 address
if __name__ == '__main__':
    app.run(host='192.168.1.60', port=20000, debug=True)

