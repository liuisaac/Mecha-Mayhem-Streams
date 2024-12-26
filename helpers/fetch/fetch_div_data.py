# File: helpers/robotevents_api.py

import os
import requests
from dotenv import load_dotenv
from helpers.fetch.mappings import year_to_key_map
import json

# Load environment variables
load_dotenv()

API_KEY = os.getenv('ROBOTEVENTS_API_KEY')
BASE_URL = 'https://www.robotevents.com/api/v2'

def load_match_info(year, division_id):
    event_id = year_to_key_map[year]

    output_dir = "./DivResults"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{event_id}_division_{division_id}_matches.json")
    matches = []
    url = f"{BASE_URL}/events/{event_id}/divisions/{division_id}/matches"
    headers = {
        'Authorization': f"Bearer {API_KEY}",
        'Accept': 'application/json',
    }

    while url:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            matches.extend(data['data'])
            url = data['meta']['next_page_url']
        except requests.RequestException as e:
            print(f"Error fetching match info: {e}")
            break

    try:
        with open(output_file, "w") as f:
            json.dump(matches, f, indent=4)
        print(f"Match info saved to {output_file}")
    except IOError as e:
        print(f"Error saving match info to file: {e}")

    return matches

# USAGE EXAMPLE: load_match_info(2024, 2)