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
if [ -f $ARCHIVER_LOG ];
then
    touch $ARCHIVER_LOG
fi
chmod 777 $ARCHIVER_LOG

# install apache, mysql
export DEBIAN_FRONTEND=noninteractive
apt-get -q -y install mysql-server
apt-get update -q
cat <<PACKAGES | xargs apt-get install -q -y
git-core

python
python-mysqldb
python-setuptools

apache2
libapache2-mod-wsgi

mysql-server
mysql-client
PACKAGES

# Install beautifulsoup4 since ubuntu repo does not have newest version
easy_install beautifulsoup4

# Install django-1.4 since ubuntu repos only have django-1.3
python -c "import django"
if [ $? != 1 ];
then
    cd /tmp
    wget "http://www.djangoproject.com/download/1.4/tarball/" -O "django.tar.gz"
    tar xzvf "django.tar.gz"
    cd Django-1.4
    python setup.py install
    cd $PROJECT_ROOT
fi

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
if [ ! -f /etc/cron.d/lurkerfaqs ]; then
    cat <<CRON > /etc/cron.d/lurkerfaqs
0 0 * * 01 root python $PROJECT_ROOT/manage.py runbatch top_users
CRON
fi


#-- Services --#
service apache2 restart
service mysql restart

DBNAME=lurkerfaqs
set +e; mysqladmin -uroot "CREATE DATABASE $DBNAME CHARACTER SET utf8;" set -e
python manage.py syncdb
python manage.py archiver start


cat <<CONCLUSION
LurkerFAQs is now installed and running :)

To access it go to <ip>:<port>

Your database password is BLANK. Please change your database password and
update settings.py with the new one.
CONCLUSION
