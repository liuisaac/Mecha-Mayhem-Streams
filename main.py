import os
import time
from helpers.video_processing import frame_at_time, grab_match_info, get_cur_match, get_cur_div
from helpers.stream_processing import similar, validate_match_integrity, process_match_end
from helpers.fetch.fetch_match_data import get_match_info_from_api

url = "VODS/Prairies_Division_Day_1.mp4"
DIVISION_NAME = 'Prairies Division'
YEAR = 2024
DIVISION_ID = 2

if not os.path.exists('TempImages'):
    os.makedirs('TempImages')

if not os.path.exists('matches'):
    os.makedirs('matches')

if __name__ == "__main__":
    cur_time = 3850  # Starting point
    skip_time = 120  # Minimum time skip after finding match information
    processed_matches = set()  # Track processed match IDs

    while True:
        print(f'Processing time: {cur_time} seconds')
        temp = frame_at_time(cur_time, url)

        if temp.returncode != 0:
            print("Reached the end of the video.")
            break

        grab_match_info(qual=False)
        div_name = get_cur_div()

        if similar(div_name, DIVISION_NAME):
            start_time = time.time()
            grab_match_info(div=False)
            match_val = str(get_cur_match())

            if match_val.isdigit() and int(match_val) not in processed_matches:
                print(f'Found match {match_val} in division {div_name} at time {cur_time}')
                processed_matches.add(int(match_val))

                match_info = get_match_info_from_api(int(match_val), 2, YEAR, DIVISION_ID)
                print(match_info, match_val, YEAR, DIVISION_ID)

                if match_info:
                    # Validate that we've actually found the start of a match
                    # by checking 30 seconds ahead
                    is_valid, validation_match = validate_match_integrity(cur_time, url, match_val)
                    match_bounds = {
                        'start': cur_time,
                        'qual': match_val,
                        'red_teams': [match_info['Red Team 1'], match_info['Red Team 2']],
                        'blue_teams': [match_info['Blue Team 1'], match_info['Blue Team 2']],
                        'red_score': match_info['Red Score'],
                        'blue_score': match_info['Blue Score']
                    }

                    cur_time += skip_time
                    temp = frame_at_time(cur_time, url)
                    grab_match_info(div=False)
                    new_match_val = get_cur_match()

                    process_match_end(match_val, cur_time, url, match_bounds, DIVISION_NAME, start_time)
                else:
                    print(f'No match information found for match {match_val}')
                    cur_time += skip_time
            else:
                cur_time += 10
        else:
            cur_time += 10
