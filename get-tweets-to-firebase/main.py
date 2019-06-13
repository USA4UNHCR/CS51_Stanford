import tweepy
from tweepy import OAuthHandler
import copy
import firebase_admin
from firebase_admin import credentials, db
import random
import re
import geocoder
import datetime

queries = ['#refugee', '#immigrants', '#withrefugees', 'USA for UNHCR',
            '@UNRefugeeAgency', '@UNHCRUSA', '@Refugees', '#RefugeesWelcome',
            '#unhcr', '#refugees', '#immigrants', '#migrants',
            '#asylumseekers', '#illegals', '#Undocumented', 'UNHCR', 'UN',
           	'Refugees', 'ICE', 'deportation', 'border wall','#rohingyarefugees',
           	'#rohingya', '#asylum', '#syria', '#syrianrefugees'
			'Internally displaced person', 'Resettlement', 'Illegal Immigrant',
           	'Undocumented'] # Twitter search tokens, chosen at random per query

# Main function, Google Cloud Functions requires HTTP request parameter.
def main(request):
    apis = get_apis(credentials_arr) # returns array of API instances
    ref = db.reference() # get firebase root folder (that contains all the data)
    makeQueries(apis, ref)

# Error catching function, stops Twitter API queries if rate limit reached.
def limit_handled(cursor, index):
    while True:
        try:
            yield cursor.next()
        except tweepy.TweepError:
            print("Limit reached on api " + index)
            continue
        except StopIteration:
            break

# Runs the search query on given Twitter API instance and stores data into Firebase.
def runQuery(index, api, ref, added):
    for tweet in limit_handled(tweepy.Cursor(api.search, q=random.choice(queries), lang="en", geocode="39.8,-95.583068847656,2500km", \
    tweet_mode='extended').items(), index): # Query Twitter with randomly selected query (language set to English, geocode set to US only)
        if tweet == None:
            break
        tweet_ref = ref.child('Tweets-Folder/' + str(datetime.date.today())) # Store tweets in today's date's Firebase folder

        if hasattr(tweet, 'retweeted_status'): # Ignore retweets
            continue

        text = tweet.full_text
        new_tweet = tweet_ref.push() # Push to firebase

        if (text, tweet.user.name) not in added: # If tweet is unique
            if tweet.place != None: # Get tweet location
                tweetCoords = tweet.place.bounding_box.coordinates
                tweetLong = (tweetCoords[0][0][0] + tweetCoords[0][1][0] + tweetCoords[0][2][0] + tweetCoords[0][3][0]) / 4
                tweetLat = (tweetCoords[0][0][1] + tweetCoords[0][1][1] + tweetCoords[0][2][1] + tweetCoords[0][3][1]) / 4
            elif (tweet.user.location != None): # get user location
                coords = geocoder.arcgis(tweet.user.location) # converts user location from string to coordinates
                if coords != None:
                    tweetLat = coords.latlng[0]
                    tweetLong = coords.latlng[1]
                else:
                    tweetLong = None
                    tweetLat = None
            else:
                tweetLong = None
                tweetLat = None

            if re.search("(?P<url>https?://[^\s]+)", text):
                url = re.search("(?P<url>https?://[^\s]+)", text).group("url") # Obtains URL of tweet
            else:
                url = None

            new_tweet.set({
                'Date': str(tweet.created_at),
                'Tweet': text, # Full text
                'Tweet longitude': tweetLong,
                'Tweet latitude': tweetLat,
                'User location': tweet.user.location, #where the user is based, not where they tweeted from
                'Retweets': tweet.retweet_count,
                'Liked': tweet.favorite_count,
                'User': tweet.user.name,
                'Handle': tweet.user.screen_name,
                'Followers': tweet.user.followers_count,
                'Total Tweets by user': tweet.user.statuses_count,
                'Tweet URL': url,
            }) # Set relevant tweet information in Firebase

        added.append((text, tweet.user.name)) # Add tweet to already added list of tweets

# Handles queries for every Twitter API instance given in apis parameter.
def makeQueries(apis, ref):
    added = [] # Stores added tweets (used as check for uniqueness)
    for index, api in enumerate(apis): # Run search for each API instance
        runQuery(index, api, ref, added)

# Returns array of API instances given input array of API keysets.
def get_apis(credentials_arr):
    apis = []
    for dict in credentials_arr:
        auth = OAuthHandler(dict['consumer_key'], dict['consumer_secret'])
        auth.set_access_token(dict['access_token'], dict['access_token_secret'])
        apis.append(tweepy.API(auth))
    return apis

# Reads credentials.txt file, initializes Firebase and returns Twitter API instances.
def read_credentials():
    keyFile = open('credentials.txt', 'r')
    credentials_arr = []
    titles = ['consumer_key', 'consumer_secret', 'access_token', 'access_token_secret']
    creds_dict = {} # Dictionary of keys per API keyset
    index = 0
    for line in enumerate(keyFile):
        if line.startswith('#'):
            continue
        creds_dict[titles[index % 4]] = line.rstrip()
        if index % 4 == 3:
            credentials_arr.append(copy.copy(creds_dict))
            creds_dict.clear()
        index += 1
    keyFile.close()

    # Firebase setup
    if (not len(firebase_admin._apps)): # Check if Firebase not already initialized
        cred = credentials.Certificate("firebase-cred.json")
        firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://hive-258ce.firebaseio.com/'
        })
    return get_apis(credentials_arr) # Returns array of API instances
