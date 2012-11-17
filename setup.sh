#!/bin/bash -e
set -e

PROJECT_ROOT="$( cd "$( dirname "$0" )" && pwd )"
cd $PROJECT_ROOT

# make LURKERFAQS_RUN_DIR
RUN_DIR=$PWD/run
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

# install apache, mysql
export DEBIAN_FRONTEND=noninteractive
apt-get -q -y install mysql-server
apt-get update -q
cat <<PACKAGES | xargs apt-get install -q -y
git-core

python
python-dev
python-setuptools

apache2
libapache2-mod-wsgi

default-jdk
solr-jetty
libxslt-dev

mysql-server
mysql-client
PACKAGES

# Install python libraries
easy_install pip
pip install MySQL-python        # mysql driver
pip install beautifulsoup4      # website scraping
pip install lxml                # sunburnt dependency
pip install sunburnt            # solr
pip install django              # web framework

#-- Configuration --#

# apache
cat <<HTTPDCONF > /etc/apache2/httpd.conf
WSGIScriptAlias / $PROJECT_ROOT/lurkerfaqs/wsgi.py
WSGIPythonPath $PROJECT_ROOT

<Directory $PROJECT_ROOT>
Order allow,deny
Allow from all
Options Indexes FollowSymLinks
</Directory>
HTTPDCONF

# cronjob
cat <<CRON > /etc/cron.daily/lurkerfaqs
#!/bin/sh
echo [`date`] 'Batch User Counts Starting' &> $BATCH_LOG
$PROJECT_ROOT/manage.py batch_user_counts &> $BATCH_LOG
echo [`date`] 'Batch User Counts Ended' &> $BATCH_LOG
CRON

cat <<CRON > /etc/cron.daily/lurkerfaqs
#!/bin/sh
echo [`date`] 'Batch Index Topics Starting' &> $BATCH_LOG
$PROJECT_ROOT/manage.py batch_index_topics &> $BATCH_LOG
echo [`date`] 'Batch Index Topics Ended' &> $BATCH_LOG
CRON

# solr
mv $PROJECT_ROOT/search/schema.xml /etc/solr/conf/schema.xml
cat <<JETTYCONF > /etc/default/jetty
NO_START=0
JETTY_HOST=127.0.0.1
JETTY_PORT=8983
JAVA_HOME=/usr/lib/jvm/default-java
JAVA_OPTIONS="-Xmx256m -Djava.awt.headless=true"
VERBOSE=yes
JETTYCONF

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
