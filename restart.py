#!/usr/bin/env python3

import subprocess


def execute(topic, payload):

    returnValue = {}

    result = subprocess.run(['shutdown', '-r'], stderr=subprocess.PIPE)

    if result.returncode != 0:

        returnValue['message'] = result.stderr.decode('ascii').strip()

        raise Exception(result.stderr.decode('ascii').strip())

    returnValue['message'] = "OK"

    return returnValue