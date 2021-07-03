#!/usr/bin/env python3

import logging
import importlib
import json
import paho.mqtt.client as mqtt
import logging.handlers as handlers
from pkgutil import iter_modules
import os
import json
import socket


def on_connect(client, userdata, flags, rc):
    #########################################################
    # Handles MQTT Connections
    #########################################################

    try:
        if rc != 0:
            logger.warning("Failed to connect to MQTT.  Response code: " + str(rc))

        else:
            logger.info("MQTT connected to " + settings["mqtt"]["serverName"])

    except Exception as ex:
        logger.error(ex)
        
def on_message(client, userdata, msg):
    #########################################################
    # Handles MQTT Message Receipt
    #########################################################

    #Find the handler
    for skill in skills['loaded']:
        if skill['requestTopic'] == msg.topic:
            logger.info("Received message on " + msg.topic + " will be handled by " + skill['name'])

            targetModule = importlib.import_module(skill['name'])
            returnValue = targetModule.execute(msg.payload.decode('UTF-8'))

            mqttClient.publish(skill['responseTopic'], json.dumps(returnValue))
            logger.info("Sent message on " + skill['responseTopic'])

def setLogLevel(logLevel):

    logLevel = logLevel.lower()

    if logLevel == "notset":
        logger.setLevel(logging.NOTSET)

    if logLevel == "info":
        logger.setLevel(logging.INFO)

    if logLevel == "error":
        logger.setLevel(logging.ERROR)

    if logLevel == "warning":
        logger.setLevel(logging.WARNING)   

    if logLevel == "critical":
        logger.setLevel(logging.CRITICAL)
    
    logger.critical("Log level set to " + logLevel.upper())   

def setup():

    try:

        #Ensure the settings are valid
        if "mqtt" not in settings:
            raise Exception("Settings file is missing \"mqtt\".")

        if "username" not in settings["mqtt"]:
            raise Exception("\"username\" is missing from the \"mqtt\" object in the settings file.")
        
        if "password" not in settings["mqtt"]:
            raise Exception("\"password\" is missing from the \"mqtt\" object in the settings file.")

        if "serverName" not in settings["mqtt"]:
            raise Exception("\"serverName\" is missing from the \"mqtt\" object in the settings file.")

        if "port" not in settings["mqtt"]:
            settings["mqtt"]["port"] = 1883

        if "logLevel" not in settings:
            settings["logLevel"] = "info"

        #Set the log level from the settings file
        setLogLevel(settings["logLevel"])

        skillCount = 0

        for skill in skills['defined']:

            if "enabled" not in skill:
                logger.critical("Skill at element " + str(skillCount) + " does not have an enabled element.  The skill will not be loaded.")
                continue

            if "name" not in skill:
                logger.critical("Skill at element " + str(skillCount) + " does not have a name element.  The skill will not be loaded.")
                continue

            skillCount = skillCount + 1

            if skill["enabled"] == False:
                logger.info("Skipping skill \"" + skill["name"] + "\" because it is disabled.")
                continue

            if "requiredPackages" not in skill:
                logger.critical(skill["name"] + " does not contain an array of required packages.  The skill will not be loaded.")
                continue

            #Check for the rquired packages for this skill 
            if checkPackages(skill["name"], skill["requiredPackages"]) == False:
                continue

            #Check MQTT topics
            if "requestTopic" not in skill:
                logger.critical(skill["name"] + " does not contain element \"requestTopic\".  The skill will not be loaded.")
                continue

            if len(skill["requestTopic"].strip()) == 0 or skill["requestTopic"].strip() == "*":
                logger.critical(skill["name"] + " does not have a valid requestTopic.  The skill will not be loaded.")
                continue


            if "responseTopic" not in skill:
                logger.critical(skill["name"] + " does not contain element \"responseTopic\".  The skill will not be loaded.")
                continue

            if len(skill["responseTopic"].strip()) == 0 or skill["responseTopic"].strip() == "*":
                logger.critical(skill["name"] + " does not have a valid responseTopic.  The skill will not be loaded.")
                continue

            tmpSkill = {}

            tmpSkill['name'] = skill["name"]
            tmpSkill['requestTopic'] = replaceMQTTTopicTokens(skill["requestTopic"])
            tmpSkill['responseTopic'] = replaceMQTTTopicTokens(skill["responseTopic"])

            #Register the skill
            skills['loaded'].append(tmpSkill)
            logger.info(skill["name"] + " skill installed sucessfully.")
            
    except Exception as ex:
        logger.critical(ex)
        print("Check logs.")
        quit()

