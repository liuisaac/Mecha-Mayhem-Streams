import os
import subprocess
from helpers.video_processing import frame_at_time, grab_match_info, get_cur_match, get_cur_div
from helpers.excel_processing import load_match_info, get_match_info_from_excel
from difflib import SequenceMatcher
import time

url = "VODS/Mecha Mayhem 2024 - Prairies Division Day 1 (1080p_60fps_H264-128kbit_AAC).mp4"
murl = "DivResults/RE-VRC-23-1496-Prairies Division-Results-2024-12-18.xls"
DIVISION_NAME = 'Prairies Division'

def similar(a, b, threshold=0.8):
    """Return True if strings are similar above threshold."""
    if not a or not b:  # Handle None or empty strings
        return False
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold


if not os.path.exists('TempImages'):
    os.makedirs('TempImages')

if not os.path.exists('matches'):
    os.makedirs('matches')

if __name__ == "__main__":
    # Load match information from Excel file
    match_info_df = load_match_info(murl)

    cur_time = 3600  # Starting point
    skip_time = 120  # Minimum time skip after finding match information

    while True:
        print(f'Processing time: {cur_time} seconds')
        temp = frame_at_time(cur_time, url)

        if temp.returncode != 0:
            print("Reached the end of the video.")
            break

        grab_match_info(qual=False)
        div_name = get_cur_div()

        if similar(div_name, DIVISION_NAME):
            grab_match_info(div=False)
            match_val = str(get_cur_match())

            if match_val != '':
                print(f'Found match {match_val} in division {div_name} at time {cur_time}')
                match_info = get_match_info_from_excel(str(match_val), match_info_df)

                if match_info:
                    # Validate that we've actually found the start of a match
                    # by checking 30 seconds ahead
                    validation_time = cur_time + 30
                    temp = frame_at_time(validation_time, url)
                    grab_match_info(div=False)
                    validation_match = get_cur_match()

                    start_time = time.time()
                    
                    if validation_match != match_val:
                        print(f"False match detection at {cur_time}. Expected {match_val}, found {validation_match} after 30s")
                        cur_time += 10
                        continue

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

                    if match_val == new_match_val:
                        while match_val == new_match_val:
                            cur_time += 5
                            temp = frame_at_time(cur_time, url)
                            grab_match_info(div=False)
                            new_match_val = get_cur_match()


                        match_bounds['end'] = cur_time
                        print(f'Match {match_val} ends at {cur_time} seconds')

                        buffer_start = max(0, match_bounds['start'] - 20)
                        buffer_end = match_bounds['end'] + 20

                        file_name = f'matches/{DIVISION_NAME}_Q{match_bounds["qual"]}_2024_{match_bounds["red_teams"][0]}_{match_bounds["red_teams"][1]}_vs_{match_bounds["blue_teams"][0]}_{match_bounds["blue_teams"][1]}-{match_bounds["red_score"]}_to_{match_bounds["blue_score"]}.mp4'
                        print(f'Saving match to {file_name}')

                        ffmpeg_command = [
                            'ffmpeg', '-ss', str(buffer_start), '-i', url,
                            '-t', str(buffer_end - buffer_start),
                            '-c', 'copy', file_name, '-y', '-hide_banner', '-loglevel', 'error'
                        ]
                        subprocess.run(ffmpeg_command)
                        print(f'Time to process: {time.time() - start_time} seconds')
                    else:
                        cur_time -= 115
                else:
                    print(f'No match information found for match {match_val}')
                    cur_time += skip_time
            else:
                cur_time += 10
        else:
            cur_time += 10
