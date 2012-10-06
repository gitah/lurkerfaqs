from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns




#TODO: map old urls to new ones
#TODO: alias topic titles in URL for SEO improvements


urlpatterns = patterns('lurkerfaqs.views',
    url(r'^$', 'show_home'),
    url(r'^faq/$', 'show_faq'),

    url(r'^boards/$', 'show_boards'),
    url(r'^boards/(?P<board_alias>[\w-]+)/$', 'show_board'),
    url(r'^boards/(?P<board_alias>[\w-]+)/(?P<topic_num>\d+)/$', 'show_topic'),

    url(r'^users/(?P<username>[\w+ -]+)$', 'show_user'),
    url(r'^users/(?P<username>[\w+ -]+)/topics$', 'show_user_topics'),
    url(r'^users/(?P<username>[\w+ -]+)/posts$', 'show_user_posts'),

    url(r'^users/search/*$', 'search_user'),
)

urlpatterns += staticfiles_urlpatterns()
