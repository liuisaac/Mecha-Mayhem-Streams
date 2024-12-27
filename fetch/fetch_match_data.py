import os
import json
from .fetch_div_data import load_match_info
from .mappings import year_to_key_map

def get_match_info_from_api(match_val, round_num, year, division_id):
    event_id = year_to_key_map[year]

    output_dir = "./divResults"
    output_file = os.path.join(output_dir, f"{event_id}_division_{division_id}_matches.json")

    if os.path.exists(output_file):
        try:
            with open(output_file, "r") as f:
                matches = json.load(f)
        except IOError as e:
            print(f"Error reading match info file: {e}")
            return None
    else:
        matches = load_match_info(event_id, division_id)

    for match in matches:
        if (round_num == match['round'] and match_val == match['matchnum']):
            return {
                'Match': match['name'],
                'Red Team 1': match['alliances'][1]['teams'][0]['team']['name'] if len(match['alliances'][1]['teams']) > 0 else '',
                'Red Team 2': match['alliances'][1]['teams'][1]['team']['name'] if len(match['alliances'][1]['teams']) > 1 else '',
                'Blue Team 1': match['alliances'][0]['teams'][0]['team']['name'] if len(match['alliances'][0]['teams']) > 0 else '',
                'Blue Team 2': match['alliances'][0]['teams'][1]['team']['name'] if len(match['alliances'][0]['teams']) > 1 else '',
                'Red Score': match['alliances'][1]['score'],
                'Blue Score': match['alliances'][0]['score']
            }
    return None

# USAGE EXAMPLE: get_match_info_from_api(1, 2, 2024, 2)