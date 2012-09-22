from django.http import HTTPResponse, HTTPResponseServerError, HTTPResponseNotFound
from django.core.paginator import Paginator

import gfaqs.models as models

"""
URL paths were designed to mimic the url paths on gamefaqs
"""

# -- Boards -- #
def show_boards(request):
    # /boards
    pass

# -- Topics -- #
def show_board(request):
    # /boards/<board_alias>?page=2
    path_args = request.path.split('/')
    assert len(path_args), 3
    board_id = path_args[2]
    pass

# -- Posts -- #
def show_topic(request):
    # /boards/<board_alias>/<topic_num>?page=2
    pass

# -- Users -- #
def show_user(request):
    # /user/<username>
    pass

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
