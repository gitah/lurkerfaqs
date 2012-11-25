# -*- coding: utf-8 -*-
"""Backs up mysql database to AWS S3

PROTIP: set the lifecycle in the s3 bucket to glacier for savings
"""
import os
import subprocess
import tempfile

import boto

def s3backup(db, username, password,
        s3bucket, s3object, aws_access_key_id,
        aws_secret_access_key):
    sql_file = run_mysqldump(db, username, password)
    sql_file_gz = run_gzip(sql_file)
    upload_s3(sql_file_gz, s3bucket, s3object,
            aws_access_key_id, aws_secret_access_key)

def run_mysqldump(db, username, password=None):
    cmd = ['mysqldump', '-u%s' % username]
    if password:
        cmd.append('-p%s' % password)
    cmd.append(db)

    fd, sql_file = tempfile.mkstemp(prefix='s3backup-')
    with open(sql_file, 'w') as fp:
        subprocess.check_call(cmd, stdout=fp)
    return sql_file

def run_gzip(sql_file):
    cmd = ['gzip', sql_file]
    subprocess.check_call(cmd)
    return "%s.gz" % sql_file

def upload_s3(sql_file_gz, s3bucket, s3object,
        aws_access_key_id, aws_secret_access_key):
    conn = boto.connect_s3(aws_access_key_id, aws_secret_access_key)
    bucket = conn.get_bucket(s3bucket)
    k = boto.s3.key.Key(bucket)
    k.key = (s3object)
    k.set_contents_from_filename(sql_file_gz)

def cleaup(sql_file_gz):
    os.remove(sql_file_gz)
