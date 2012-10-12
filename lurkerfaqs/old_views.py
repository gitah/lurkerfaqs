from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseServerError, HttpResponseNotFound, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from gfaqs.models import Board, Topic, Post, User
import lurkerfaqs.views


def top_users(request):
    new_url = reverse('lurkerfaqs.views.top_users')
    return HttpResponseRedirect(new_url)

def show_faq(request):
    new_url = reverse('lurkerfaqs.views.show_faq')
    return HttpResponseRedirect(new_url)

def show_board(request, board_id, page=None):
    try:
        board = Board.objects.get(pk=int(board_id))
    except ObjectDoesNotExist, ValueError:
        raise Http404
    new_url = reverse('lurkerfaqs.views.show_board', args=[board.alias])
    if page:
        new_url = append_page(new_url, page)
    return HttpResponseRedirect(new_url)

def show_topic(request, topic_id, page=None):
    try:
        topic = Topic.objects.get(pk=int(topic_id))
    except ObjectDoesNotExist, ValueError:
        raise Http404
    new_url = reverse('lurkerfaqs.views.show_topic',
        args=[topic.board.alias, topic.gfaqs_id])
    if page:
        new_url = append_page(new_url, page)
    return HttpResponseRedirect(new_url)

def show_user(request, user_id):
    try:
        user = User.objects.get(pk=int(user_id))
    except ObjectDoesNotExist, ValueError:
        raise Http404
    new_url = reverse('lurkerfaqs.views.show_user', args=[user.username])
    return HttpResponseRedirect(new_url)

def show_user_topics(request, user_id, page=None):
    try:
        user = User.objects.get(pk=int(user_id))
    except ObjectDoesNotExist, ValueError:
        raise Http404
    new_url = reverse('lurkerfaqs.views.show_user_topics', args=[user.username])
    if page:
        new_url = append_page(new_url, page)
    return HttpResponseRedirect(new_url)

def show_user_posts(request, user_id, page=None):
    try:
        user = User.objects.get(pk=int(user_id))
    except ObjectDoesNotExist, ValueError:
        raise Http404
    new_url = reverse('lurkerfaqs.views.show_user_posts', args=[user.username])
    if page:
        new_url = append_page(new_url, page)
    return HttpResponseRedirect(new_url)

def append_page(url, page):
    return "%s?page=%s" % (url,page)
