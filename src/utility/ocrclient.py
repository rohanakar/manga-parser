from os import getenv
from .restclient import RestClient
import configparser

config = configparser.ConfigParser()
config.read('./config/config.ini')
base_path = config.get('OCR_CLIENT','base_url')
print(base_path)
apiKey = getenv('ocr_api_key','donotstealthiskey8589')
    

def performOCR(filePath,details=False):
    rest_client = RestClient(base_path)  
    # print(filePath)  
    files = {'file': open(filePath, 'rb')}

    response = rest_client.post("/parse/image",headers={'apikey':apiKey},data={
        'language':'eng',
        'isOverlayRequired':'true',
        'IsCreateSearchablePDF':'false',
        'isSearchablePdfHideTextLayer':'true',
        'detectOrientation':'false',
        'isTable':'false',
        'scale':'true',
        'OCREngine': 5,
        'detectCheckbox':'false',
        'checkboxTemplate':0
    },
    files=files)
    if(details):
        return response.json()['ParsedResults'][0]['TextOverlay']['Lines']
    return response.json()['ParsedResults'][0]['ParsedText']


