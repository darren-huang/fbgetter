# -*- coding: UTF-8 -*-

from fbchat import Client
from fbchat.models import *

def fetchUserName(userID):
    user = client.fetchUserInfo(str(userID))[str(userID)]
    return user.name

def cachedFM(func):
    d = {}
    def cachedF(oneArg):
        if oneArg in d:
            return d[oneArg]
        else:
            returnVal = func(oneArg)
            d[oneArg] = returnVal
            return returnVal
    return cachedF

fetchUserName = cachedFM(fetchUserName)

client = Client('zentoo2007@gmail.com', 'skipper')

# Fetches a list of all users you're currently chatting with, as `User` objects
users = client.fetchAllUsers()

print("users' IDs: {}".format(user.uid for user in users))
print("users' names: {}".format(user.name for user in users))


# If we have a user id, we can use `fetchUserInfo` to fetch a `User` object
steffi = client.fetchUserInfo('1255012174')['1255012174']  # FOUND USING "entity_ID"
# We can also query both mutiple users together, which returns list of `User` objects
# users = client.fetchUserInfo('<1st user id>', '<2nd user id>', '<3rd user id>')

print("user's name: {}".format(steffi.name))
# print("users' names: {}".format(users[k].name for k in users))


# `searchForUsers` searches for the user and gives us a list of the results,
# and then we just take the first one, aka. the most likely one:
steffi = client.searchForUsers('Steffi Kwok')[0]

print('user ID: {}'.format(steffi.uid))
print("user's name: {}".format(steffi.name))
print("user's photo: {}".format(steffi.photo))
print("Is user client's friend: {}".format(steffi.is_friend))


# Fetches a list of the 20 top threads you're currently chatting with
threads = client.fetchThreadList()
# Fetches the next 10 threads
threads += client.fetchThreadList(offset=20, limit=10)

watch = client.fetchThreadInfo(steffi.uid)

print("Threads: {}".format(threads))


# Gets the last 10 messages sent to the thread
messages = client.fetchThreadMessages(thread_id=steffi.uid)
# Since the message come in reversed order, reverse them
messages.reverse()

# Prints the content of all the messages
for message in messages:
    print(fetchUserName(message.author) + ": " + message.text)


# If we have a thread id, we can use `fetchThreadInfo` to fetch a `Thread` object
thread = client.fetchThreadInfo('<thread id>')['<thread id>']
print("thread's name: {}".format(thread.name))
print("thread's type: {}".format(thread.type))


# `searchForThreads` searches works like `searchForUsers`, but gives us a list of threads instead
thread = client.searchForThreads('<name of thread>')[0]
print("thread's name: {}".format(thread.name))
print("thread's type: {}".format(thread.type))


# Here should be an example of `getUnread`