#!/usr/bin/env python3

import json
import os
import boto3
import re

def execute(topic, payload):

    returnValue = {}

    try:
        #Incoming payload should be a JSON object
        annunciation = json.loads(payload)

        #Validate the required fields
        if "name" not in annunciation:
            raise Exception("Missing required element \"name\" not found.")

        if "sentences" not in annunciation:
            raise Exception("Missing required element \"sentences\" not found.")

        if len(annunciation["sentences"]) == 0:
            raise Exception("\"sentences\" array was empty.")

        #Set defaults if they were not overridden by the JSON file
        if "outputFormat" not in annunciation:
            annunciation["outputFormat"] = "mp3"
        
        if "voice" not in annunciation:
            annunciation["voice"] = "Matthew"

        if "engine" not in annunciation:
            annunciation["engine"] = "neural"

        if "language" not in annunciation:
            annunciation["language"] = "en-US"

        #Create the filename
        outputFileName = annunciation["name"].lower()
        outputFileName = outputFileName.replace(" ", "_")
        outputFileName = re.sub(r'\W+', '', outputFileName)
        outputFileName = outputFileName + "." + annunciation["outputFormat"].lower()

        if outputFileName == ".mp3":
            raise Exception("The resulting output filename was empty.")

        #Compose the output file
        outputFile = os.path.join("/etc/P5Software/audio/", outputFileName)

        #See if the output file already exists
        if os.path.exists(outputFile) == False:

            #Compose the sentences
            text = "<speak>"

            for sentence in annunciation["sentences"]:
                text = text + "<s>" + sentence + "</s>"

            #Close the text
            text = text + "</speak>"

            #Set the region
            pollyClient = boto3.Session().client('polly')

            #Submit the request to AWS
            pollyResponse = pollyClient.synthesize_speech(
                Engine = annunciation["engine"],
                LanguageCode = annunciation["language"],
                OutputFormat = annunciation["outputFormat"],
                Text = text,
                TextType = 'ssml',
                VoiceId = annunciation["voice"]
            )

            #Write the data to disk
            file = open(outputFile, 'wb')
            file.write(pollyResponse['AudioStream'].read())
            file.close()

            returnValue['fileLocation'] =  outputFile
            returnValue['alreadyExists'] = False
            return returnValue

        else:
            #The file already exists
            returnValue['fileLocation'] =  outputFile
            returnValue['alreadyExists'] = True
            return returnValue

    except Exception as ex:
        returnValue['error'] = ex
        return returnValue