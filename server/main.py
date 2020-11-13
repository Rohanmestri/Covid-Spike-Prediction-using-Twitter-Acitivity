# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_render_template]
import datetime
import tweepy
from flask import Flask, render_template,jsonify, request

app = Flask(__name__)

def authorize_tweepy():
    access_token = "1316596554019606528-jQFT42MywGGywBCV3zRG04meWY7Djb"
    access_token_secret = "gQhey9w6PG21CFwDZ2fnr8Loc9VAvQkPCzv9Xuv312vv9"

    twitter_app_auth = {
        'consumer_key': 'D8dNIYJYmKnYAEtmz3WKxg3Oq',
        'consumer_secret': 'lTh6qHCqds1bIKBBn9WtGeqxpLyKsIjKz4FAO1SGETMnVmkVbZ'
    }

    auth = tweepy.OAuthHandler(twitter_app_auth['consumer_key'], twitter_app_auth['consumer_secret'])
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True)
    return api

def get_tweets(latitude,longitude,radius):
    api = authorize_tweepy()
    
    keywords = ["restaurants","groceries","gym","mall","theatres","event","travelled","salon"]
    q = ""
    for key in keywords:
       q += key + " OR "

    q = q[:-4]
    q += " -filter:retweets"
    print(q)

    gcode = latitude + "," + longitude + "," + radius + "km"
    cursor = tweepy.Cursor(api.search, q=q, lang="en", tweet_mode='extended', geocode = gcode).items(10000)
    tweets = [status._json for status in cursor]
    return tweets

    

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def get_coordinates():
    if not request.json or not 'latitude' in request.json or not 'longitude' in request.json:
        abort(400)
    '''
    coordinates = {
        'latitude': request.json['latitude'],
        'longitude': request.json['longitude'],
        'Received': "Yes"
    }
    '''
    tweets = get_tweets(request.json['latitude'],request.json['longitude'],request.json['radius'])

    # Enter the code to process the data
    # Run Classifier
    
    for tweet in tweets:
          tweet['full_text']
    
    
    tweet = {
       'number_of_tweets':len(tweets),
    }

    return jsonify(tweet), 201
    


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python38_render_template]



