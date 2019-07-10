# -*- coding: UTF-8 -*-

from fbchat import Client
from fbchat.models import *
import sys
import codecs
import time
import os
from FBMG.TimeConverter import epochToDate

# a function (later cached) to find the userNames

outputPath = "../ChatsArchive"
emailPath = "FBMG/email.txt"
passPath = "FBMG/password.txt"



def fetchUserName(client, userID):
    if userID is None:
        return "no Author???"
    user = client.fetchUserInfo(str(userID))[str(userID)]
    return user.name


def cachedFM(func):
    d = {}
    def cachedF(oneArg, twoArg):
        if (oneArg, twoArg) in d:
            return d[(oneArg, twoArg)]
        else:
            returnVal = func(oneArg, twoArg)
            d[(oneArg, twoArg)] = returnVal
            return returnVal
    return cachedF


def namePadder(name, targetLength):
    if len(name) < targetLength:
        return name + ((targetLength - len(name)) * " ")
    return name
fetchUserName = cachedFM(fetchUserName)
namePadder = cachedFM(namePadder)

def getAllMessages(name, filename, step, numSpaces=12):

    tz = "US/Pacific"

    #  the meat of the program:
    with open(emailPath, "r") as f:
        email = f.readline().replace("\n", "")
    with open(passPath, "r") as f:
        pWord = f.readline().replace("\n", "")
    client = Client(email, pWord)

    user = client.searchForUsers(name)[0]  # this is for searching for a name
    # user = client.fetchUserInfo(str(userID))[str(userID)]  # FOUND USING "entity_ID"

    msgStrings = []
    try:
        with codecs.open(os.path.join(outputPath,filename), "x", "utf-8") as f:
            # Gets the last 10 messages sent to the thread
            before = int(round(time.time() * 1000))  # current time in milliseconds

            numMsgs = 0
            lastName = None
            messages = client.fetchThreadMessages(thread_id=user.uid, limit=step, before=before)
            # for _ in range(2):
            while (messages):
                ts = messages[-1].timestamp

                # stores the content of all the messages
                for message in messages:
                    currName = namePadder(fetchUserName(client, message.author), numSpaces)
                    sp = " " * numSpaces

                    # places name tag on previous message after new message has a namechange
                    # (NOTE: a bit backwards because we are reading the messages soonest to last)
                    beginner = sp + ": "
                    if currName != lastName:
                        if msgStrings:
                            msgStrings[-1] = "\n" + msgStrings[-1].replace(sp + ": ", lastName + ": ")
                        lastName = currName

                    beginner = epochToDate(int(message.timestamp) // 1000, tz) + " : "  + beginner # /1000 is to convert to seconds

                    if message.text:
                        msgStrings.append(beginner + message.text)
                    elif message.sticker:
                        # print(message.sticker)
                        msgStrings.append(beginner + "STICKER : \n"  + message.sticker.url)
                before = int(ts) - 1

                numMsgs += len(messages)
                print(numMsgs)

                messages = client.fetchThreadMessages(thread_id=user.uid, limit=step, before=before)

            # adds the final name tag
            msgStrings[-1] = msgStrings[-1].replace(sp + ": ", lastName + ": ")


            # writes the contents backwards
            for i in range(len(msgStrings) - 1, -1, -1):  # message reversing in the range
                msgString = msgStrings[i]
                f.write(msgString + "\n")
    except FileExistsError as e:
        print("File already exists, please delete " + filename + " in order to continue")

name = "Annie Tang"
filename = "annieTangAllChat"
num = 0
while os.path.exists(os.path.join(outputPath, (filename + str(num) + ".txt"))):
    num += 1
filename = filename + str(num) + ".txt"
getAllMessages(name, filename, 5000, numSpaces=16)