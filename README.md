Lurkerfaqs
==========
LurkerFAQs is an archiver for the [GameFAQs message
boards](http://www.gamefaqs.com/boards)

It scrapes the GameFAQs message boards and stores topics and posts in a
database. There is a front end to access the archived material.

[LurkerFAQs was originally written in PHP](http://www.lurkerfaqs.com). This is a rewrite of LurkerFAQs using
Python and Django.


TODO
====
##Scraper
1. Define Models (OK)
    - User
    - Topic
    - Post
    - Board

2. Write Scraper (OK)
    - investigate BeautifulSoup (OK)
    - posts scraper (OK)
    - topics scraper (OK)
    - write tests (OK)

3. Write Archiver (DONE)
    - configuration to define boards to scrape (OK)
    - write daemon (DONE)
    - write tests (DONE)

4. Misc (WORK)
    - gfaqs authentication and cookie management (DONE)
        - support multiple users?
    - logging (WORK)

##Front-End
1. Board List

2. Topic List

3. Post List

4. User Info
    - User Posts
    - User Topics

5. Search
    - Topic Search
    - User Search

6. Static
    - Front Page
        - updates system
    - FAQs     

7. Misc
    - logging 
    - google analytics
    - google ads

8. New Features
    - hot topics of the day/week
    - top users of the day/week
