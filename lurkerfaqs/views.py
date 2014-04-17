# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseServerError, HttpResponseNotFound, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.template import loader, RequestContext
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.db import connection, transaction

from batch.models import UserTopicCount, UserPostCount
from gfaqs.models import Board, User, Topic, Post
from search.solr import SolrSearcher
from util.linkify import linkify

""" NOTE: URL paths were designed to mimic the url paths on gamefaqs """

TOPIC_STATUS_TO_IMG = {
    Topic.NORMAL: "topic_normal.gif",
    Topic.CLOSED: "topic_closed.gif",
    Topic.ARCHIVED: "topic_archived.gif",
    Topic.STICKY: "sticky.gif",
    Topic.STICKY_CLOSED: "sticky_closed.gif",
    Topic.PURGED: "topic_closed.gif",
    Topic.POLL: "topic_poll.gif",
    "default": "topic_normal.gif"
}

# -- Utils -- #
def get_qs_paged(request, qs, window_size):
    """ page the qs to the given (page, window_size)
        NOTE:
            - page is 1-indexed
            - if page is invalid, qs will be executed with page=1

        returns (paged_qs, current_page, page_guide)
    """
    page = get_page_from_request(request)
    paginator = Paginator(qs, window_size)
    try:
        paged_qs = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        raise Http404

    num_pages = paginator.num_pages
    pages_to_display = settings.LURKERFAQS_PAGES_TO_DISPLAY

    page_guide = create_page_guide(paginator.num_pages,
        settings.LURKERFAQS_PAGES_TO_DISPLAY, page)

    return (paged_qs, page, page_guide)

def create_page_guide(total_pages, pages_to_display, curr_page):
    """ returns a list that the template will use to create the pagination bar """
    def insert_division(lst):
        new_lst = []
        for el in lst:
            new_lst.append(el)
            new_lst.append("|")
        new_lst.pop()
        return new_lst

    page_guide = []
    if total_pages == 1:
        return []
    elif total_pages <= pages_to_display:
        page_guide = insert_division(range(1,total_pages+1))
    elif curr_page < pages_to_display:
       #1 2 **3** 4 5...
       page_guide = insert_division(range(1, pages_to_display+1))
       page_guide.append("...")
    else:
       page_guide.append(1)
       page_guide.append("...")
       m = pages_to_display/2
       beg = max(curr_page - m, 1)
       end = min(curr_page+m, total_pages)
       page_guide += insert_division(range(beg, end+1))
       if end < total_pages:
           page_guide.append("...")

    return page_guide

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
    context = RequestContext(request, kwargs)
    return context

def load_status_icon(topic):
    # map topic status to icons
    topic.status_icon = TOPIC_STATUS_TO_IMG.get(int(topic.status), TOPIC_STATUS_TO_IMG["default"])

# -- Boards -- #
@cache_page(settings.CACHE_STORAGE_TIME)
def show_boards(request):
    # /boards
    boards = Board.objects.all().order_by('name')

    t = loader.get_template('boards.html')
    c = RequestContext(request, {
        "boards": boards
    })
    return HttpResponse(t.render(c))

# -- Topics -- #
@cache_page(settings.CACHE_STORAGE_TIME)
def show_board(request, board_alias):
    # /boards/<board_alias>?page=2
    if request.GET.get("search"):
        return search_topic(request, board_alias, request.GET.get("search"))

    try:
        board = Board.objects.get(alias=board_alias)
    except ObjectDoesNotExist:
        raise Http404

    qs = Topic.objects.filter(board=board).order_by('-last_post_date')
    topics, current_page, page_guide = get_qs_paged(
        request, qs, settings.LURKERFAQS_TOPICS_PER_PAGE)

    for tp in topics:
        load_status_icon(tp)

    t = loader.get_template('topics.html')
    c = build_context(request, board=board, topics=topics,
            current_page=current_page, page_guide=page_guide)
    return HttpResponse(t.render(c))

# -- Posts -- #
@cache_page(settings.CACHE_STORAGE_TIME)
def show_topic(request, board_alias, topic_num):
    # /boards/<board_alias>/<topic_num>?page=2
    try:
        board = Board.objects.get(alias=board_alias)
        topic = Topic.objects.get(gfaqs_id=topic_num)
    except ObjectDoesNotExist:
        raise Http404

    qs = Post.objects.filter(topic=topic).order_by('date')
    posts, current_page, page_guide = get_qs_paged(
        request, qs, settings.LURKERFAQS_POSTS_PER_PAGE)

    if not posts:
        t = loader.get_template('posts_none.html')
        c = build_context(request, topic=topic, board=topic.board)
        return HttpResponse(t.render(c))

    for post in posts:
        post.contents = linkify(post.contents)
    op_post = posts[0]
    posts = posts[1:]

    # get related topics to this one
    related_topics_gids = SolrSearcher.search_related_topics(
            topic, settings.LURKERFAQS_RELATED_TOPICS_COUNT)
    related_topics = list(
        Topic.objects.filter(gfaqs_id__in=related_topics_gids)
    )
    for tp in related_topics:
        load_status_icon(tp)

    t = loader.get_template('posts.html')
    c = build_context(request, board=topic.board, topic=topic,
            posts=posts, op_post=op_post, related_topics=related_topics,
            current_page=current_page, page_guide=page_guide)
    return HttpResponse(t.render(c))

