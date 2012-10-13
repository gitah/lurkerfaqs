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

# install apache, mysql
export DEBIAN_FRONTEND=noninteractive
apt-get -q -y install mysql-server
apt-get update -q
cat <<PACKAGES | xargs apt-get install -q -y
git-core

python
python-django
python-mysqldb
python-bs4

apache2
libapache2-mod-wsgi

mysql-server
mysql-client
PACKAGES

#-- Configuration --#

# apache
cat <<HTTPDCONF > /etc/apache2/httpd.conf
WSGIScriptAlias / $PROJECT_ROOT/wsgi.py
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

set +e; mysqladmin -uroot create lurkerfaqs; set -e
python manage.py syncdb
python manage.py archiver start


cat <<CONCLUSION
LurkerFAQs is now installed and running :)

To access it go to <ip>:<port>

Your database password is BLANK. Please change your database password and
update settings.py with the new one.
CONCLUSION
