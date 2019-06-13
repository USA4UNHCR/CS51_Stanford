import firebase_admin
from firebase_admin import credentials, db
import json
import copy
from flask import Flask
from flask_cors import CORS

# Initialize CORS to allow data retreival from front-end.
app = Flask(__name__)
CORS(app)
@app.route("/")

# Main function, Google Cloud Functions requires HTTP request parameter.
def main(request):
    headers = {
        'Access-Control-Allow-Origin': '*' # Allow access from any domain (insecure - FIX IF POSSIBLE)
    }

    # Firebase setup
    if (not len(firebase_admin._apps)): # Check if Firebase not already initialized
        cred = credentials.Certificate("firebase-cred.json")
        firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://hive-258ce.firebaseio.com/'
        })

    k_influencers = 200 # Return this many influencers
    ref_influencers = db.reference('/Influencers')
    influencers = ref_influencers.order_by_child('Influencer-Score').limit_to_last(k_influencers) # Get top k_influencers number of influencers
    arr = influencers.get() # Complete dictionary of influencers
    sorted_keys = list(arr.keys())[::-1]

    output_keys = ['star', 'macro', 'mid', 'micro'] # Influencer tiers
    scores = [2000000, 500000, 100000, 1000] # Tier minimum follower counts
    output = {'star': {}, 'macro': {}, 'mid': {}, 'micro': {}}

    for user in sorted_keys: # Form output dictionary, users divided by tiers
        user_dict = copy.copy(arr[user])
        for i in range(len(scores)):
            if user_dict['Followers'] >= scores[i]:
                user_dict['Tier'] = output_keys[i]
                output[output_keys[i]][user] = user_dict
                break

    return (json.dumps(output), 200, headers) # Return jsonified dictionary and HTTPS code/headers
