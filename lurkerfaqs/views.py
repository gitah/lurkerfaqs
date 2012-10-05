from django.http import HttpResponse, HttpResponseServerError, HttpResponseNotFound, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.template import loader, RequestContext
from django.conf import settings
from django.db import connection, transaction

import gfaqs.models as models

"""
URL paths were designed to mimic the url paths on gamefaqs
"""

#TODO: add missing icons for topic status
TOPIC_STATUS_TO_IMG = {
    models.Topic.NORMAL: "topic_normal.gif",
    #models.Topic.CLOSED: "topic_closed.gif",
    models.Topic.ARCHIVED: "topic_archived.gif",
    #models.Topic.STICKY: "topic_sticky.gif",
    #models.Topic.STICKY_CLOSED: "topic_sticky_closed.gif",
    #models.Topic.PURGED: "topic_purged.gif",
    "default": "topic_normal.gif"
}

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
    except (PageNotAnInteger, EmptyPage):
        raise Http404
    return (paged_qs, paginator.count)

def get_page_from_request(req):
    """ returns the page parameter from the query string of the request
        NOTE:
            - actual page value is incremented by 1 since paginator is 1-indexed
            - 1 is returned if parameter does not exist or has a non-integer value
    """
    try:
        page = int(req.GET.get('page',1)) # paginator is 1-indexed
    except ValueError:
        page = 1
    return page

def build_context(request, **kwargs):
    """ returns a RequestContext for a template """
    kwargs["pages_to_display"] = range(1, settings.LURKERFAQS_PAGES_TO_DISPLAY+1)
    context = RequestContext(request, kwargs)
    return context

# -- Boards -- #
def show_boards(request):
    # /boards
    boards = models.Board.objects.all()
    t = loader.get_template('boards.html')
    c = RequestContext(request, {
        "boards": boards
    })
    return HttpResponse(t.render(c))

# -- Topics -- #
def show_board(request, board_alias):
    # /boards/<board_alias>?page=2
    try:
        board = models.Board.objects.get(alias=board_alias)
    except ObjectDoesNotExist:
        raise Http404

    qs = models.Topic.objects.filter(board=board)
    page = get_page_from_request(request)
    topics,total = get_qs_paged(qs, settings.LURKERFAQS_TOPICS_PER_PAGE, page)

    # map topic status to icons
    for tp in topics:
        tp.status_icon = TOPIC_STATUS_TO_IMG.get(tp.status,
            TOPIC_STATUS_TO_IMG["default"])

    t = loader.get_template('topics.html')
    c = build_context(request, board=board, topics=topics,
            total_topics=total, current_page=page)
    return HttpResponse(t.render(c))

# -- Posts -- #
def show_topic(request, board_alias, topic_num):
    # /boards/<board_alias>/<topic_num>?page=2
    #TODO: make a version that does not need board_alias
    try:
        board = models.Board.objects.get(alias=board_alias)
        topic = models.Topic.objects.get(gfaqs_id=topic_num)
    except ObjectDoesNotExist:
        raise Http404

    qs = models.Post.objects.filter(topic=topic)
    page = get_page_from_request(request)
    posts, total = get_qs_paged(qs, settings.LURKERFAQS_POSTS_PER_PAGE, page)

    t = loader.get_template('posts.html')
    c = build_context(request, board=topic.board, topic=topic,
            posts=posts, total_posts=total, current_page=page)
    return HttpResponse(t.render(c))

def search_topic(request, board_alias, query):
    cursor = connection.cursor()
    try:
        board = models.Board.objects.get(alias=board_alias)
    except ObjectDoesNotExist:
        raise Http404

    cursor.execute("SELECT * FROM gfaqs_topic WHERE board_id='%s' AND title LIKE '%s%", [board.id,query])
    desc = cursor.description
    topics = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

    t = loader.get_template('topic_search.html')
    c = build_context(request, topics=topics, boards=boards, query=query)
    return HttpResponse(t.render(c))

# -- Users -- #
def get_user(username):
    """ returns user with given username; raises Http404 if no user found"""
    try:
        user = models.User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404
    return user

def show_user(request, username):
    # /users/<username>
    user = get_user(username)

    topics_qs = models.Topic.objects.filter(creator=user)
    posts_qs = models.Post.objects.filter(creator=user)

    total_topics = len(topics_qs)
    total_posts = len(posts_qs)

    #TODO how to query active, even include it ???
    #active_topics = len(last_post_date)
    #total_topics = len(posts_qs.filter())

    t = loader.get_template('user_profile.html')
    c = build_context(request, user=user, total_topics=total_topics,
            total_posts=total_posts)
    return HttpResponse(t.render(c))

def show_user_topics(request, username):
    # /users/<username>/topics?page=2
    user = get_user(username)

    qs = models.Topic.objects.filter(creator=user)
    page = get_page_from_request(request)
    topics, total = get_qs_paged(qs, settings.LURKERFAQS_TOPICS_PER_PAGE, page)

    t = loader.get_template('user_topics.html')
    c = build_context(request, user=user, topics=topics,
        total_topics=total, current_page=page)
    return HttpResponse(t.render(c))

def show_user_posts(request, username):
    # /users/<username>/posts?page=2
    user = get_user(username)

    qs = models.Post.objects.filter(creator=user)
    page = get_page_from_request(request)
    posts, total = get_qs_paged(qs, settings.LURKERFAQS_TOPICS_PER_PAGE, page)

    t = loader.get_template('user_posts.html')
    c = build_context(request, user=user, posts=posts,
        total_topics=total, current_page=page)
    return HttpResponse(t.render(c))

def search_user(request, query):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM gfaqs_users WHERE username LIKE '\%s%", [query])
    desc = cursor.description
    users = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

    t = loader.get_template('user_search.html')
    c = RequestContext(request, {
        "users": users, "query": query
    })
    return HttpResponse(t.render(c))


# -- Misc -- #
def top_users(request):
    pass

def show_home(request):
    t = loader.get_template('home.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))
