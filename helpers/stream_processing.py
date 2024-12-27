import time
import subprocess
from difflib import SequenceMatcher
from .ocr_processing import frame_at_time, grab_match_info, get_cur_match
from .monitors import print_info

def similar(a, b, threshold=0.8):
    """Return True if strings are similar above threshold."""
    if not a or not b:  # Handle None or empty strings
        return False
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold

def validate_match_integrity(cur_time, match_val, info_json, url):
    errorCount = 0
    intervals = [15, 30, 60, 100]

    for interval in intervals:
        frame_at_time(cur_time + interval, url)
        grab_match_info(div=False)
        validation_match = get_cur_match()

        if validation_match != match_val:
            if (errorCount < 2):
                errorCount += 1
            else:
                info_json['errors'].append(f"False match detection at {cur_time + interval}s. Expected [{match_val}], found [{validation_match}]")
                print_info(info_json)
                return False, validation_match
    return True, validation_match


def process_match_end(match_val, cur_time, url, match_bounds, DIVISION_NAME, start_time, info_json):
    bufferLength = 10
    # Capture the match info until the match ends
    while match_val == get_cur_match():
        cur_time += 10
        info_json['time'] = str(cur_time) + "*"
        print_info(info_json)


        frame_at_time(cur_time, url)
        grab_match_info(div=False)
    
    # Set the match end time
    match_bounds['end'] = cur_time
    # print(f'Match {match_val} ends at {cur_time} seconds')

    # Define time buffer before and after the match
    buffer_start = max(0, match_bounds['start'] - bufferLength)
    buffer_end = match_bounds['end'] + bufferLength

    # Construct the filename for the match video
    file_name = f'matches/Q{match_bounds["qual"]} {DIVISION_NAME} 2024 {match_bounds["red_teams"][0]} {match_bounds["red_teams"][1]} vs {match_bounds["blue_teams"][0]} {match_bounds["blue_teams"][1]} - {match_bounds["red_score"]} to {match_bounds["blue_score"]}.mp4'

    # Run the ffmpeg command to extract the video
    ffmpeg_command = [
        'ffmpeg', '-ss', str(buffer_start), '-i', url,
        '-t', str(buffer_end - buffer_start),
        '-c', 'copy', file_name, '-y', '-hide_banner', '-loglevel', 'error'
    ]
    subprocess.run(ffmpeg_command)

    info_json['saved'] = f'Saving match to {file_name}' 
    info_json['runtime'] = f'Time to process: {time.time() - start_time} seconds'
    print_info(info_json)