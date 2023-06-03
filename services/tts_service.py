import logging
from os import getenv

from utils.restclient import RestClient
import configparser
from utils import fileutils

config = configparser.ConfigParser()
config.read('config/api.ini')
base_path = config.get('TTS_CLIENT','base_url')
apiKey = getenv('ocr_api_key',config.get('TTS_CLIENT','api_key'))
logger = logging.getLogger(__name__)

speakerMap = {
    'MALE':('en-gb','Harry'),
    'FEMALE':('en-gb','Nancy'),
    'KID':('ja-jp','Hina'),
    'NARRATOR':('en-au','Jack')

}


def performTTS(text,output_file,speaker='MALE'):
    rest_client = RestClient(base_path)  
    logger.debug(f"Generating TTS for {text}");
    lang = speakerMap[speaker][0]
    voice = speakerMap[speaker][1]
    logger.debug(f'Language => {lang} , voice => {voice}')
    response = rest_client.get("/controls/speech.ashx",params={
        'hl':lang,
        'v':voice,
        'src':text,
        'c':'mp3'
    },
    headers={
        'referer':'https://www.voicerss.org/api/demo.aspx'
    })
    fileutils.writeToFile(output_file,response.content)




