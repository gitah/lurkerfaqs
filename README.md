Lurkerfaqs
==========
[LurkerFAQs](http://www.lurkerfaqs.com) is an archiver for the [GameFAQs message
boards](http://www.gamefaqs.com/boards).

It scrapes the GameFAQs message boards and stores topics and posts in a
database. There is a front end to access the archived material.

LurkerFAQs was originally written in PHP. This is a rewrite of LurkerFAQs using Python and Django.


Installation
============
To install and run LurkerFAQs, go to the project root directory and execute

    ./setup/setup.sh

NOTE: this script assumes that you are using Ubuntu 12.04 Server Edition

Change your MySQL database password via

    mysqladmin -uroot password <new_pass>

and then change the db password in settings.py to `<new_pass>`

Archiver
========
The archiver is a daemon that scrapes the GameFAQs message board. Message boards
to scrape is defined in `settings.py` in the following format:

    GFAQS_BOARDS = [
        (<board_alias>, <board_name>, <refresh_rate>),
        (<board_alias>, <board_name>, <refresh_rate>),
        ...
    ]
    <board_alias> => gamefaqs.com/boards/[.....]
    <board_name> => name of board to show on page
    <refresh_rate> => period in min. that the archiver checks the board

    ex:
    GFAQS_BOARDS = [
        ("8-gamefaqs-contests", "GameFAQs Contests", 5),
        ...
    ]

To start the archiver, run the command

    ./manage.py archvier start

The error/info log for the gfaqs archiver can be found at `run/archiver.log`

## Authentication
For boards that require authentication (ie. CE), you can set a user to login as
in `settings.py`

    GFAQS_LOGIN_AS_USER=True
    GFAQS_LOGIN_EMAIL=""
    GFAQS_LOGIN_PASSWORD=""


## GameFAQs Monitoring
The archiver scrapes GameFAQs and assumes a certain DOM structure for the site.
This makes it very brittle against minor changes to the DOM. There is a test to
detect when the structure changes and whether or not you can still login:

    ./manage.py test gfaqs.GFAQSDOMTest

There is a cron job setup to run this periodically. If you want to be notified
when the test fails fails via email, set the following setting variables:

    EMAIL_HOST = ''
    EMAIL_PORT = 25
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''


Search Server
=============
The search server is Solr contained in a Jetty server.

Documents are topics. There is a batch to index topics in the database to the
search server. Remember to restart the Jetty after indexing. By default there is
a cronjob to index unindexed topics every day.


Backups
=======
LurkerFAQs has the capibility of automatically backuping the database to AWS
S3/Glacier. This can be enabled by setting the following setting variables:

    ENABLE_S3_DB_BACKUP = False
    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''
    AWS_S3_BUCKET_NAME = ''
