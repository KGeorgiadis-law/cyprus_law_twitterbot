#!/usr/bin/python3
# coding: utf-8
# !Py3.5.2
#  CyprusLawTwitterBot_ver2.py
#  Mostly a learning exercise.
#  A bot to:
#  (a) check CyLaw once every five minutes for an update
#  (b) if it finds an update, take the title and a link to the document
#  (c) post these on twitter as an announcement.

# How does it do these things?
# (a) is done using an HTTP request to see whether something has changed
# (b) is done using BeautifulSoup4 to find the latest link added to the page
# (c) is done using the twitter API

# Where does the bot run?
# The bot runs on a Raspberry pi (Linux).

# dependencies
import tweepy # twitter API

from bs4 import BeautifulSoup # package for HTML Parsing

import requests # HTTP Requests package (used for quick requests)

from urllib.request import urlopen # used for GET HTTP requests

from time import sleep, gmtime, strftime

from functions.functions import *

from app import Etag, Tweet # import tables

# from credentials import * # log in information

from os import getenv

# initialise twitter API

def cyprusLawBot(db):

    # log in

    auth = tweepy.OAuthHandler(getenv('CONSUMER_KEY'), getenv('CONSUMER_SECRET'))
    auth.set_access_token(getenv('ACCESS_TOKEN'), getenv('ACCESS_SECRET'))
    api = tweepy.API(auth)

    # helper variables
    time_format = "%Y-%m-%d %H:%M:%S"

    # message creator that the bot is starting
    try:
        print("Messaging creator...")
        USERNAME = getenv('USERNAME')
        api.send_direct_message(USERNAME, USERNAME, USERNAME, "Bot Initialising at %s" % strftime(time_format, gmtime()))
    except tweepy.TweepError:
        print("Error messaging creator!")

    # start main function
    try:

        url = "http://www.cylaw.org/updates.html"

        print("Starting... ", strftime(time_format, gmtime()))

        # only request the headers to avoid making a whole GET request every time
        # for more info on ETags and why they're used here,
        # see https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag

        print("Requesting headers...")
        response = requests.head(url)
        headers = response.headers
        current_ETag = headers['ETag']

        # log the time of check and current ETag
    	# this log can be used down the line to check how much ETag changes and
	    ## if it is a good method.

        # get most recent Etag from the Etag database
        last_ETag = db.session.query(Etag).order_by(Etag.id.desc()).first()

        print("Comparing ETags...")
        print(current_ETag + " " + last_ETag)

        if current_ETag == last_ETag:
            print("No changes since last time! Sleeping now...\n\n")
            # exit program
            return ""
        
        print("change detected!")

        # update the ETag database with the new ETag
        db.session.add(Etag(etag=current_ETag))

        # change of ETag means that the page has been updated
	    # Open the site properly (with a GET request) using URLopen
        print("Requesting full HTML...")
        html = urlopen(url, timeout=30)

        # create a beautiful soup object from the HTML received
        print("Creating beautiful soup object...")
        soup = BeautifulSoup(html, "html.parser")

	    # Get the date of the latest update on cylaw.org/updates and
	    # get links to the latest cases.

        # Method to parse (analyse) HTML received
        # 1. Find `<div id='inner-content'>`
        # 2. Find 2nd `<h3>` tag (1st `<h3>` tag is the title card)
        # 3. Collect the date from that `<h3>` tag
        # 4. get the div after that tag
        # 5. get all `<a>` tags inside that tag

        print("Parsing HTML...")

        # step 1
        container = soup.find(id="inner-content")  # <div> with all contents
        
        # step 2
        title_card = container.h3  # the title card for the central <div>
        # the first announcement after the title card is the most recent one
        latest_announcement = title_card.find_next_sibling("h3")

	    # the date is consistently second in the list of contents for the latest announcement
        latest_announcement_date = latest_announcement.contents[1]
        # all new decisions are contained within <a> tags in the div after <h3>
        judgements_links = latest_announcement.find_next_sibling("div").findAll("a")
        link_prefix = "http://www.cylaw.org"

        if len(judgements_links) == 0:
            print("No judgements found! That's strange...")
    		##TODO: set hard limit on amount of judgements that can be posted.
            return ""

        # start drafting opening tweet
        print("Judgements found! Starting drafting process...")
        new_judgements_count = str(len(judgements_links))
        prefix = "νέας απόφασης" if new_judgements_count == 1 else "νέων αποφάσεων"

        # draft text for starting tweet
        starting_tweet = "{}: Δημοσίευση {} {} Ανωτάτου Κύπρου {}".format(latest_announcement_date, new_judgements_count, prefix, url)

		# count tweets posted. Tweet #0 is the starting tweet
        tweet_counter = 0

		# post starter tweet
        print("Posting Starter tweet...")
        first_tweet = post_tweet(tweet_counter, starting_tweet, api, tweet_counter, Tweet, db)

        if first_tweet != False or first_tweet == None:

            print("Success: tweet id: {}".format(first_tweet.id_str))

            # draft and send tweets
            for judgement in judgements_links:

                tweet_counter += 1

                judgement_title = judgement.text
                print(judgement_title)

                # check if the length exceeds standard tweet length
                # explanation of 108/105 char limit:
                # links (urls) are automatically shortened by twitter to 23 characters;
                # therefore, we can substract the length fo the link and add 23 to find the real
                # length of the tweet.
                # If it is more than 140 characters, the text is shortened to its first 105 characters
                #  (this is considering that link = 23 chars and counter/no announcements = up to 9 chars, since judgement number may be a 2-digit number)
                #  (140 - (23 + 7) = 108)
                # Finally, if a title is over 108 characters, we reduce it to 105 and add 3 fullstops

                if len(judgement_title) > 105:

                    print("Length larger than 140 characters so shortening length to first 105 chars")
                    judgement_title = judgement.text[:105]+"..."

                judgement_url = link_prefix + judgement.get('href')
                tweet_text = "[{}/{}] {} {}".format(str(tweet_counter), len(judgements_links), judgement_title, judgement_url)
                tweet = post_tweet(tweet_counter, tweet_text, api, first_tweet, Tweet, db)

                if tweet != False or tweet == None:
                    print("Success: tweet id: {}".format(tweet.id_str))

                sleep(5) # wait five seconds before posting a new tweet

            print("Finished! Sleeping now... \n\n")

    except Exception as ex:
        print(ex)
	# message creator that an error has appeared
        try:
            api.send_direct_message(USERNAME, USERNAME, USERNAME, "Error: {}".format(ex))
        except Exception as ex2:
            print(ex2)
        print("Error handled, sleeping again...")

    sleep(600)  # do this every 600 seconds (i.e. 5 mins)

if __name__ is '__main__':
    cyprusLawBot()