def main():

    try:

        #Setup the handlers for connection and messages
        mqttClient.on_connect = on_connect
        mqttClient.on_message = on_message

        #Create the MQTT credentials from the settings file
        mqttClient.username_pw_set(settings["mqtt"]["username"], password=settings["mqtt"]["password"])

        #Connect to MQTT
        mqttClient.connect(settings["mqtt"]["serverName"], port=settings["mqtt"]["port"], keepalive=60)

        #Subscribe to the loaded topics
        for skill in skills['loaded']:
            mqttClient.subscribe(skill["requestTopic"])
            logger.info("Subscribed to request topic " + skill["requestTopic"])

        #Listen
        mqttClient.loop_forever()

    except KeyboardInterrupt:
        print("\n")
        quit()

    except Exception as ex:
        logger.critical(ex)
        print("Check logs.")

def init():

    global logger
    global applicationName
    global filePath
    global settings
    global skills
    global mqttClient

    try:

        skills = {}

        applicationName = "MQTT Server Manager"

        filePath = os.path.dirname(__file__) + "/"

        #Setup the logger, 10MB maximum log size
        logger = logging.getLogger(applicationName)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
        logHandler = handlers.RotatingFileHandler(filePath + 'events.log', maxBytes=10485760, backupCount=1)
        logHandler.setFormatter(formatter)
        logger.addHandler(logHandler)

        logger.info(applicationName + " application started.")

        #Create MQTT Client
        mqttClient = mqtt.Client()

        #Make sure the settings file exists
        if os.path.exists(filePath + 'settings.json') == False:
            raise Exception("Settings file does not exist.  Expected file " + filePath + 'settings.json')

        #Get the settings file
        if os.path.exists(filePath + 'settings.json.private') == True:
            with open(filePath + 'settings.json.private') as settingsFile:
                settings = json.load(settingsFile)
        else:   
            with open(filePath + 'settings.json') as settingsFile:
                settings = json.load(settingsFile)

        #Make sure the skills file exists
        if os.path.exists(filePath + 'skills.json') == False:
            raise Exception("Skills file does not exist.  Expected file " + filePath + 'skills.json')

        #Get the settings file
        with open(filePath + 'skills.json') as skillsFile:
            skills['defined'] = json.load(skillsFile)

        #Create the loaded skills attribute
        skills['loaded'] = []

    except Exception as ex:
        logger.critical(ex)
        print("Check logs.")
        quit()

def replaceMQTTTopicTokens(topic):

    topic = topic.lower()
    topic = topic.replace("%clienttopic%", settings["mqtt"]["clientTopic"])
    topic = topic.replace("%hostname%", socket.gethostname().split(".")[0].lower())

    return topic

def checkPackages(skillName, requiredPackages):
    for requiredPackage in requiredPackages:
        if module_exists(requiredPackage) == False:
            logger.critical(skillName + " requires package \"" + requiredPackage + "\", which is not installed.  The skill will not be loaded." )
            return False

    return True

def module_exists(module_name):
    return module_name in (name for loader, name, ispkg in iter_modules())

if __name__ == "__main__":

    #Get the application common variables
    init()

    #Setup the configuration required
    setup()

    #Start the application
    main()