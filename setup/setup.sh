#!/bin/bash -e

# Installs lurkerfaqs dependencies and configurations
# Please run this in the project root directory
set -e

PROJECT_ROOT=$PWD

# make LURKERFAQS_RUN_DIR
RUN_DIR=$PROJECT_ROOT/run
if [ ! -d $RUN_DIR ];
then
    mkdir $RUN_DIR
    chmod 777 $RUN_DIR

fi

ARCHIVER_LOG=$RUN_DIR/archiver.log
if [ ! -f $ARCHIVER_LOG ];
then
    touch $ARCHIVER_LOG
fi
chmod 777 $ARCHIVER_LOG

BATCH_LOG=$RUN_DIR/batch.log
if [ ! -f $BATCH_LOG ];
then
    touch $BATCH_LOG
fi
chmod 777 $BATCH_LOG


$PROJECT_ROOT/setup/dependency_setup.sh
$PROJECT_ROOT/setup/configuration_setup.sh
$PROJECT_ROOT/setup/cron_setup.sh

#-- Services --#
service apache2 restart
service mysql restart
service jetty restart

DBNAME=lurkerfaqs
set +e
mysql -uroot -e "CREATE DATABASE $DBNAME CHARACTER SET utf8;"
set -e
python manage.py syncdb

cat <<CONCLUSION
LurkerFAQs is now installed and running :)

To access it go to <ip>:<port>

Your database password is BLANK. Please change your database password and
update settings.py with the new one.
CONCLUSION
