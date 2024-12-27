import os
import time
from helpers.ocr_processing import frame_at_time, grab_match_info, get_cur_match, get_cur_div
from helpers.stream_processing import similar, validate_match_integrity, process_match_end
from fetch.fetch_match_data import get_match_info_from_api
from helpers.monitors import print_info

url = "VODS/Prairies_Division_Day_1.mp4"
DIVISION_NAME = 'Prairies Division'
YEAR = 2024
DIVISION_ID = 2

info_json = {
    'time': 0,
    'division': DIVISION_NAME,
    'matchnum': "Pending...",
    'matchdetails': "Pending...",
    "saved": "N/A",
    "runtime": "N/A",
    'errors': [],
}

if not os.path.exists('TempImages'):
    os.makedirs('TempImages')

if not os.path.exists('matches'):
    os.makedirs('matches')

if __name__ == "__main__":
    cur_time = 3850  # Starting point
    skip_time = 120  # Minimum time skip after finding match information
    processed_matches = set()  # Track processed match IDs

    while True:
        # print(f'Processing time: {cur_time} seconds')
        temp = frame_at_time(cur_time, url)

        if temp.returncode != 0:
            print("Reached the end of the video.")
            break

        grab_match_info(qual=False)
        div_name = get_cur_div()
        info_json['time'] = cur_time

        if similar(div_name, DIVISION_NAME):
            start_time = time.time()
            grab_match_info(div=False)
            match_val = str(get_cur_match())

            if match_val.isdigit() and int(match_val) not in processed_matches:
                processed_matches.add(int(match_val))
                match_info = get_match_info_from_api(int(match_val), 2, YEAR, DIVISION_ID)

                if match_info:
                    # Validate that we've actually found the start of a match
                    # by checking 30 seconds ahead
                    is_valid, validation_match = validate_match_integrity(cur_time, match_val, info_json, url)

                    match_bounds = {
                        'start': cur_time,
                        'qual': match_val,
                        'red_teams': [match_info['Red Team 1'], match_info['Red Team 2']],
                        'blue_teams': [match_info['Blue Team 1'], match_info['Blue Team 2']],
                        'red_score': match_info['Red Score'],
                        'blue_score': match_info['Blue Score']
                    }

                    info_json['matchnum'] = match_val
                    info_json['matchdetails'] = f"{match_info['Red Team 1']} vs {match_info['Red Team 2']} - {match_info['Blue Team 1']} vs {match_info['Blue Team 2']}"

                    cur_time += skip_time
                    temp = frame_at_time(cur_time, url)
                    grab_match_info(div=False)
                    new_match_val = get_cur_match()

                    print_info(info_json)

                    if is_valid:
                        process_match_end(match_val, cur_time, url, match_bounds, DIVISION_NAME, start_time, info_json)
                        cur_time -= 10
                else:
                    info_json['errors'].append(f"No match information found for match {match_val}")
                    cur_time += skip_time
            else:
                cur_time += 10
        else:
            info_json['matchnum'] = "Pending..."
            info_json['matchdetails'] = "Pending..."

            cur_time += 10
        
        print_info(info_json)