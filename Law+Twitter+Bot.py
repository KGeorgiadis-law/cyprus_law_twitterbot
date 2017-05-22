
# coding: utf-8

# In[18]:

#!Py3.5.2
#  CyprusLawTwitterBot_ver2.py
#  Mostly a learning exercise.
#  A bot to:
##  (a) check CyLaw once an hour on weekdays for an update
##  (b) if it finds an update, take the title and a link to the document
##  (c) post these on twitter as an announcement.

## How does it do these things?
### (a) is done using an HTTP request to see whether something has changed
### (b) is done using BeautifulSoup4 to find the latest link added to the page
### (c) is done using the twitter API

## Where will the bot run?
### The plan is to have the tweeterbot run on my Amazon EC2 instance -
### but we'll see how that goes.


# In[94]:

#dependencies

import tweepy

from bs4 import BeautifulSoup

import requests

from credentials import *

from urllib.request import urlopen

from time import sleep




# In[29]:

while True:

    url = "http://www.cylaw.org/updates.html"


    # In[56]:

    # method 1: only request the headers to avoid making a whole GET request every time 
    response = requests.head(url)
    headers = response.headers


    # In[67]:

    conn = requests.get(url)


    # In[57]:

    # commented out to get this script to work wihtout using urlopen - to avoid importing two libraries

    '''
    conn = urlopen(url, timeout=30)
    headers = conn.headers
    '''
    #print(headers['ETag'])
    current_ETag = headers['ETag'] 
    # for more info on ETags and why they're used here, see https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag


    # In[71]:

    #next step: try to read last saved ETag - if file does not exist, create it
    try:
        ETag_file = open("last_ETag.txt", "r")
        last_ETag = ETag_file.read()
    except FileNotFoundError:
        ETag_file = open("last_ETag.txt", "w")
        last_ETag = None
    ETag_file.close()
    print(current_ETag+" "+last_ETag)

    if current_ETag != last_ETag: #change this to != for production environment
        
        print("change detected!")
        #update the ETag file with the new ETag
        ETag_file = open("last_ETag.txt", "w")
        ETag_file.write(current_ETag)
        
        # change of ETag means that the page has been updated. Open the site properly (with a GET request).
        # using URLopen
        html = urlopen(url, timeout=30)

        # In[72]:

        #create a beautiful soup object that we can then search through
        soup = BeautifulSoup(html, "html.parser")


        # Method::
        # 1. Find div id='inner-content' x
        # 2. Find 2nd `<h3>` tag (1st `<h3>` tag is the title card) x
        # 3. Collect the date from that h3 tag x
        # 4. get the div after that tag x
        # 5. get all `<a>` tags inside that tag x

        # In[74]:

        container = soup.find(id="inner-content") #<div> with all contents
        title_card = container.h3 #the title card for the central div

        #the first announcement after the title. 
        #it seems that this is going to be the most recent one
        latest_announcement = title_card.find_next_sibling("h3") 
        date = latest_announcement.contents[1] #second in the list of contents for the <h3> tag is consistently the date


        # In[101]:

        # all new decisions are contained within <a> tags
        # in the div after <h3>
        announcements = latest_announcement.find_next_sibling("div").findAll("a") 

        link_prefix = "http://www.cylaw.org"

        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)

        if len(announcements) > 0:
            #load a list of previous tweets to ensure no duplicates
            try:
                previous_tweets_file = open("previous_tweets.txt", "r")
                previous_tweets = previous_tweets_file.read().split("\n")
                previous_tweets_file.close()
            except FileNotFoundError:
                previous_tweets = None

            previous_tweets_file = open("previous_tweets.txt", "a")
            
            #start drafting a tweet
            tweet_list = []
            no_announcements = str(len(announcements))
            starting_tweet = (date+": Δημοσίευση "+no_announcements+" Νέων αποφάσεων στο http://www.cylaw.org/updates.html : ...")
            api.update_status(starting_tweet)
            print(starting_tweet)

            counter = 1

            for ann in announcements: #compile and send tweets
                text = ann.text
                link = link_prefix + ann.get('href')
                #tweet_end is to show there are other messages following as well 
                try:
                    tweet_text = "["+str(counter)+"/"+no_announcements+"]: "+text+" "+link
                    if tweet_text not in previous_tweets:
                        api.update_status(tweet_text)
                        previous_tweets_file.write(tweet_text+"\n")
                    else:
                        print("tweet already posted!")
                except TweepError: #only post the first 75 characters of the case if the script gets a twitter error
                    tweet_text = "["+str(counter)+"/"+no_announcements+"]: "+text[0:75]+" "+link 
                    api.update_status(tweet_text)
                    if tweet_text not in previous_tweets:
                        api.update_status(tweet_text)
                        previous_tweets_file.write(tweet_text+"\n")
                    else:
                        print("tweet already posted!")
                print(tweet_text)
                sleep(5)
                counter += 1
            previous_tweets_file.close()
        
        print("Finished! Sleeping now...")
    else:
        print("No changes since last time!")

    sleep(300) #do this every 300 seconds

