from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('lurkerfaqs.views',
    url(r'^boards/$', 'show_boards'),
    url(r'^boards/(?P<board_alias>\w+)/$', 'show_board'),
    url(r'^boards/(?P<board_alias>\(?P<topic_num>\d+)/$', 'show_topic'),
)
