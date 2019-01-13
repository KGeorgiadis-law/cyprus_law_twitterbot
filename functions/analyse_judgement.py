# #!/usr/bin/python3

# # coding: utf-8

# # !Py3.5.2
# #  Cyprus Law Twitter Bot
# #  Mostly a learning exercise.

# # analyse_judgement.py:
# # a function to extract the text of the judgement from the script, and generate a short tidbit to tweet as a reply
# # to the original tweet announcing the judgement

# # dependencies

# import tweepy

# from bs4 import BeautifulSoup

# import requests

# from credentials import *

# from urllib.request import urlopen

# from time import sleep, gmtime, strftime

# def analyse_judgement(url):
#     # the url is the url of the judgement

#     html = urlopen(url, timeout=30)

#     # create a beautiful soup object of the judgement text that we can then analyse
#     soup = BeautifulSoup(html, "html.parser")

#     # Thing to get:
#     # Find a short sentence that sums up the judgement. This is usually the second to last paragraph.
#     # If not successful, then don't produce anything

#     # Method::
#     # 1. Use BS to extract all text
#     # 2. Split text by newlines to have a list with all the paragraphs
#     # 3. Iterate through the list, searching for two newlines next to each other (indication of the judgement end)
#     # 4. Convert last paragraph to tweet, containing first n characters and the link (again)
#     # 5. Either post directly (from function) or return tweet to main script

#     judgement_full_text = soup.get_text()

#     print(judgement_full_text)

# ##    judgement_paragraphs = judgement_full_text.split("\n")
# ##    potential_paragraphs = list()
# ##    for i in range(len(judgement_paragraphs) -1):
# ##        # important paragraphs are usually followed by two empty lines. We can use that here
# ##        potential_paragraph = judgement_paragraphs[i - 2]
# ##        previous_line = judgement_paragraphs[i-1]
# ##        current_line = judgement_paragraphs[i]
# ##        # print("{}: Length: {}; Text :'{}'".format(i, len(judgement_paragraphs[i]), judgement_paragraphs[i]))
# ##        if len(previous_line) == 1 and len(current_line) == 1 and len(potential_paragraph) != 1:
# ##            #print("{}: '{}'".format(i, potential_paragraph))
# ##            potential_paragraphs.append(potential_paragraph)
# ##    print("'{}'".format(potential_paragraphs[1][:140]))


#     # twitter portion: reply to the status posted with a tidbit from the judgement
#     # posting a status returns a Status object, with the id_str variable which can be called by using
#     # Status.id_str ; this can be used to post a reply to a tweet.

#     auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
#     auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)


#     # api = tweepy.API(auth)

#     # status = api.update_status("test, please ignore")

#     # print(status)

#     # reply = api.update_status("reply test, please ignore", status.id_str)


# analyse_judgement("http://www.cylaw.org/cgi-bin/open.pl?file=/apofaseis/aad/meros_2/2017/2-201706-161-142.htm")

