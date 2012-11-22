#!/bin/bash -e

# Installs configuration files for lurkerfaqs
# Please run this in the project root directory
set -e
PROJECT_ROOT=$PWD
RUN_DIR=$PROJECT_ROOT/run
BATCH_LOG=$RUN_DIR/batch.log

# apache
cat <<HTTPDCONF > /etc/apache2/httpd.conf
WSGIScriptAlias / $PROJECT_ROOT/lurkerfaqs/wsgi.py
WSGIPythonPath $PROJECT_ROOT

alias /static $PROJECT_ROOT/lurkerfaqs/static
alias /robots.txt $PROJECT_ROOT/lurkerfaqs/static/robots.txt
alias /favicon.ico $PROJECT_ROOT/lurkerfaqs/static/img/favicon.ico

<Directory $PROJECT_ROOT>
Order allow,deny
Allow from all
Options Indexes FollowSymLinks
</Directory>
HTTPDCONF

# solr
cp $PROJECT_ROOT/search/schema.xml /etc/solr/conf/schema.xml
cat <<JETTYCONF > /etc/default/jetty
NO_START=0
JETTY_HOST=127.0.0.1
JETTY_PORT=8983
JAVA_HOME=/usr/lib/jvm/default-java
JAVA_OPTIONS="-Xmx256m -Djava.awt.headless=true"
VERBOSE=yes
JETTYCONF
