from os import getenv

from .fileutils import save as saveFile
from .restclient import RestClient
import configparser
from .enums.Speaker import Speaker

config = configparser.ConfigParser()
config.read('./config/config.ini')
base_path = config.get('TTS_CLIENT','base_url')
print(base_path)
apiKey = getenv('ocr_api_key','donotstealthiskey8589')


speakerMap = {
    Speaker.MALE:('en-gb','Harry'),
    Speaker.FEMALE:('en-gb','Nancy'),
    Speaker.KID:('ja-jp','Hina'),
    Speaker.NARRATOR:('en-au','Jack')

}


def performTTS(text,output_file,speaker=Speaker.MALE):
    rest_client = RestClient(base_path)  
    # print(f"Generating TTS for {text}");
    lang = speakerMap[speaker][0]
    voice = speakerMap[speaker][1]
    # print(f'Language => {lang} , voice => {voice}')
    response = rest_client.get("/controls/speech.ashx",params={
        'hl':lang,
        'v':voice,
        'src':text,
        'c':'mp3'
    },
    headers={
        'referer':'https://www.voicerss.org/api/demo.aspx'
    })
    saveFile(output_file,response.content)




