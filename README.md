Lurkerfaqs
==========
LurkerFAQs is an archiver for the [GameFAQs message
boards](http://www.gamefaqs.com/boards)

It scrapes the GameFAQs message boards and stores topics and posts in a
database. There is a front end to access the archived material.

[LurkerFAQs was originally written in PHP](http://www.lurkerfaqs.com). This is a rewrite of LurkerFAQs using
Python and Django.


Installation
============
To install and run LurkerFAQs, go to the project root directory and execute

    ./setup.sh

NOTE: this script assumes that you are using Ubuntu 12.04 Server Edition

Change your MySQL database password via

    mysqladmin -uroot password <new_pass>

and then change the db password in settings.py to `<new_pass>`

Archiver
========
The archiver is a daemon that scrapes the GameFAQs message board. Message boards
to scrape is defined in `settings.py`

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

For boards that require authentication (ie. CE), you can set a user to login as
in `settings.py`

    GFAQS_LOGIN_AS_USER=True
    GFAQS_LOGIN_EMAIL=""
    GFAQS_LOGIN_PASSWORD=""

To start the archiver

    ./manage.py archvier start

The error/info log for the gfaqs archiver can be found at `run/archiver.log`
