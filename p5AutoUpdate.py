#!/usr/bin/env python3

import subprocess


def execute(topic, payload):

    returnValue = {}

    result = subprocess.run(['bash', '/etc/P5Software/Linux-Tools/AutoUpdate.sh'])

    if result.returncode != 0:

        returnValue['message'] = result.stderr.decode('ascii').strip()

        raise Exception(result.stderr.decode('ascii').strip())

    returnValue['P5SoftwareAutoUpdate'] = "DONE"

    return returnValue