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

from sending_tweets import send_tweet

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

api.send_direct_message(USERNAME, USERNAME, USERNAME, "Bot Initialising...")

while True:

    try:

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


            if len(announcements) > 0:


                # start drafting a tweet

                no_announcements = str(len(announcements))
                starting_tweet = (
                    date + ": Δημοσίευση " + no_announcements +
                    " Νέων αποφάσεων Ανωτάτου Κύπρου http://www.cylaw.org/updates.html")

                send_tweet(starting_tweet)

                counter = 1

                for ann in announcements:  # compile and send tweets
                    text = ann.text
                    link = link_prefix + ann.get('href')
                    tweet_text = "[" + str(counter) + "/" + no_announcements + "] " + text + " " + link

                    sleep(5)
                    counter += 1

            print("Finished! Sleeping now... \n\n")
        else:
            print("No changes since last time! Sleeping now...\n\n")

    except Exception as ex:
        print(ex)
        api.send_direct_message(USERNAME, USERNAME, USERNAME, "Error: {}".format(ex))
        print("Error handled, sleeping again...")
    sleep(600)  # do this every 600 seconds (5 mins)
