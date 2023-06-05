import base64
from functools import cmp_to_key
import functools
from io import BytesIO
import io
import json
import logging
from os import getenv
import os
import signal
from PIL import Image

import cv2
from image_utils import panel_extractor
from utils import fileutils
from utils.restclient import RestClient
import configparser

config = configparser.ConfigParser()
config.read('config/api.ini')
base_path = config.get('OCR_CLIENT','base_url')
apiKeys = [getenv('ocr_api_key_1','ocr_api_key_1'),getenv('ocr_api_key_2','ocr_api_key_2')]

counter = 0
config.read('config/app.ini')
input_directory = config.get('DEFAULT','inbox_folder')
logger = logging.getLogger(__name__)

def order(diag1,diag2):
    return -diag1["x1"]+diag2["x1"]
 
def clean(diag):
    op = {}
    op['LineText'] = diag['LineText']
    op['x1'] = min(word["Left"] for word in diag["Words"])
    op['y1'] = min(word["Top"] for word in diag["Words"])
    op['x2'] = max(word["Left"]+word["Width"] for word in diag["Words"])
    op['y2'] = max(word["Top"]+word["Height"] for word in diag["Words"])
    return op

def is_in(rect,panel):
    x1 = min(word["Left"] for word in panel["Words"])
    y1 = min(word["Top"] for word in panel["Words"])
    x2 = max(word["Left"]+word["Width"] for word in panel["Words"])
    y2 = max(word["Top"]+word["Height"] for word in panel["Words"])
    return x1>=rect[0] and x2<=rect[2] and y1>=rect[1] and y2<=rect[3]

def panel_sort(lines,panels):
    op = []
    for panel in panels:
        panel_diag = []
        for line in lines:
            if(is_in(panel,line)):
                panel_diag.append(line)
        panel_diag = combine_nearby_lines(panel_diag)
        op.append(panel_diag)
    return op

def pretty_print(panel_diag):
    print(json.dumps(panel_diag,indent=2))
    

def combine_nearby_lines(lines, buffer_length=30, max_horizontal_distance=75):
    output = []
    if not lines:
        return lines
    current_line = lines[0]

    for line in lines[1:]:
        if (
            line["MinTop"] <= current_line["MinTop"] + current_line["MaxHeight"] + buffer_length
            and line["Words"][0]["Left"] - current_line["Words"][-1]["Left"] <= max_horizontal_distance
        ):
            # last_word = current_line["Words"][-1]["WordText"]
            # if last_word.endswith("-"):
            #     last_word = last_word[:-1]  # Remove the trailing '-'
            current_line["LineText"] += " " + line["LineText"]
            current_line["Words"] += line["Words"]
            # current_line["Words"][-1]["WordText"] = last_word  # Update the last word
            current_line["MaxHeight"] = current_line["MaxHeight"] + line["MaxHeight"] + buffer_length
        else:
            output.append(current_line)
            current_line = line
    
    output.append(current_line)
    return output

def convert_to_jpeg(image_path):
    # Open the image

    image = Image.open(image_path)
    image = image.convert('RGB')
    temp_file = 'a.jpeg'
    image.save(temp_file, format='JPEG')
    image_binary =  open(temp_file, 'rb')
    os.remove(temp_file)
    return image_binary

def kill_current_task():
    os.kill(os.getpid(), signal.SIGINT)

def performOCR(filePath,details=False):
    rest_client = RestClient(base_path)  
    filePath = fileutils.get_relative_path(input_directory, filePath)
    logger.debug(filePath)  
    panel_order = panel_extractor.generate_panels(filePath,False)  
    image_size = os.path.getsize(filePath)
    if image_size > 1000000:
        file = convert_to_jpeg(filePath)
    else:
        file =  open(filePath, 'rb')
    files = {'file':file}
    global counter 
    counter = (counter+1)%2
    logger.debug(f'counter {counter}')
    response = rest_client.post("/parse/image",headers={'apikey':apiKeys[counter]},data={
            'language':'eng',
            'isOverlayRequired':'true',
            'IsCreateSearchablePDF':'false',
            'isSearchablePdfHideTextLayer':'true',
            'detectOrientation':'false',
            'isTable':'false',
            'scale':'true',
            'OCREngine': 2,
            'detectCheckbox':'false',
            'checkboxTemplate':0
            },
        files=files)
    op = []
    
    try:
        api_reponse = response.json()
        logger.debug(api_reponse)
        logger.debug(api_reponse['OCRExitCode'],api_reponse['IsErroredOnProcessing'],api_reponse['ErrorMessage'])
        # api_reponse = combine_nearby_lines(api_reponse['ParsedResults'][0]['TextOverlay']['Lines'])
        api_reponse = api_reponse['ParsedResults'][0]['TextOverlay']['Lines']

        panel_diag = panel_sort(api_reponse,panel_order)
        
        for i,entry in enumerate(panel_diag):
            op.append({'sound_data':sorted([clean(diag) for diag in entry],key=functools.cmp_to_key(order)),'panel':panel_order[i][0:4]})
    except Exception as e:
        logger.warn(f"KILLING PROCESS -> OCR API with key => {apiKeys[counter]}")
        logger.error(e)
        kill_current_task()
    return op
    # if(details):
    #     return combine_nearby_lines(response.json()['ParsedResults'][0]['TextOverlay']['Lines'])
    # return response.json()['ParsedResults'][0]['ParsedText']
