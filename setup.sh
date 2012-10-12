#!/bin/bash
PROJECT_ROOT=`dirname $0`
cd $PROJECT_ROOT

# make LURKERFAQS_RUN_DIR
mkdir run
chmod 777 run

# install apache, mysql
cat <<PACKAGES | xargs apt-get install $APTITUDE_OPTIONS
git-core

python
python-django
python-beautifulsoup4

apache2
libapache2-mod-wsgi

mysql-server
mysql-client
PACKAGES

#-- Configuration --#

# httpd
cat > /etc/apache2/httpd.conf <<HTTPDCONF
WSGIScriptAlias / $PROJECT_ROOT/wsgi.py
WSGIPythonPath $PROJECT_ROOT

<Directory $PROJECT_ROOT>
Order allow,deny
Allow from all
Options Indexes FollowSymLinks
</Directory>
HTTPDCONF

# mysql

# run crons

cat <<CONCLUSION
LurkerFAQs is now installed and running :)

To access it go to <ip>:<port>

Your database password is $DB_PASSWORD. Please change your database password and
update settings.py with the new one.
CONCLUSION
