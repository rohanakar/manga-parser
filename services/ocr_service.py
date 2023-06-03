import base64
from functools import cmp_to_key
import functools
from io import BytesIO
import json
import logging
from os import getenv

import cv2
from image_utils import panel_extractor
from utils import fileutils
from utils.restclient import RestClient
import configparser

config = configparser.ConfigParser()
config.read('config/api.ini')
base_path = config.get('OCR_CLIENT','base_url')
apiKey = getenv('ocr_api_key','donotstealthiskey8589')

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



def performOCR(filePath,details=False):
    rest_client = RestClient(base_path)  
    filePath = fileutils.get_relative_path(input_directory, filePath)
    logger.debug(filePath)  
    panel_order = panel_extractor.generate_panels(filePath,False)  
    files = {'file': open(filePath, 'rb')}

    response = rest_client.post("/parse/image",headers={'apikey':apiKey},data={
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
        # logger.debug(api_reponse)
        api_reponse = combine_nearby_lines(api_reponse['ParsedResults'][0]['TextOverlay']['Lines'])
        panel_diag = panel_sort(api_reponse,panel_order)
        for i,entry in enumerate(panel_diag):
            op.append({'sound_data':sorted([clean(diag) for diag in entry],key=functools.cmp_to_key(order)),'panel':panel_order[i][0:4]})
        # pretty_print(op)
    except Exception as e:
        logger.debug(e)
    return op
    # if(details):
    #     return combine_nearby_lines(response.json()['ParsedResults'][0]['TextOverlay']['Lines'])
    # return response.json()['ParsedResults'][0]['ParsedText']

def test():
    api_reponse = {
    "ParsedResults": [
        {
            "TextOverlay": {
                "Lines": [
                    {
                        "LineText": "RIGHT",
                        "Words": [
                            {
                                "WordText": "RIGHT",
                                "Left": 110.0,
                                "Top": 79.0,
                                "Height": 29.0,
                                "Width": 96.0
                            }
                        ],
                        "MaxHeight": 29.0,
                        "MinTop": 79.0
                    },
                    {
                        "LineText": "HERE,",
                        "Words": [
                            {
                                "WordText": "HERE",
                                "Left": 112.0,
                                "Top": 114.0,
                                "Height": 36.0,
                                "Width": 92.0
                            },
                            {
                                "WordText": ",",
                                "Left": 112.0,
                                "Top": 114.0,
                                "Height": 36.0,
                                "Width": 92.0
                            }
                        ],
                        "MaxHeight": 36.0,
                        "MinTop": 114.0
                    },
                    {
                        "LineText": "WE",
                        "Words": [
                            {
                                "WordText": "WE",
                                "Left": 122.0,
                                "Top": 148.0,
                                "Height": 28.0,
                                "Width": 48.0
                            }
                        ],
                        "MaxHeight": 28.0,
                        "MinTop": 148.0
                    },
                    {
                        "LineText": "MUST",
                        "Words": [
                            {
                                "WordText": "MUST",
                                "Left": 112.0,
                                "Top": 630.0,
                                "Height": 28.0,
                                "Width": 100.0
                            }
                        ],
                        "MaxHeight": 28.0,
                        "MinTop": 630.0
                    },
                    {
                        "LineText": "SURPASS",
                        "Words": [
                            {
                                "WordText": "SURPASS",
                                "Left": 76.0,
                                "Top": 662.0,
                                "Height": 31.0,
                                "Width": 155.0
                            }
                        ],
                        "MaxHeight": 31.0,
                        "MinTop": 662.0
                    },
                    {
                        "LineText": "AND DEFEAT",
                        "Words": [
                            {
                                "WordText": "AND",
                                "Left": 58.0,
                                "Top": 697.0,
                                "Height": 30.0,
                                "Width": 73.0
                            },
                            {
                                "WordText": "DEFEAT",
                                "Left": 131.0,
                                "Top": 697.0,
                                "Height": 30.0,
                                "Width": 113.0
                            }
                        ],
                        "MaxHeight": 30.0,
                        "MinTop": 697.0
                    },
                    {
                        "LineText": "YOUII",
                        "Words": [
                            {
                                "WordText": "YOUII",
                                "Left": 104.0,
                                "Top": 733.0,
                                "Height": 28.0,
                                "Width": 96.0
                            }
                        ],
                        "MaxHeight": 28.0,
                        "MinTop": 733.0
                    },
                    {
                        "LineText": "YOU NO",
                        "Words": [
                            {
                                "WordText": "YOU",
                                "Left": 62.0,
                                "Top": 877.0,
                                "Height": 26.0,
                                "Width": 54.0
                            },
                            {
                                "WordText": "NO",
                                "Left": 115.0,
                                "Top": 877.0,
                                "Height": 26.0,
                                "Width": 41.0
                            }
                        ],
                        "MaxHeight": 26.0,
                        "MinTop": 877.0
                    },
                    {
                        "LineText": "LONGER",
                        "Words": [
                            {
                                "WordText": "LONGER",
                                "Left": 62.0,
                                "Top": 903.0,
                                "Height": 27.0,
                                "Width": 98.0
                            }
                        ],
                        "MaxHeight": 27.0,
                        "MinTop": 903.0
                    },
                    {
                        "LineText": "HAVE",
                        "Words": [
                            {
                                "WordText": "HAVE",
                                "Left": 78.0,
                                "Top": 929.0,
                                "Height": 25.0,
                                "Width": 66.0
                            }
                        ],
                        "MaxHeight": 25.0,
                        "MinTop": 929.0
                    },
                    {
                        "LineText": "UNDINE...",
                        "Words": [
                            {
                                "WordText": "UNDINE",
                                "Left": 50.0,
                                "Top": 953.0,
                                "Height": 26.0,
                                "Width": 108.0
                            },
                            {
                                "WordText": "...",
                                "Left": 50.0,
                                "Top": 953.0,
                                "Height": 26.0,
                                "Width": 108.0
                            }
                        ],
                        "MaxHeight": 26.0,
                        "MinTop": 953.0
                    },
                    {
                        "LineText": "@steams.owwwwwwwwwils",
                        "Words": [
                            {
                                "WordText": "@",
                                "Left": 414.0,
                                "Top": 454.0,
                                "Height": 48.0,
                                "Width": 95.0
                            },
                            {
                                "WordText": "steams.owwwwwwwwwils",
                                "Left": 414.0,
                                "Top": 454.0,
                                "Height": 48.0,
                                "Width": 95.0
                            }
                        ],
                        "MaxHeight": 48.0,
                        "MinTop": 454.0
                    },
                    {
                        "LineText": "BUT",
                        "Words": [
                            {
                                "WordText": "BUT",
                                "Left": 350.0,
                                "Top": 542.0,
                                "Height": 26.0,
                                "Width": 50.0
                            }
                        ],
                        "MaxHeight": 26.0,
                        "MinTop": 542.0
                    },
                    {
                        "LineText": "YOURE NO",
                        "Words": [
                            {
                                "WordText": "YOURE",
                                "Left": 304.0,
                                "Top": 555.0,
                                "Height": 45.0,
                                "Width": 85.0
                            },
                            {
                                "WordText": "NO",
                                "Left": 390.0,
                                "Top": 555.0,
                                "Height": 44.0,
                                "Width": 38.0
                            }
                        ],
                        "MaxHeight": 45.0,
                        "MinTop": 555.0
                    },
                    {
                        "LineText": "LONGER THE",
                        "Words": [
                            {
                                "WordText": "LONGER",
                                "Left": 294.0,
                                "Top": 602.0,
                                "Height": 24.0,
                                "Width": 98.0
                            },
                            {
                                "WordText": "THE",
                                "Left": 391.0,
                                "Top": 602.0,
                                "Height": 24.0,
                                "Width": 47.0
                            }
                        ],
                        "MaxHeight": 24.0,
                        "MinTop": 602.0
                    },
                    {
                        "LineText": "ACIER SILVA",
                        "Words": [
                            {
                                "WordText": "ACIER",
                                "Left": 300.0,
                                "Top": 631.0,
                                "Height": 26.0,
                                "Width": 67.0
                            },
                            {
                                "WordText": "SILVA",
                                "Left": 366.0,
                                "Top": 632.0,
                                "Height": 26.0,
                                "Width": 66.0
                            }
                        ],
                        "MaxHeight": 26.0,
                        "MinTop": 631.0
                    },
                    {
                        "LineText": "WE KNOW!",
                        "Words": [
                            {
                                "WordText": "WE",
                                "Left": 302.0,
                                "Top": 660.0,
                                "Height": 29.0,
                                "Width": 44.0
                            },
                            {
                                "WordText": "KNOW",
                                "Left": 345.0,
                                "Top": 659.0,
                                "Height": 29.0,
                                "Width": 83.0
                            },
                            {
                                "WordText": "!",
                                "Left": 345.0,
                                "Top": 659.0,
                                "Height": 29.0,
                                "Width": 83.0
                            }
                        ],
                        "MaxHeight": 30.0,
                        "MinTop": 659.0
                    },
                    {
                        "LineText": "YOU MAY",
                        "Words": [
                            {
                                "WordText": "YOU",
                                "Left": 534.0,
                                "Top": 510.0,
                                "Height": 29.0,
                                "Width": 62.0
                            },
                            {
                                "WordText": "MAY",
                                "Left": 595.0,
                                "Top": 509.0,
                                "Height": 29.0,
                                "Width": 51.0
                            }
                        ],
                        "MaxHeight": 29.0,
                        "MinTop": 509.0
                    },
                    {
                        "LineText": "BE ACIER",
                        "Words": [
                            {
                                "WordText": "BE",
                                "Left": 526.0,
                                "Top": 543.0,
                                "Height": 30.0,
                                "Width": 47.0
                            },
                            {
                                "WordText": "ACIER",
                                "Left": 573.0,
                                "Top": 543.0,
                                "Height": 31.0,
                                "Width": 80.0
                            }
                        ],
                        "MaxHeight": 31.0,
                        "MinTop": 543.0
                    },
                    {
                        "LineText": "SILVA...",
                        "Words": [
                            {
                                "WordText": "SILVA",
                                "Left": 542.0,
                                "Top": 580.0,
                                "Height": 34.0,
                                "Width": 90.0
                            },
                            {
                                "WordText": "...",
                                "Left": 542.0,
                                "Top": 580.0,
                                "Height": 34.0,
                                "Width": 90.0
                            }
                        ],
                        "MaxHeight": 34.0,
                        "MinTop": 580.0
                    },
                    {
                        "LineText": "..NOELLE...",
                        "Words": [
                            {
                                "WordText": "..",
                                "Left": 448.0,
                                "Top": 925.0,
                                "Height": 32.0,
                                "Width": 116.0
                            },
                            {
                                "WordText": "NOELLE",
                                "Left": 448.0,
                                "Top": 925.0,
                                "Height": 32.0,
                                "Width": 116.0
                            },
                            {
                                "WordText": "...",
                                "Left": 448.0,
                                "Top": 925.0,
                                "Height": 32.0,
                                "Width": 116.0
                            }
                        ],
                        "MaxHeight": 32.0,
                        "MinTop": 925.0
                    },
                    {
                        "LineText": "\" YOU REALLY",
                        "Words": [
                            {
                                "WordText": "\"",
                                "Left": 444.0,
                                "Top": 1010.0,
                                "Height": 40.0,
                                "Width": 27.0
                            },
                            {
                                "WordText": "YOU",
                                "Left": 472.0,
                                "Top": 1011.0,
                                "Height": 40.0,
                                "Width": 49.0
                            },
                            {
                                "WordText": "REALLY",
                                "Left": 522.0,
                                "Top": 1011.0,
                                "Height": 41.0,
                                "Width": 84.0
                            }
                        ],
                        "MaxHeight": 41.0,
                        "MinTop": 1010.0
                    },
                    {
                        "LineText": "HAVE GROWN",
                        "Words": [
                            {
                                "WordText": "HAVE",
                                "Left": 462.0,
                                "Top": 1049.0,
                                "Height": 30.0,
                                "Width": 62.0
                            },
                            {
                                "WordText": "GROWN",
                                "Left": 524.0,
                                "Top": 1049.0,
                                "Height": 30.0,
                                "Width": 88.0
                            }
                        ],
                        "MaxHeight": 31.0,
                        "MinTop": 1049.0
                    },
                    {
                        "LineText": "L STRONGER,",
                        "Words": [
                            {
                                "WordText": "L",
                                "Left": 444.0,
                                "Top": 1069.0,
                                "Height": 32.0,
                                "Width": 30.0
                            },
                            {
                                "WordText": "STRONGER",
                                "Left": 474.0,
                                "Top": 1069.0,
                                "Height": 32.0,
                                "Width": 124.0
                            },
                            {
                                "WordText": ",",
                                "Left": 474.0,
                                "Top": 1069.0,
                                "Height": 32.0,
                                "Width": 124.0
                            }
                        ],
                        "MaxHeight": 32.0,
                        "MinTop": 1069.0
                    },
                    {
                        "LineText": "BUT",
                        "Words": [
                            {
                                "WordText": "BUT",
                                "Left": 506.0,
                                "Top": 1105.0,
                                "Height": 20.0,
                                "Width": 42.0
                            }
                        ],
                        "MaxHeight": 20.0,
                        "MinTop": 1105.0
                    },
                    {
                        "LineText": "I'VE",
                        "Words": [
                            {
                                "WordText": "I'VE",
                                "Left": 756.0,
                                "Top": 106.0,
                                "Height": 24.0,
                                "Width": 50.0
                            }
                        ],
                        "MaxHeight": 24.0,
                        "MinTop": 106.0
                    },
                    {
                        "LineText": "ONLY MET",
                        "Words": [
                            {
                                "WordText": "ONLY",
                                "Left": 732.0,
                                "Top": 132.0,
                                "Height": 24.0,
                                "Width": 56.0
                            },
                            {
                                "WordText": "MET",
                                "Left": 787.0,
                                "Top": 132.0,
                                "Height": 24.0,
                                "Width": 45.0
                            }
                        ],
                        "MaxHeight": 24.0,
                        "MinTop": 132.0
                    },
                    {
                        "LineText": "HER SPIRIT",
                        "Words": [
                            {
                                "WordText": "HER",
                                "Left": 728.0,
                                "Top": 158.0,
                                "Height": 24.0,
                                "Width": 47.0
                            },
                            {
                                "WordText": "SPIRIT",
                                "Left": 774.0,
                                "Top": 158.0,
                                "Height": 24.0,
                                "Width": 64.0
                            }
                        ],
                        "MaxHeight": 24.0,
                        "MinTop": 158.0
                    },
                    {
                        "LineText": "BEFORE,",
                        "Words": [
                            {
                                "WordText": "BEFORE",
                                "Left": 738.0,
                                "Top": 184.0,
                                "Height": 30.0,
                                "Width": 90.0
                            },
                            {
                                "WordText": ",",
                                "Left": 738.0,
                                "Top": 184.0,
                                "Height": 30.0,
                                "Width": 90.0
                            }
                        ],
                        "MaxHeight": 30.0,
                        "MinTop": 184.0
                    },
                    {
                        "LineText": "BUT..",
                        "Words": [
                            {
                                "WordText": "BUT",
                                "Left": 754.0,
                                "Top": 210.0,
                                "Height": 24.0,
                                "Width": 46.0
                            },
                            {
                                "WordText": "..",
                                "Left": 754.0,
                                "Top": 210.0,
                                "Height": 24.0,
                                "Width": 46.0
                            }
                        ],
                        "MaxHeight": 24.0,
                        "MinTop": 210.0
                    },
                    {
                        "LineText": "THAT",
                        "Words": [
                            {
                                "WordText": "THAT",
                                "Left": 756.0,
                                "Top": 648.0,
                                "Height": 24.0,
                                "Width": 60.0
                            }
                        ],
                        "MaxHeight": 24.0,
                        "MinTop": 648.0
                    },
                    {
                        "LineText": "DEFINITELY",
                        "Words": [
                            {
                                "WordText": "DEFINITELY",
                                "Left": 722.0,
                                "Top": 675.0,
                                "Height": 28.0,
                                "Width": 122.0
                            }
                        ],
                        "MaxHeight": 28.0,
                        "MinTop": 675.0
                    },
                    {
                        "LineText": "WAS MY",
                        "Words": [
                            {
                                "WordText": "WAS",
                                "Left": 740.0,
                                "Top": 703.0,
                                "Height": 26.0,
                                "Width": 54.0
                            },
                            {
                                "WordText": "MY",
                                "Left": 793.0,
                                "Top": 703.0,
                                "Height": 26.0,
                                "Width": 35.0
                            }
                        ],
                        "MaxHeight": 26.0,
                        "MinTop": 703.0
                    },
                    {
                        "LineText": "MOTHER!",
                        "Words": [
                            {
                                "WordText": "MOTHER",
                                "Left": 736.0,
                                "Top": 733.0,
                                "Height": 31.0,
                                "Width": 100.0
                            },
                            {
                                "WordText": "!",
                                "Left": 736.0,
                                "Top": 733.0,
                                "Height": 31.0,
                                "Width": 100.0
                            }
                        ],
                        "MaxHeight": 31.0,
                        "MinTop": 733.0
                    }
                ],
                "HasOverlay": True
            },
            "TextOrientation": "0",
            "FileParseExitCode": 1,
            "ParsedText": "RIGHT\nHERE,\nWE\nMUST\nSURPASS\nAND DEFEAT\nYOUII\nYOU NO\nLONGER\nHAVE\nUNDINE...\n@steams.owwwwwwwwwils\nBUT\nYOURE NO\nLONGER THE\nACIER SILVA\nWE KNOW!\nYOU MAY\nBE ACIER\nSILVA...\n..NOELLE...\n\" YOU REALLY\nHAVE GROWN\nL STRONGER,\nBUT\nI'VE\nONLY MET\nHER SPIRIT\nBEFORE,\nBUT..\nTHAT\nDEFINITELY\nWAS MY\nMOTHER!",
            "ErrorMessage": "",
            "ErrorDetails": ""
        }
    ],
    "OCRExitCode": 1,
    "IsErroredOnProcessing": False,
    "ProcessingTimeInMilliseconds": "6578",
    "SearchablePDFURL": "Searchable PDF not generated as it was not requested."
    }
    panel_order = [[676, 0, 900, 827], [274, 0, 674, 827], [39, 23, 273, 826], [633, 854, 900, 1248], [39, 852, 632, 1325]]
    api_reponse = combine_nearby_lines(api_reponse['ParsedResults'][0]['TextOverlay']['Lines'])
    panel_diag = panel_sort(api_reponse,panel_order)
    op = []
    for entry in panel_diag:
        op.append(sorted([clean(diag) for diag in entry],key=functools.cmp_to_key(order)))
    pretty_print(op)

if(__name__ == '__main__'):
    test()