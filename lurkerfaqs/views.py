from django.http import HTTPResponse, HTTPResponseServerError, HTTPResponseNotFound, HTTP404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.template import loader, Context
from django.config import settings

import gfaqs.models as models

"""
URL paths were designed to mimic the url paths on gamefaqs
"""

# -- Utils -- #
def get_qs_paged(qs, window_size, page):
    """ page the qs to the given (page, window_size)
        NOTE:
            - page is 1-indexed
            - if page is invalid, qs will be executed with page=1

        returns (paged_qs, total_count)
    """
    paginator = Paginator(qs, window_size)
    try:
        paged_qs = paginator.page(page)
    except PageNotAnInteger, EmptyPage:
        paged_qs = paginator.page(1)
    return (paged_qs, paginator.count)

def get_page_from_request(req):
    """ returns the page parameter from the query string of the request
        NOTE:
            - actual page value is incremented by 1 since paginator is 1-indexed
            - 1 is returned if parameter does not exist or has a non-integer value
    """
    try:
        page = int(request.GET.get('page',0)) + 1 # paginator is 1-indexed
    except ValueError:
        page = 1
    return page

# -- Boards -- #
def show_boards(request):
    # /boards
    boards = models.Boards.objects.all()
    t = loader.get_template('lurkerfaqs/templates/boards.html')
    c = Context(boards = boards)
    return HTTPResponse(t.render(c))

# -- Topics -- #
def show_board(request, board_alias):
    # /boards/<board_alias>?page=2
    try:
        board = models.Board.objects.get(alias=board_alias)
    except ObjectDoesNotExist:
        raise HTTP404

    qs = models.Topic.objects.filter(board=board)
    page = get_page_from_request(request)
    topics, total = get_qs_paged(topics_qs,
            settings.LURKERFAQS_TOPICS_PER_PAGE, page)

    c = Context(board=board, topics=topics, total_topics=total)
    return HTTPResponse(t.render(c))

# -- Posts -- #
def show_topic(request, board_alias, topic_num):
    # /boards/<board_alias>/<topic_num>?page=2
    #TODO: make a version that does not need board_alias
    try:
        topic = models.Topics.get(gfaqs_id=topic_num)
    except ObjectDoesNotExist:
        raise HTTP404

    qs = models.Post.objects.filter(topic=topic)
    page = get_page_from_request(request)
    posts, total = get_qs_paged(qs, settings.LURKERFAQS_TOPICS_PER_PAGE, page)

    t = loader.get_template('lurkerfaqs/templates/posts.html')
    c = Context(board=topic.board, topic=topic, posts=posts)
    return HTTPResponse(t.render(c))

# -- Users -- #
def get_user(username):
    """ returns user with given username; raises HTTP404 if no user found"""
    try:
        user = models.User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise HTTP404
    return user

def show_user(request, username):
    # /users/<username>
    user = get_user(username)

    topics_qs = models.Topic.objects.filter(creator=creator)
    posts_qs = models.Post.objects.filter(creator=creator)

    total_topics = len(topics_qs)
    total_posts = len(posts_qs)

    #TODO how to query active
    #active_topics = len(last_post_date)
    #total_topics = len(posts_qs.filter())

    t = loader.get_template('lurkerfaqs/templates/user.html')
    c = Context(user=user, total_topics=total_topics, total_posts=total_posts)
    return HTTPResponse(t.render(c))

def show_user_topics(request):
    # /users/<username>/topics?page=2
    user = get_user(username)

    qs = models.Topic.objects.filter(creator=creator)
    page = get_page_from_request(request)
    posts, total = get_qs_paged(qs, settings.LURKERFAQS_TOPICS_PER_PAGE, page)

    t = loader.get_template('lurkerfaqs/templates/user_topics.html')
    c = Context(user=user, posts=posts, total_topics=total)
    return HTTPResponse(t.render(c))

def show_user_posts(request):
    # /users/<username>/posts?page=2
    user = get_user(username)

    qs = models.Post.objects.filter(creator=creator)
    page = get_page_from_request(request)
    posts, total = get_qs_paged(qs, settings.LURKERFAQS_TOPICS_PER_PAGE, page)

    t = loader.get_template('lurkerfaqs/templates/user_posts.html')
    c = Context(user=user, posts=posts, total_topics=total)
    return HTTPResponse(t.render(c))

def user_search(request):
    pass

# -- Misc -- #
def top_users(request):
    pass

# -- Something is wrong ----#
def not_found(request):
    return HTTPResponseNotFound()

def server_error(request):
    return HTTPResponseServerError()
