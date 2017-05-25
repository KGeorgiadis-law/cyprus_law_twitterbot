# Cyprus Law Twitterbot

A bot to search cylaw.org (which posts decisions of the Cyprus Supreme Court) and post updates to twitter

The bot requests the ETag of cylaw.org/updates.html every 10 minutes. If the tag has changed, it reads the uppermost section of the website (where new decisions appear) and breaks that into tweets.


After compiling a tweet, it checks with an internal log whether that tweet has been sent before (to avoid duplicates). If that tweet is not found, it posts the tweet and saves its text in the log for future use.
