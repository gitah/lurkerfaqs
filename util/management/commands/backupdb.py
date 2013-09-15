# -*- coding: utf-8 -*-
import os
import sys
import logging
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand

from util.s3backup import s3backup

S3_OBJECT_KEY = "lurkerfaqs_db_backup.sql.gz"
logger = logging.getLogger(settings.MISC_LOGGER)

class Command(BaseCommand):
    help = 'backs up the lurkerfaqs database to s3'

    def handle(self, *args, **options):
        logger.info("Starting db backup")

        if not settings.ENABLE_S3_DB_BACKUP:
            err_str = "Please configure S3_DB_BACKUP to enable back ups of database to AWS S3"
            print err_str
            logger.error(err_str)

        db = settings.DATABASES['default']
        db_name, db_user, db_password = db["NAME"], db['USER'], db['PASSWORD']

        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        s3bucket = settings.AWS_S3_BUCKET_NAME
        s3object = "%s-%s" % (date.today(), S3_OBJECT_KEY)

        try:
            s3backup(db_name, db_user, db_password, s3bucket, s3object,
                    aws_access_key_id, aws_secret_access_key)
            logger.info("Finished db backup")
        except:
            logger.error("S3 backup failed. Exception: %s" % str(e))
