import numpy as np
import pandas as pd
import json
import datetime
import firebase_admin
from firebase_admin import credentials, db
import geocoder
import re

# Main function, Google Cloud Functions requires HTTP request parameter.
def main(request):
    if (not len(firebase_admin._apps)): # Check if Firebase not already initialized
        cred = credentials.Certificate("firebase-cred.json")
        firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://hive-258ce.firebaseio.com/'
        })
    retrieveData()

# Get tweet data from today's date's respective tweet folder, then calculate and update
# influencer table given tweet data.
def retrieveData():
    ref = db.reference('/Tweets-Folder/' + str(datetime.date.today()) + '/')
    result = ref.get()
    data = pd.DataFrame(columns=['Date', 'Tweet', 'Tweet latitude', 'Tweet longitude', 'User', 'User location', 'Retweets', 'Replies', 'Liked', 'Handle', 'Followers', 'Total Tweets by user']) # Form dataframe of user information
    for i , key in enumerate(result.keys()):
        data.loc[i] = (result[key]['Date'] if 'Date' in result[key] else np.NaN,
        result[key]['Tweet'] if 'Tweet' in result[key] else np.NaN,
        result[key]['Tweet latitude'] if 'Tweet latitude' in result[key] else np.NaN,
        result[key]['Tweet longitude'] if 'Tweet longitude' in result[key] else np.NaN,
        result[key]['User'] if 'User' in result[key] else np.NaN,
        result[key]['User location'] if 'User location' in result[key] else np.NaN,
        result[key]['Retweets'] if 'Retweets' in result[key] else np.NaN,
        result[key]['Replies'] if 'Replies' in result[key] else np.NaN,
        result[key]['Liked'] if 'Liked' in result[key] else np.NaN,
        result[key]['Handle'] if 'Handle' in result[key] else np.NaN,
        result[key]['Followers'] if 'Followers' in result[key] else np.NaN,
        result[key]['Total Tweets by user'] if 'Total Tweets by user' in result[key] else np.NaN)
    data.fillna(0) # Fill non-numbers with 0 value
    data['Influencer-Score'] = (data['Followers'] * (data['Retweets']+1) * (np.log(data['Total Tweets by user'].astype('float'))/np.log(1.5)) * (data['Liked']+1)) / 10**9 # Calculate influencer score for all users in dataframe
    influencers = data.loc[data['Influencer-Score'] >= 1] # Store influencers with score above threshold

    influencer_ref = db.reference('Influencers/') # Influencers Firebase reference location
    city_ref = db.reference('City/') # City Firebase reference location (to store influencers by city)
    for index,row in influencers.iterrows():
        existingChild = influencer_ref.child(row['Handle']).get()
        existingChild_ref = influencer_ref.child(row['Handle'])
        if existingChild:
            if existingChild['Influencer-Score'] < row['Influencer-Score']:
                existingChild_ref.update({
                    'User': row['User'],
                    'User location': row['User location'],
                    'Handle': row['Handle'],
                    'Latitude': row['Tweet latitude'],
                    'Longitude': row['Tweet longitude'],
                    'Followers': row['Followers'],
                    'Total Tweets by user': row['Total Tweets by user'],
                    'Tweet': row['Tweet'],
                    'Influencer-Score': row['Influencer-Score'],
                })
        else:
            newInfluencer = influencer_ref.child(row['Handle'])
            newInfluencer.update({
                'User': row['User'],
                'User location': row['User location'],
                'Handle': row['Handle'],
                'Latitude': row['Tweet latitude'],
                'Longitude': row['Tweet longitude'],
                'Followers': row['Followers'],
                'Total Tweets by user': row['Total Tweets by user'],
                'Tweet': row['Tweet'],
                'Influencer-Score': row['Influencer-Score'],
            })
        try:
            g = geocoder.yandex(row['Tweet latitude'], [row['Tweet longitude']], method='reverse').json
        except:
            g = None

        if g:
            cityName = g['raw']['metaDataProperty']['GeocoderMetaData']['text']
            cityName = re.sub('[.]', '', cityName)
            cityName = cityName.split(',')
            cityName.reverse()
            cityName = ",".join(cityName)
        else:
            cityName = 'unknown'

        existingCity = city_ref.child(cityName).get()
        existingCity_ref = city_ref.child(cityName)
        if existingCity and not existingChild:
            newInfluencer = existingCity_ref.child(row['Handle'])
            newInfluencer.update({
                'User': row['User'],
                'User location': row['User location'],
                'Handle': row['Handle'],
                'Latitude': row['Tweet latitude'],
                'Longitude': row['Tweet longitude'],
                'Followers': row['Followers'],
                'Total Tweets by user': row['Total Tweets by user'],
                'Tweet': row['Tweet'],
                'Influencer-Score': row['Influencer-Score'],
            })
        elif not existingCity:
            newCity = city_ref.child(cityName)
            newInfluencer = newCity.child(row['Handle'])
            newInfluencer.update({
                'User': row['User'],
                'User location': row['User location'],
                'Handle': row['Handle'],
                'Latitude': row['Tweet latitude'],
                'Longitude': row['Tweet longitude'],
                'Followers': row['Followers'],
                'Total Tweets by user': row['Total Tweets by user'],
                'Tweet': row['Tweet'],
                'Influencer-Score': row['Influencer-Score'],
            })
