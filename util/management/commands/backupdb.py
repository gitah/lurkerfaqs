# -*- coding: utf-8 -*-
import os
import sys
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand

from util import s3mysqldump

#TODO: set object archival to glacier

# http://<bucket>.s3.amazonaws.com/<key>
S3_URI_TEMPLATE = "s3://%s/%s"
S3_OBJECT_KEY = "lurkerfaqs_db_backup.sql"

class Command(BaseCommand):
    args = 'database table_name'
    help = 'Sends an email to the configured administrator'

    def handle(self, *args, **options):
        if not settings.ENABLE_S3_DB_BACKUP:
            print "Please configure S3_DB_BACKUP to enable back ups of database to AWS S3"

        # generate S3 URI to store the db backup
        s3_obj_name = "%s-%s" % (date.today(), S3_OBJECT_KEY)
        s3_uri = S3_URI_TEMPLATE % (settings.AWS_S3_BUCKET_NAME, s3_obj_name)

        # set environs for boto
        os.environ['AWS_ACCESS_KEY_ID'] = settings.AWS_ACCESS_KEY_ID
        os.environ['AWS_SECRET_ACCESS_KEY'] = settings.AWS_SECRET_ACCESS_KEY

        # run s3mysqldump script directly in python
        # ie. s3mysqldump -v -A <db_name> <s3://emr-storage/user.sql>
        db = settings.DATABASES['default']
        if db['PASSWORD']:
            mysqldump_args = '-u%s -p%s' % (db['USER'], db['PASSWORD'])
        else:
            mysqldump_args = '-u%s' % (db['USER'])

        script_args = ['-v', '-B']
        script_args.append("-M %s" % mysqldump_args)
        script_args.extend([db['NAME'], s3_uri])
        s3mysqldump.main(script_args)
