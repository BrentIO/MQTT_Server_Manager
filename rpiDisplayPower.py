#!/usr/bin/env python3

import subprocess


def execute(topic, payload):

    returnValue = {}

    #Determine if we are GETTING the value or SETTING the value
    if topic.endswith("/get"):
        returnValue['display'] = getDisplayPower()
        return returnValue

    if topic.endswith("/set"):

        returnValue['display'] = "INVALID_REQUEST"

        payload = payload.strip().upper()

        if payload == "ON":
            returnValue['display'] = setDisplayPower("1")
            return returnValue

        if payload == "OFF":
            returnValue['display'] = setDisplayPower("0")
            return returnValue

        returnValue['display'] = "INVALID_REQUEST"
    
        return returnValue


def setDisplayPower(value):
    
    result = subprocess.run(['vcgencmd', 'display_power', value], stdout=subprocess.PIPE)

    #Get the response from the OS, convert it to ascii, and remove any trailing characters
    osResponse = result.stdout.decode('ascii').strip()
    
    if osResponse.split("=")[1] == "1":
        return "ON"

    if osResponse.split("=")[1] == "0":
        return "OFF"
    else:
        return "UNKNOWN"


def getDisplayPower():

    result = subprocess.run(['vcgencmd', 'display_power'], stdout=subprocess.PIPE)

    #Get the response from the OS, convert it to ascii, and remove any trailing characters
    osResponse = result.stdout.decode('ascii').strip()
    
    if osResponse.split("=")[1] == "1":
        return "ON"

    if osResponse.split("=")[1] == "0":
        return "OFF"
    else:
        return "UNKNOWN"