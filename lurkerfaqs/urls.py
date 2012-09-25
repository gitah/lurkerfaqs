from django.conf.urls import patterns, include, url

#TODO: map old urls to new ones
#TODO: alias topic titles in URL for SEO improvements

urlpatterns = patterns('lurkerfaqs.views',
    url(r'^boards/$', 'show_boards'),
    url(r'^boards/(?P<board_alias>\w+)/$', 'show_board'),
    url(r'^boards/(?P<board_alias>\(?P<topic_num>\d+)/$', 'show_topic'),

    url(r'^users/(?P<username>', 'show_user'),
    url(r'^users/(?P<username>/topics', 'show_user_topics')
    url(r'^users/(?P<username>/posts', 'show_user_posts'),
)
