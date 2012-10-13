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
To install and run LurkerFAQs, go to the project root directory and
execute

    ./setup.sh

NOTE: this script assumes that you are using Ubuntu 12.04 Server Edition

Change your MySQL database password via

    mysqladmin -uroot password <new_pass>

and then change the db password in settings.py to `<new_pass>`
