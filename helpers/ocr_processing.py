import os
import subprocess
import cv2
import pytesseract

def frame_at_time(time_stamp, url):
    output_file = 'TempImages/frame.jpg'
    if os.path.exists(output_file):
        os.remove(output_file)
    options = ['-ss', str(time_stamp), '-i', url, '-frames:v', '1', '-q:v', '1', output_file, '-hide_banner', '-loglevel', 'error']
    return subprocess.run(['ffmpeg'] + options)

def grab_match_info(qual=True, div=True):
    frame = cv2.imread('TempImages/frame.jpg')
    frame = cv2.bitwise_not(frame)
    frame = cv2.convertScaleAbs(frame, alpha=1.0, beta=0)
    frame = cv2.GaussianBlur(frame, (5, 5), 0)

    threshold_value = 40
    _, frame = cv2.threshold(frame, threshold_value, 255, cv2.THRESH_BINARY)


    if qual:
        temp = frame[27:83, 600:800]
        temp = cv2.copyMakeBorder(temp, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=(255,255,255))
        cv2.imwrite('TempImages/QualNumber.jpg', temp)

    if div:
        div_frame = frame[5:80, 770:1140]
        cv2.imwrite('TempImages/Division.jpg', div_frame)

def get_cur_match():
    frame = cv2.imread('TempImages/QualNumber.jpg')

    raw_match_val = pytesseract.image_to_string(frame, config='--psm 6 -c tessedit_char_whitelist=0123456789').strip()
    # Normalize and validate the output to ensure it contains only digits
    normalized_match_val = ''.join(char if char != 'O' else '0' for char in raw_match_val if char.isdigit() or char == 'O')

    return normalized_match_val


def get_cur_div():
    frame = cv2.imread('TempImages/Division.jpg')
    frame = cv2.bitwise_not(frame)
    frame = cv2.convertScaleAbs(frame, alpha=3.0, beta=0)
    return pytesseract.image_to_string(frame, config='--psm 6').strip()