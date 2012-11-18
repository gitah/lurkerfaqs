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

<Directory $PROJECT_ROOT>
Order allow,deny
Allow from all
Options Indexes FollowSymLinks
</Directory>
HTTPDCONF
