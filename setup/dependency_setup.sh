#!/bin/bash -e

# Installs lurkerfaqs dependencies
# Please run this in the project root directory
set -e
PROJECT_ROOT=$PWD
RUN_DIR=$PROJECT_ROOT/run
BATCH_LOG=$RUN_DIR/batch.log

# install apache, mysql
export DEBIAN_FRONTEND=noninteractive
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
libmysqlclient-dev
PACKAGES

# Install python libraries
easy_install pip
easy_install distribute
pip install MySQL-python        # mysql driver
pip install beautifulsoup4      # website scraping
pip install lxml                # sunburnt dependency
pip install sunburnt            # solr
pip install httplib2            # for sunburnt
pip install boto                # AWS api
pip install django              # web framework

# For Testing
pip install mock
pip install ipdb
