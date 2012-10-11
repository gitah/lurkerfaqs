from django.http import HttpResponse, HttpResponseRedirect 
from django.http import HttpResponseServerError, HttpResponseNotFound, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from gfaqs.models import Board, Topic, Post, User
import lurkerfaqs.views


def top_users(request):
    new_url = reverse('lurkerfaqs.top_users')
    return HttpResponseRedirect(new_url) 

def show_faqs(request):
    new_url = reverse('lurkerfaqs.show_faqs')
    return HttpResponseRedirect(new_url) 

def show_board(request, board_id, page=None):
    try:
        board = Board.objects.get(pk=int(board_id))
    except ObjectDoesNotExist, ValueError:
        return Http404
    new_url = reverse('lurkerfaqs.show_board', board.alias)
    if page
        new_url = append_page(new_url, page)
    return HttpResponseRedirect(new_url) 

def show_topic(request, topic_id, page=None):
    try:
        topic = Topic.objects.get(pk=int(topic_id))
    except ObjectDoesNotExist, ValueError:
        return Http404
    new_url = reverse('lurkerfaqs.show_topic', topic.board.alias, topic.gfaqs_id)
    if page
        new_url = append_page(new_url, page)
    return HttpResponseRedirect(new_url) 

def show_user(request, user_id):
    try:
        user = Topic.objects.get(pk=int(user_id))
    except ObjectDoesNotExist, ValueError:
        return Http404
    new_url = reverse('lurkerfaqs.show_user', user.username)
    return HttpResponseRedirect(new_url) 

def show_user_topics(request, user_id, page=None):
    try:
        user = Topic.objects.get(pk=int(user_id))
    except ObjectDoesNotExist, ValueError:
        return Http404
    new_url = reverse('lurkerfaqs.show_user_topics', user.username)
    if page
        new_url = append_page(new_url, page)
    return HttpResponseRedirect(new_url) 

def show_user_topics(request, user_id, page=None):
    try:
        user = Topic.objects.get(pk=int(user_id))
    except ObjectDoesNotExist, ValueError:
        return Http404
    new_url = reverse('lurkerfaqs.show_user_posts', user.username)
    if page
        new_url = append_page(new_url, page)
    return HttpResponseRedirect(new_url) 

def append_page(url, page)
    return url += "?page=%s" % page
