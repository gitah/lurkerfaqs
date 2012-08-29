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

2. Write Scraper
    - investigate BeautifulSoup (OK)

    - posts scraper (WORK)
        - for each page pg in topic:
            - get pg
            - process pg wiht BeautifulSoup
            - for each post:
                - update db with post info

    - topics scraper (WORK)
        - until unchanged topic processed:
            - scrape page i
            - parse page i with BeautifulSoup
            - for each topic t:
                - update db with topic info
                - run posts scraper on topic t

    - write tests

3. Write ScraperController
    - configuration to define boards to scrape
        - board url
        - scrape period
        - automatically update Board model with boards

    - gfaqs authentication and cookie management
        - support multiple users?

    - write tests

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
