#!/bin/bash -e
set -e

# Installs cron jobs for lurkerfaqs
# Please run this in the project root directory
PROJECT_ROOT=$PWD
RUN_DIR=$PROJECT_ROOT/run
BATCH_LOG=$RUN_DIR/batch.log

# User Count batch
LURKERFAQS_CRON_USER_COUNT=/etc/cron.daily/lurkerfaqs_user_count
touch $LURKERFAQS_CRON_USER_COUNT
chmod 755 $LURKERFAQS_CRON_USER_COUNT
cat <<CRON > $LURKERFAQS_CRON_USER_COUNT
#!/bin/sh
echo [\`date\`] 'Batch User Counts Starting' 1>> $BATCH_LOG 2>&1
$PROJECT_ROOT/manage.py batch_user_counts 1>> $BATCH_LOG 2>&1
echo [\`date\`] 'Batch User Counts Ended' 1>> $BATCH_LOG 2>&1
CRON

# Topic indexing batch
LURKERFAQS_CRON_INDEX_TOPICS=/etc/cron.daily/lurkerfaqs_index_topics
touch $LURKERFAQS_CRON_INDEX_TOPICS
chmod 755 $LURKERFAQS_CRON_INDEX_TOPICS
cat <<CRON > $LURKERFAQS_CRON_INDEX_TOPICS
#!/bin/sh
echo [\`date\`] 'Batch Index Topics Starting' 1>> $BATCH_LOG 2>&1
$PROJECT_ROOT/manage.py batch_index_topics update 1>> $BATCH_LOG 2>&1
service jetty restart 1>> $BATCH_LOG 2>&1
echo [\`date\`] 'Batch Index Topics Ended' 1>> $BATCH_LOG 2>&1
CRON

# GFAQs DOM monitoring
LURKERFAQS_CRON_MONITORING=/etc/cron.weekly/lurkerfaqs_monitoring
touch $LURKERFAQS_CRON_MONITORING
chmod 755 $LURKERFAQS_CRON_MONITORING
cat <<CRON > $LURKERFAQS_CRON_MONITORING
#!/bin/sh
echo [\`date\`] 'DOM tests started' 1>> $BATCH_LOG 2>&1
$PROJECT_ROOT/manage.py test gfaqs.GFAQSDOMTest 1>> $BATCH_LOG 2>&1
if [ $? -ne 0 ];
then
    echo [\`date\`] 'Test failed; sending email to admin' 1>> $BATCH_LOG 2>&1
    $PROJECT_ROOT/manage.py alert_admin 'gfaqs dom test failed' 'failed' 1>> $BATCH_LOG 2>&1
fi
echo [\`date\`] 'DOM tests ended' 1>> $BATCH_LOG 2>&1
CRON

# Database Backup
LURKERFAQS_CRON_BACKUPDB=/etc/cron.weekly/lurkerfaqs_backupdb
touch $LURKERFAQS_CRON_BACKUPDB
chmod 755 $LURKERFAQS_CRON_BACKUPDB
cat <<CRON > $LURKERFAQS_CRON_BACKUPDB
#!/bin/sh
echo [\`date\`] 'Backing up database!' 1>> $BATCH_LOG 2>&1
$PROJECT_ROOT/manage.py backupdb 1>> $BATCH_LOG 2>&1
echo [\`date\`] 'Backup database finished!' 1>> $BATCH_LOG 2>&1
CRON
