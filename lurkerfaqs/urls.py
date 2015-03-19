# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from lurkerfaqs import views, payment_views

#TODO: alias topic titles in URL for SEO improvements
# These map the URLs for the old lurkerfaqs site to the new urls
urlpatterns = patterns('',
    url(r'^$', views.show_home),
    url(r'^faq/$', views.show_faq),
    url(r'^top_users/$', views.top_users),

    url(r'^boards/$', views.show_boards),
    url(r'^boards/(?P<board_alias>[\w-]+)/$', views.show_board),
    url(r'^boards/(?P<board_alias>[\w-]+)/(?P<topic_num>\d+)/$', views.show_topic),

    url(r'^users/(?P<username>[\w+ -]+)$', views.show_user),
    url(r'^users/(?P<username>[\w+ -]+)/topics$', views.show_user_topics),
    url(r'^users/(?P<username>[\w+ -]+)/posts$', views.show_user_posts),

    url(r'^users/search/*$', views.search_user),
)

# Payment URLs
urlpatterns += patterns('',
    url(r'^payment/delete_post/(?P<gfaqs_topic_id>\d+)/(?P<post_num>\d+)/$', payment_views.create_payment_delete_post),
    url(r'^payment_confirmation/delete_post/(?P<gfaqs_topic_id>\d+)/(?P<post_num>\d+)/$', payment_views.confirm_payment_delete_post),
    #url(r'^payment_cancel/$', 'cancel_payment'),
)

urlpatterns += staticfiles_urlpatterns()
