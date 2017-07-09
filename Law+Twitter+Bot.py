#!/usr/bin/python3

# coding: utf-8

# !Py3.5.2
#  CyprusLawTwitterBot_ver2.py
#  Mostly a learning exercise.
#  A bot to:
#  (a) check CyLaw once an hour on weekdays for an update
#  (b) if it finds an update, take the title and a link to the document
#  (c) post these on twitter as an announcement.

# How does it do these things?
# (a) is done using an HTTP request to see whether something has changed
# (b) is done using BeautifulSoup4 to find the latest link added to the page
# (c) is done using the twitter API

# Where will the bot run?
# The plan is to have the tweeterbot run on my Amazon EC2 instance -
# but we'll see how that goes.

# dependencies

import tweepy

from bs4 import BeautifulSoup

import requests

from credentials import *

from urllib.request import urlopen

from time import sleep, gmtime, strftime

while True:

    url = "http://www.cylaw.org/updates.html"

    print("Starting... ", strftime("%Y-%m-%d %H:%M:%S", gmtime()))

    # method 1: only request the headers to avoid making a whole GET request every time
    response = requests.head(url)
    headers = response.headers

    current_ETag = headers['ETag']
    # for more info on ETags and why they're used here,
    # see https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag

    # log the time of check
    with open("log.txt", "a") as log_file:
        log = strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " : " + current_ETag + "\n"
        log_file.write(log)

    # next step: try to read last saved ETag - if file does not exist, create it
    try:
        ETag_file = open("last_ETag.txt", "r")
        last_ETag = ETag_file.read()
    except FileNotFoundError:
        print("FileNotFoundError")
        ETag_file = open("last_ETag.txt", "w")
        last_ETag = ''
    ETag_file.close()
    print(current_ETag + " " + last_ETag)

    if current_ETag == last_ETag:  # change this to != for production environment

        print("change detected!")
        # update the ETag file with the new ETag
        ETag_file = open("last_ETag.txt", "w")
        ETag_file.write(current_ETag)
        ETag_file.close()

        # change of ETag means that the page has been updated. Open the site properly (with a GET request).
        # using URLopen
        html = urlopen(url, timeout=30)

        # create a beautiful soup object that we can then search through
        soup = BeautifulSoup(html, "html.parser")

        # Method::
        # 1. Find div id='inner-content' x
        # 2. Find 2nd `<h3>` tag (1st `<h3>` tag is the title card) x
        # 3. Collect the date from that h3 tag x
        # 4. get the div after that tag x
        # 5. get all `<a>` tags inside that tag x

        container = soup.find(id="inner-content")  # <div> with all contents
        title_card = container.h3  # the title card for the central div

        # the first announcement after the title.
        # it seems that this is going to be the most recent one
        latest_announcement = title_card.find_next_sibling("h3")
        date = latest_announcement.contents[1]
        # second in the list of contents for the <h3> tag is consistently the date

        # all new decisions are contained within <a> tags in the div after <h3>
        announcements = latest_announcement.find_next_sibling("div").findAll("a")

        link_prefix = "http://www.cylaw.org"

        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)

        if len(announcements) > 0:

            with open("previous_tweets.txt", "r", encoding='utf-8') as previous_tweets_file:
                previous_tweets_list = previous_tweets_file.readlines()

            previous_tweets_file = open("previous_tweets.txt", "a", encoding='utf-8')

            # start drafting a tweet

            no_announcements = str(len(announcements))
            starting_tweet = (
                date + ": Δημοσίευση " + no_announcements +
                " Νέων αποφάσεων στο http://www.cylaw.org/updates.html : ...")
            if starting_tweet + "\n" not in previous_tweets_list:
                previous_tweets_file.write(starting_tweet+"\n")
                try:
                    starting_status = api.update_status(starting_tweet)
                    print(starting_tweet)
                except:  # only post the first 75 characters of the case if the script gets a twitter error
                    # tweet_text = "["+str(counter)+"/"+no_announcements+"]: "+text[0:75]+" "+link
                    # api.update_status(tweet_text)
                    print("Error encountered! Skipping posting of this tweet...")
                    print("For reference, tweet length was {} and its text was {}".format(len(starting_tweet),
                                                                                          starting_tweet))
            else:
                print("Duplicate tweet!\n{}".format(starting_tweet))

            counter = 1

            for ann in announcements:  # compile and send tweets
                text = ann.text
                link = link_prefix + ann.get('href')
                tweet_text = "[" + str(counter) + "/" + no_announcements + "]: " + text + " " + link
                if tweet_text + "\n" not in previous_tweets_list:
                    previous_tweets_file.write(tweet_text+"\n")
                    try:
                        # check if the length exceeds standard tweet length
                        # explanation: links are shortened by twitter to always be 23 characters.
                        # therefore, we can substract the length fo the link and add 23 to find the real
                        # length of the tweet.
                        # If it is more than 140 characters, the text is shortened to its first 105 characters
                        #  (this is considering that link = 23 chars and counter/no announcements = 9 chars)
                        #  (140 - (23 + 9) = 108)
                        if len(tweet_text) - len(link) + 23 > 140:
                            print("Length larger than 140 characters so shortening length to first 105 chars")
                            tweet_text = "[" + str(counter) + "/" + no_announcements + "]: " + text[0:105] + "... " + link
                        api.update_status(tweet_text, starting_status.id_str)
                        print("Posting...")
                        print(tweet_text)
                        # previous_tweets_file.write()
                    except:
                        print("""Error encountered! Skipping posting of this tweet...\n
                        For reference, tweet length was {} and its text was {}"""
                              .format(len(tweet_text), tweet_text))
                else:
                    print("Duplicate tweet!")
                sleep(5)
                counter += 1
            previous_tweets_file.close()

        print("Finished! Sleeping now... \n\n")
    else:
        print("No changes since last time! Sleeping now...\n\n")

    sleep(600)  # do this every 600 seconds (5 mins)
