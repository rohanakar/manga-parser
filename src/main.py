import json
from utility.ocrclient import performOCR
import utility.fileutils as fileutils
import service.ocr_engine as ocr_engine
from utility.ttsclient import performTTS
from utility.video_generation_utils import generate_video,combine_video_and_clean_up, delete_folder
import time

def main():
    folder_map = fileutils.list_pending_image_pair('/Users/rischaud/opensrc/manga-parser/resources')
    for folder_path in folder_map:
        inbox_folder_path = folder_path
        try:
            start = time.time()
            images = folder_map[folder_path]
            for image_pair in images:
                print(f'***********  performing ocr => {image_pair[0]}  ***********')
                text = performOCR(image_pair[0],details=True)
                texts = combine_nearby_lines(text)
                print(f'***********  processing ocr text together => {image_pair[0]} ***********')
                i=0
                folder_path = fileutils.replace_extension(image_pair[1],'')
                folder_path+="/"
                fileutils.create_folder(folder_path);
                output_clip = fileutils.replace_extension(image_pair[1],'.mp4')
                metadata = {'image':image_pair[0],'sounds':[],'output':output_clip}
                print(f'***********  processing tts  => {image_pair[0]} ***********')
                for s in texts:
                    i+=1    
                    op_file = folder_path+str(i)+'.mp3' 
                    performTTS(s['LineText'],op_file)
                    metadata['sounds'].append(
                        {
                            'location':op_file,
                            'top':s['MinTop'],
                            'left':s['Words'][0]['Left']
                        }
                    )
                metadata_file = folder_path+'metadata.json'

                print(f'***********  preparing metadata file at => {metadata_file} ***********')
                fileutils.save(metadata_file,json.dumps(metadata),writeType='w')
                print(f'***********  Generating clip for => {output_clip} ***********')
                generate_video(metadata_file)
            print(f'***********  Combing clips and cleaning up => {inbox_folder_path} ***********')
            combine_video_and_clean_up()
            delete_folder(inbox_folder_path)
            end = time.time()
            print(f'\n \n \n ****************    {inbox_folder_path}   ***********')
            print(f' ****************    time taken {end-start}   ***********')
        except Exception as e:
            print(e)

    # generate_video(metadata_file='/Users/rischaud/opensrc/manga-parser/resources/processing/black-clover-chapter-359/clovertcb_359_001/metadata.json')

def combine_nearby_lines(lines, buffer_length=30, max_horizontal_distance=75):
    output = []
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


if __name__ == '__main__':
    main()