@cache_page(settings.CACHE_STORAGE_TIME)
def search_topic(request, board_alias, query):
    cursor = connection.cursor()
    try:
        board = Board.objects.get(alias=board_alias)
    except ObjectDoesNotExist:
        raise Http404

    page  = get_page_from_request(request)
    start = (page-1) * settings.LURKERFAQS_TOPICS_PER_PAGE
    count = settings.LURKERFAQS_TOPICS_PER_PAGE

    # topic ids should be date descending ordered
    total_results, topic_gfaqs_ids = SolrSearcher.search_topic(query, board_alias, start, count)
    topics_unordered = list(Topic.objects.filter(gfaqs_id__in=topic_gfaqs_ids))

    # reorder topics
    topics = []
    for gid in topic_gfaqs_ids:
        for t in topics_unordered:
            if t.gfaqs_id == gid:
                topics.append(t)
                break

    # create a page guide for pagination
    topics_per_page = settings.LURKERFAQS_PAGES_TO_DISPLAY
    page_guide = create_page_guide(total_results/count + 1,
            settings.LURKERFAQS_PAGES_TO_DISPLAY, page)

    t = loader.get_template('topic_search.html')
    c = build_context(request, topics=topics, board=board, query=query,
        current_page=page, page_guide=page_guide)
    return HttpResponse(t.render(c))

# -- Users -- #
def get_user(username):
    """ returns user with given username; raises Http404 if no user found"""
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404
    return user

@cache_page(settings.CACHE_STORAGE_TIME)
def show_user(request, username):
    # /users/<username>
    user = get_user(username)
    try:
        total_topics = UserTopicCount.objects.get(username=user.username).count
    except ObjectDoesNotExist:
        total_topics = 0
    try:
        total_posts = UserPostCount.objects.get(username=user.username).count
    except ObjectDoesNotExist:
        total_posts = 0

    t = loader.get_template('user_profile.html')
    c = build_context(request, user=user,
        total_topics=total_topics, total_posts=total_posts)
    return HttpResponse(t.render(c))

@cache_page(settings.CACHE_STORAGE_TIME_LONG)
def show_user_topics(request, username):
    # /users/<username>/topics?page=2
    user = get_user(username)

    qs = Topic.objects.filter(creator=user).order_by('-last_post_date')
    topics, current_page, page_guide = get_qs_paged(
        request, qs, settings.LURKERFAQS_POSTS_PER_PAGE)

    t = loader.get_template('user_topics.html')
    c = build_context(request, user=user, topics=topics,
        current_page=current_page, page_guide=page_guide)
    return HttpResponse(t.render(c))

@cache_page(settings.CACHE_STORAGE_TIME_LONG)
def show_user_posts(request, username):
    # /users/<username>/posts?page=2
    user = get_user(username)

    qs = Post.objects.filter(creator=user).order_by('-date')
    posts, current_page, page_guide = get_qs_paged(
        request, qs, settings.LURKERFAQS_POSTS_PER_PAGE)

    for post in posts:
        post.contents = linkify(post.contents)

    t = loader.get_template('user_posts.html')
    c = build_context(request, user=user, posts=posts,
        current_page=current_page, page_guide=page_guide)
    return HttpResponse(t.render(c))

def search_user(request):
    if not request.GET.get("search"):
       return HttpResponseRedirect("/")
    query = request.GET.get("search")
    users = User.objects.filter(username__istartswith=query).all()

    t = loader.get_template('user_search.html')
    c = RequestContext(request, {
        "users": users, "query": query
    })
    return HttpResponse(t.render(c))


# -- Misc -- #
@cache_page(settings.CACHE_STORAGE_TIME)
def top_users(request):
    t = loader.get_template('top_users.html')
    limit = settings.LURKERFAQS_TOP_USERS_TO_SHOW
    top_user_posts = UserPostCount.objects.all().order_by('-count')[:limit]
    top_user_topics = UserTopicCount.objects.all().order_by('-count')[:limit]
    c = RequestContext(request, {
        "top_user_posts": top_user_posts,
        "top_user_topics": top_user_topics
    })
    return HttpResponse(t.render(c))

@cache_page(settings.CACHE_STORAGE_TIME_LONG)
def show_home(request):
    t = loader.get_template('home.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

@cache_page(settings.CACHE_STORAGE_TIME_LONG)
def show_faq(request):
    t = loader.get_template('faqs.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))
