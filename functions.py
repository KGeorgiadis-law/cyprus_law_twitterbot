# function to check tweets

def post_tweet(counter, tweet_text, api, reply_to):

    with open("previous_tweets.txt", "r", encoding='utf-8') as previous_tweets_file:
        previous_tweets_list = previous_tweets_file.readlines()

    previous_tweets_file = open("previous_tweets.txt", "a", encoding='utf-8')

    tweet_text_log = tweet_text + "\n"

    if tweet_text_log in previous_tweets_list:

        print("Duplicate tweet!\n{}".format(tweet_text))

    else:
        
        try:

            # if counter = 0, then this is the starting tweet
            if counter == 0:
                tweet = api.update_status(tweet_text)
                previous_tweets_file.write(tweet_text_log)
                return tweet

            # if counter != 0, then this is a secondary (judgement tweet), which is posted as a reply to the starting tweet
            else:
                tweet = api.update_status(tweet_text, reply_to.id_str)
                previous_tweets_file.write(tweet_text_log)
                return tweet
            
            print("Posted: {}".format(tweet_text))

        except Exception as ex:
            print(ex)
            print("Error encountered! Skipping posting of this tweet...")
            print("For reference, tweet length was {} and its text was {}".format(len(tweet_text), tweet_text))
            return False

        previous_tweets_file.close()
