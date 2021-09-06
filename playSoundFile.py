#!/usr/bin/env python3

import subprocess
import os


def execute(topic, payload):

    returnValue = []

    #Make sure the file requested exists
    if os.path.exists(payload) == False:
        raise Exception("File does not exist")

    result = subprocess.run(['omxplayer', '-o', 'alsa:hw:0,0', payload])

    if result.returncode != 0:

        message = {}
        message['message'] = result.stderr.decode('ascii').strip()

        returnValue.append(message)

        raise Exception(result.stderr.decode('ascii').strip())

    message = {}
    message['status'] = "DONE"
    returnValue.append(message)

    message = {}
    message['status'] = "IDLE"
    returnValue.append(message)

    return returnValue