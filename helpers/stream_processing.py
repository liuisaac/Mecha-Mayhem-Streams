import time
import subprocess
from difflib import SequenceMatcher
from helpers.video_processing import frame_at_time, grab_match_info, get_cur_match, get_cur_div

def similar(a, b, threshold=0.8):
    """Return True if strings are similar above threshold."""
    if not a or not b:  # Handle None or empty strings
        return False
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold

def validate_match_integrity(cur_time, url, match_val):
    """
    Validate that the match at cur_time is correctly detected by checking 30 seconds ahead.

    Args:
    - cur_time (int): The current time in the video.
    - url (str): The path to the video file.
    - match_val (str): The match identifier.

    Returns:
    - bool: True if the match is valid, False otherwise.
    - str: The validation match value.
    """
    validation_time = cur_time + 30
    temp = frame_at_time(validation_time, url)
    grab_match_info(div=False)
    validation_match = get_cur_match()

    if validation_match != match_val:
        print(f"False match detection at {cur_time}. Expected {match_val}, found {validation_match} after 30s")
        return False, validation_match

    return True, validation_match


def process_match_end(match_val, cur_time, url, match_bounds, DIVISION_NAME, start_time):
    """
    Process the end of a match by capturing the match data, adjusting time, and running the ffmpeg command.
    
    Args:
    - match_val (int): The current match value.
    - cur_time (float): The current time in seconds.
    - url (str): The video URL for ffmpeg processing.
    - match_bounds (dict): The dictionary with match start and end times.
    - DIVISION_NAME (str): The name of the division.
    
    Returns:
    - None
    """
    bufferLength = 10
    # Capture the match info until the match ends
    while match_val == get_cur_match():
        cur_time += 10
        frame_at_time(cur_time, url)
        grab_match_info(div=False)
    
    # Set the match end time
    match_bounds['end'] = cur_time
    print(f'Match {match_val} ends at {cur_time} seconds')

    # Define time buffer before and after the match
    buffer_start = max(0, match_bounds['start'] - bufferLength)
    buffer_end = match_bounds['end'] + bufferLength

    # Construct the filename for the match video
    file_name = f'matches/{DIVISION_NAME}_Q{match_bounds["qual"]}_2024_{match_bounds["red_teams"][0]}_{match_bounds["red_teams"][1]}_vs_{match_bounds["blue_teams"][0]}_{match_bounds["blue_teams"][1]}-{match_bounds["red_score"]}_to_{match_bounds["blue_score"]}.mp4'
    print(f'Saving match to {file_name}')

    # Run the ffmpeg command to extract the video
    ffmpeg_command = [
        'ffmpeg', '-ss', str(buffer_start), '-i', url,
        '-t', str(buffer_end - buffer_start),
        '-c', 'copy', file_name, '-y', '-hide_banner', '-loglevel', 'error'
    ]
    subprocess.run(ffmpeg_command)
    print(f'Time to process: {time.time() - start_time} seconds')