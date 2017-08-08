# Functions for sending tweets, surprisingly enough.


def send_tweet(counter, tweet_text, starting_tweet=False):

    with open("previous_tweets.txt", "r", encoding='utf-8') as previous_tweets_file:
        previous_tweets_list = previous_tweets_file.readlines()

    previous_tweets_file = open("previous_tweets.txt", "a", encoding='utf-8')

    if tweet_text + "\n" not in previous_tweets_list:
        if starting_tweet:
            previous_tweets_file.write(tweet_text + "\n")
            try:
                first_tweet = api.update_status(starting_tweet)
                print("Posted: ", starting_tweet)
            except Exception as ex:
                # only post the first 75 characters of the case if the script gets a twitter error
                # tweet_text = "["+str(counter)+"/"+no_announcements+"]: "+text[0:75]+" "+link
                # api.update_status(tweet_text)
                print(ex)
                starting_status = starting_tweet = ""
                print("Error encountered! Skipping posting of this tweet...")
                print("For reference, tweet length was {} and its text was {}".format(len(starting_tweet),
                                                                                      starting_tweet))
        else:
            previous_tweets_file.write(tweet_text + "\n")
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
                api.update_status(tweet_text, first_tweet.id_str)
                print("Posting...")
                print(tweet_text)
                # previous_tweets_file.write()
            except:
                print("""Error encountered! Skipping posting of this tweet...\n
                For reference, tweet length was {} and its text was {}"""
                      .format(len(tweet_text), tweet_text))
    else:
        print("Duplicate tweet!\n{}".format(tweet_text))

    previous_tweets_file.close()