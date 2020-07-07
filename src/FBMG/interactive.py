import getpass
import os
import codecs
import time
import fbchat
from fbchat.models import ImageAttachment
from fbchat import Client, FBchatException, Group, User
from os.path import dirname, realpath, exists

from FBMG.TimeConverter import epochToDate

outputPath = "./ChatsArchive"
emailPath = os.path.join(dirname(realpath(__file__)), "email.txt")
passPath = os.path.join(dirname(realpath(__file__)), "password.txt")

input3 = input
tz = "US/Pacific"

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

def get_client():
    email = ""
    if exists(emailPath):
        with open(emailPath, "r") as f:
            email = f.readline().replace("\n", "")
    if not email:
        email = input("email: ")

    password = ""
    if exists(passPath):
        with open(passPath, "r") as f:
            password = f.readline().replace("\n", "")
    if not password:
        password = getpass.getpass()

    client = Client(email, password)
    input = input3
    return client

def user_str(user):
    return f"{user.name}, is_friend: {user.is_friend}, {user.url}"

def get_msg_attachment_urls(client, msg):
    try:
        return "\n".join([client.fetchImageUrl(image_attach.uid) for image_attach in msg.attachments])
    except fbchat.FBchatFacebookError as e:
        print("ERROR: ", e)
        print(msg)
        return ""


def determine_chat_thread(client):
    while True:
        # get group or user
        choice = ""
        while choice not in ["g", "u", "group", "user"]:
            choice = input3("\ngroup chat (g) or user chat (u): ")

        # search for a specific name
        searchQuery = input("search group/user: ")
        if choice in ["g", "group"]:
            results = client.searchForGroups(searchQuery)
            print("\ngroups:")
            for c, group in enumerate(results, 0):
                print(c, ": ", group)
        else:
            results = client.searchForUsers(searchQuery)
            print("\nusers:")
            for c, user in enumerate(results, 0):
                print(c, ": ", user_str(user))

        # select group/user or retry
        choice = ""
        while choice not in ["r", "retry"] + [str(i) for i in range(len(results))]:
            choice = input("retry (r) or select number: ")
        if choice.isnumeric():
            return results[int(choice)]


def get_all_msg_strs(client, thread):
    step = 5000
    msgStrings = []

    # find max length of names in the chat
    if type(thread) == Group: # group chat
        numSpaces = max([len(user.name) for user in client.fetchAllUsersFromThreads([thread])])
    else: #User chat
        numSpaces = max([len(user.name) for user in [thread, client.fetchUserInfo(client.uid)[client.uid]]])

    before_in = input("before epoch? (leave empty if not):")
    if before_in == "":
        before = int(round(time.time() * 1000))  # current time in milliseconds
    else:
        before = int(before_in)

    numMsgs = 0
    lastName = None
    messages = client.fetchThreadMessages(thread_id=thread.uid, limit=step, before=before)
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

            beginner = epochToDate(int(message.timestamp) // 1000,
                                   tz) + " : " + beginner  # /1000 is to convert to seconds
            ender = ""
            if message.text:
                ender += message.text
            if message.sticker:
                # print(message.sticker)
                ender += "STICKER : \n" + message.sticker.url
            if message.attachments and type(message.attachments[0]) == ImageAttachment:
                ender += "ATTACHEMENT : \n" + get_msg_attachment_urls(client, message)
            if ender:
                msgStrings.append(beginner + ender)
            else:
                print(message)

        before = int(ts) - 1

        numMsgs += len(messages)
        print(numMsgs)

        try:
            time.sleep(1)
            messages = client.fetchThreadMessages(thread_id=thread.uid, limit=step, before=before)
        except FBchatException:
            messages = None
            print("\n\n\n\nFAILED TO GET MESSAGES???\n\nbefore: {}\n\n\n".format(before))
            msgStrings.append("\n before: {}\n".format(before))
            

    # adds the final name tag
    msgStrings[-1] = msgStrings[-1].replace(sp + ": ", lastName + ": ")

    msgStrings.reverse()
    return msgStrings


def write_msgs(outputPath, filename, msgStrings):
    try:
        with codecs.open(os.path.join(outputPath, filename), "x", "utf-8") as f:
            # writes the contents backwards
            for s in msgStrings:
                f.write(s + "\n")
    except FileExistsError as e:
        print("File already exists, please delete " + filename + " in order to continue")

def interactive_write_msgs(msgStrings):
    filename = input("filename: ")
    num = 0
    while os.path.exists(os.path.join(outputPath, (filename + str(num) + ".txt"))):
        num += 1
    filename = filename + str(num) + ".txt"
    write_msgs(outputPath, filename, msgStrings)

def main():
    client = get_client()
    thread = determine_chat_thread(client)
    msgs = get_all_msg_strs(client, thread)
    # print("\n".join(msgs[:15]))
    interactive_write_msgs(msgs)

if __name__ == '__main__':
    main()
