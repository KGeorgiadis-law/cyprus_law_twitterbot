# Cyprus Law Twitterbot

A bot to search cylaw.org (which posts decisions of the Cyprus Supreme Court) and post updates to Twitter.

Created partly as a learning project and partly as an attempt to help legal professionals in Cyprus get instanteneous notifications of new decisions.

The bot requests the ETag from <a href='http://www.cylaw.org/updates.html'>CyLaw</a> every 5 minutes. If the tag has changed, it reads the uppermost section of the website (where new decisions appear). If it is new, it breaks the decisions into tweets and posts them one by one.

Link to the bot: https://twitter.com/cypruslawbot
