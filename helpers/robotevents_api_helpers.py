# File: helpers/robotevents_api.py

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv('ROBOTEVENTS_API_KEY')
BASE_URL = 'https://www.robotevents.com/api/v2'

def load_match_info(event_id):
    url = f"{BASE_URL}/events/51496/matches"
    headers = {
        'Authorization': f"Bearer {API_KEY}",
        'Accept': 'application/json',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['data']  # The actual match data is in the 'data' field of the response
    except requests.RequestException as e:
        print(f"Error fetching match info: {e}")
        return None

def get_match_info_from_api(match_val, matches):
    for match in matches:
        if match_val in match['name']:
            return {
                'Match': match['name'],
                'Red Team 1': match['alliances']['red']['teams'][0]['team']['name'] if match['alliances']['red']['teams'] else '',
                'Red Team 2': match['alliances']['red']['teams'][1]['team']['name'] if len(match['alliances']['red']['teams']) > 1 else '',
                'Blue Team 1': match['alliances']['blue']['teams'][0]['team']['name'] if match['alliances']['blue']['teams'] else '',
                'Blue Team 2': match['alliances']['blue']['teams'][1]['team']['name'] if len(match['alliances']['blue']['teams']) > 1 else '',
                'Red Score': match['alliances']['red']['score'],
                'Blue Score': match['alliances']['blue']['score']
            }
    return None