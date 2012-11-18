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
echo [\`date\`] 'Batch User Counts Starting' &> $BATCH_LOG
$PROJECT_ROOT/manage.py batch_user_counts &> $BATCH_LOG
echo [\`date\`] 'Batch User Counts Ended' &> $BATCH_LOG
CRON

# Topic indexing batch
LURKERFAQS_CRON_INDEX_TOPICS=/etc/cron.daily/lurkerfaqs_index_topics
touch $LURKERFAQS_CRON_INDEX_TOPICS
chmod 755 $LURKERFAQS_CRON_INDEX_TOPICS
cat <<CRON > $LURKERFAQS_CRON_INDEX_TOPICS
#!/bin/sh
echo [\`date\`] 'Batch Index Topics Starting' &> $BATCH_LOG
$PROJECT_ROOT/manage.py batch_index_topics &> $BATCH_LOG
service jetty restart &> $BATCH_LOG
echo [\`date\`] 'Batch Index Topics Ended' &> $BATCH_LOG
CRON

# GFAQs DOM monitoring
LURKERFAQS_CRON_MONITORING=/etc/cron.weekly/lurkerfaqs_monitoring
touch $LURKERFAQS_CRON_MONITORING
chmod 755 $LURKERFAQS_CRON_MONITORING
cat <<CRON > $LURKERFAQS_CRON_MONITORING
#!/bin/sh
echo [\`date\`] 'DOM tests started' &> $BATCH_LOG
$PROJECT_ROOT/manage.py test gfaqs.GFAQSDOMTest &> $BATCH_LOG
if [ $? -ne 0 ];
then
    echo [\`date\`] 'Test failed; sending email to admin' &> $BATCH_LOG
    $PROJECT_ROOT/manage.py alert_admin 'gfaqs dom test failed' 'failed' &> $BATCH_LOG
fi
echo [\`date\`] 'DOM tests ended' &> $BATCH_LOG
CRON
