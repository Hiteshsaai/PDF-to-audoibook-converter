# Importing the required libraries 
import fitz
import json
import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import copy 
import os
from google.cloud import texttospeech
from tqdm import tqdm


class pdf_to_audio_converter:

    # Converting the pdf to text 
    def pdfToText(self, filename):
        doc = fitz.open(filename)
        allText = ''
        # count = 1
        pageNo = 1
        for page in doc:
            # sizes =[]
            # texts = []
            # bold = []

            displayList = page.getDisplayList()

            textPage = displayList.getTextPage()

            getJsonStr = textPage.extractJSON()

            getJson = json.loads(getJsonStr)

            for block in getJson['blocks']:
                for line in block['lines']:
                    allText =  allText + '\n'
                    for span in line['spans']:
                        sentence = span['text']
                        # font_size = span['size']
                        # font = span['font'].lower()
                        
                        if sentence.replace(" ", "").isdigit():
                            continue
                        
    #                     font_median = font_analysis(filename)
                        
    #                     if font_size > 20 and 'bold' in font:
    #                         allText += f'Title {count}' + '\n' + sentence
    #                         count += 1
    #                         continue
                            
                        allText += sentence
            pageNo += 1
            
        return allText

    def text_to_audio(self):
        # we don't want a full GUI, so keep the root window from appearing
        Tk().withdraw()

        # open the dialog GUI to Select the directory location
        filelocation = askopenfilename() 

        # Converting the pdf to text(str)
        allText = self.pdfToText(filelocation)

        # Importing Google Vision private key file for the service 
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/hiteshsaaimanancherypanneerselvam/Documents/Development_Projects/pdf_to_audiobook/My First Project-1f1b9b4bc545.json"

        if len(allText) >= 4800:

            #calculating the iteration for pdf text by 4800 (as google vision can take only 5000 per request)
            tot_iteration, tot_division = len(allText)//4800, len(allText)/4800

            # Checking if partition of the has to be done
            start = 0 
            end = 4800
            for countOfPart in range(1, tot_iteration+1):

                globals()['part%s' % countOfPart] = allText[start:end]
                countOfPart += 1
                start = copy.deepcopy(end) 
                end = end + 4800

            if len(allText)%4800 != 0:

                leftover = int(4800*(tot_division - tot_iteration))
                final_end = start + leftover
                globals()['part%s' % countOfPart] = allText[start: end]

            

            # Instantiates a client
            client = texttospeech.TextToSpeechClient()


            for part in tqdm(range(1, countOfPart+1)):
                # Set the text input to be synthesized
                synthesis_input = texttospeech.SynthesisInput(text= globals()['part%s' % part])

                # Build the voice request, select the language code ("en-US") and the ssml
                # voice gender ("neutral")
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
                )

                # Select the type of audio file you want returned
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3
                )

                # Perform the text-to-speech request on the text input with the selected
                # voice parameters and audio file type
                response = client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )

                file_name = filelocation.split('/')[-1].split('.')[0]
                folder_name = f'{file_name}_audio_folder'
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)
                # The response's audio_content is binary.
                with open(f'{folder_name}/part_{part}.mp3', "wb") as out:
                    # Write the response to the output file.
                    out.write(response.audio_content)
                    print(f'Audio content written to file {folder_name}/part_{part}.mp3')
        else:
            
            # Instantiates a client
            client = texttospeech.TextToSpeechClient()

            # Set the text input to be synthesized
            synthesis_input = texttospeech.SynthesisInput(text= allText)

            # Build the voice request, select the language code ("en-US") and the ssml
            # voice gender ("neutral")
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )

            # Select the type of audio file you want returned
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            # Perform the text-to-speech request on the text input with the selected
            # voice parameters and audio file type
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            file_name = filelocation.split('/')[-1].split('.')[0]
            folder_name = f'{file_name}_audio_folder'
            
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            # The response's audio_content is binary.
            with open(f'{folder_name}/{file_name}_audio.mp3', "wb") as out:
                # Write the response to the output file.
                out.write(response.audio_content)
                print(f'Audio content written to file {folder_name}/{file_name}_audio.mp3')



if __name__ == "__main__":

    try:
        pdf_to_audio_converter().text_to_audio()
        print("")
        print("Your Audio book is ready!!")
        print("Enjoy Listening")
        print("/n")

    except Exception as e:
        print(e)