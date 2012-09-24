from django.http import HTTPResponse, HTTPResponseServerError, HTTPResponseNotFound, HTTP404
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.template import loader, Context

import gfaqs.models as models

"""
URL paths were designed to mimic the url paths on gamefaqs
"""

# -- Boards -- #
def show_boards(request):
    boards = models.Boards.objects.all()
    t = loader.get_template('lurkerfaqs/templates/boards.html')
    c = Context(boards = boards)
    return HTTPResponse(t.render(c))

# -- Topics -- #
def show_board(request, board_alias):
    # /boards/<board_alias>?page=2
    try:
        board = models.Board.get(alias=board_alias)
    except ObjectDoesNotExist:
        raise HTTP404

    # TODO: paginate
    topics = models.Topic.filter(board=board)

    t = loader.get_template('lurkerfaqs/templates/topics.html')
    c = Context(board=board, topics=topics)
    return HTTPResponse(t.render(c))

# -- Posts -- #
def show_topic(request, board_alias, topic_num):
    # /boards/<board_alias>/<topic_num>?page=2
    try:
        board = models.Boards.get(alias=board_alias)
        topic = models.Topics.get(gfaqs_id=topic_num)
    except ObjectDoesNotExist:
        raise HTTP404

    # TODO: paginate
    posts = models.Post.filter(board=board)

    t = loader.get_template('lurkerfaqs/templates/posts.html')
    c = Context(board=board, topic=topic, post=post)
    return HTTPResponse(t.render(c))

# -- Users -- #
def show_user(request, username):
    # /user/<username>
    try:
        user = models.User.get(username=username)
    except ObjectDoesNotExist:
        raise HTTP404

    num_topics = num_posts = 0

    t = loader.get_template('lurkerfaqs/templates/user.html')
    c = Context(user=user, num_topics=num_topics, num_posts=num_posts)
    return HTTPResponse(t.render(c))

def show_user_posts(request):
    # /users/<username>/posts?page=2
    pass

def show_user_topics(request):
    # /users/<username>/topics?page=2
    pass

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
