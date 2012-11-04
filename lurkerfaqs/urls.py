# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

#TODO: alias topic titles in URL for SEO improvements
urlpatterns = patterns('lurkerfaqs.views',
    url(r'^$', 'show_home'),
    url(r'^faq/$', 'show_faq'),
    url(r'^top_users/$', 'top_users'),

    url(r'^boards/$', 'show_boards'),
    url(r'^boards/(?P<board_alias>[\w-]+)/$', 'show_board'),
    url(r'^boards/(?P<board_alias>[\w-]+)/(?P<topic_num>\d+)/$', 'show_topic'),

    url(r'^users/(?P<username>[\w+ -]+)$', 'show_user'),
    url(r'^users/(?P<username>[\w+ -]+)/topics$', 'show_user_topics'),
    url(r'^users/(?P<username>[\w+ -]+)/posts$', 'show_user_posts'),

    url(r'^users/search/*$', 'search_user'),
)

# These map the URLs for the old lurkerfaqs site to the new urls
urlpatterns += patterns('lurkerfaqs.old_views',
    url(r'^users/topUsers/$', 'top_users'),
    url(r'^pages/faq/$', 'show_faq'),

    url(r'topics/view/(?P<board_id>\d+)(/page:(?P<page>\d+))?/$', 'show_board'),
    url(r'posts/view/(?P<topic_id>\d+)(/page:(?P<page>\d+))?/$', 'show_topic'),

    url(r'users/view/(?P<user_id>\d+)', 'show_user'),
    url(r'topics/viewUserTopics/(?P<user_id>\d+)(/page:(?P<page>\d+))?/$', 'show_user_topics'),
    url(r'posts/viewUserPosts/(?P<user_id>\d+)(/page:(?P<page>\d+))?/$', 'show_user_posts'),
)

urlpatterns += staticfiles_urlpatterns()
