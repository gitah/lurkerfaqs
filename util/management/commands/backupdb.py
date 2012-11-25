# -*- coding: utf-8 -*-
import os
import sys
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand

from util.s3backup import s3backup

S3_OBJECT_KEY = "lurkerfaqs_db_backup.sql.gz"

class Command(BaseCommand):
    help = 'backs up the lurkerfaqs database to s3'

    def handle(self, *args, **options):
        if not settings.ENABLE_S3_DB_BACKUP:
            print "Please configure S3_DB_BACKUP to enable back ups of database to AWS S3"

        db = settings.DATABASES['default']
        db_name, db_user, db_password = db["NAME"], db['USER'], db['PASSWORD']

        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        s3bucket = settings.AWS_S3_BUCKET_NAME
        s3object = "%s-%s" % (date.today(), S3_OBJECT_KEY)

        s3backup(db_name, db_user, db_password, s3bucket, s3object,
                aws_access_key_id, aws_secret_access_key)
