# -*- coding: utf-8 -*-
import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.http import HttpResponseServerError, HttpResponseNotFound, Http404
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages

from gfaqs.admin import ContentVisibilityManager
from payments.paypal import PaypalServiceAccessor
from lurkerfaqs import views

log = logging.getLogger(settings.MISC_LOGGER)

DELETE_POST_AMOUNT_USD = 5.0
DELETE_TOPIC_AMOUNT_USD = 15.0
DELETE_USER_AMOUNT_USD = 25.0

DELETE_POST_DESCRIPTION_TMPL = "Payment to delete topic %s, post %s"
DELETE_TOPIC_DESCRIPTION_TMPL = "Payment to delete topic %s"
PAYMENT_ERROR_MSG = "Error Processing Payment. Please try again."
PAYMENT_DELETE_POST_SUCCESS_MSG = "Success! Post #%s by %s has been deleted"
PAYMENT_DELETE_TOPIC_SUCCESS_MSG = "Success! Topic #%s by %s has been deleted"

visibility_manager = ContentVisibilityManager()
ppAcc = None
if settings.PAYPAL_CLIENT_ID and settings.PAYPAL_CLIENT_SECRET:
    mode = PaypalServiceAccessor.CLIENT_SANDBOX_MODE if settings.PAYPAL_USE_SANDBOX else PaypalServiceAccessor.CLIENT_LIVE_MODE
    ppAcc = PaypalServiceAccessor(settings.PAYPAL_CLIENT_ID,
            settings.PAYPAL_CLIENT_SECRET, mode)


def create_payment_delete_post(request, gfaqs_topic_id, post_num):
    post = visibility_manager.get_post(gfaqs_topic_id, post_num)
    if not post:
        raise Http404("Invalid Post %s,%s" % (gfaqs_topic_id, post_num))

    ret_url = reverse(confirm_payment_delete_post, args=[gfaqs_topic_id, post_num])
    description = DELETE_POST_DESCRIPTION_TMPL % (gfaqs_topic_id, post_num)
    return _create_payment(request, DELETE_POST_AMOUNT_USD, ret_url, description)

def create_payment_delete_topic(request, gfaqs_topic_id):
    topic = visibility_manager.get_topic(gfaqs_topic_id)
    if not topic:
        raise Http404("Invalid Topic %ss" % (gfaqs_topic_id))

    ret_url = reverse(confirm_payment_delete_topic, args=[gfaqs_topic_id])
    description = DELETE_TOPIC_DESCRIPTION_TMPL % (gfaqs_topic_id)
    return _create_payment(request, DELETE_TOPIC_AMOUNT_USD, ret_url, description)

def _create_payment(request, amount, return_url, description):
    if not ppAcc:
        raise Http404("Server not configured for payments")

    # cancel url is same as return url since payment confirmation api will
    # figure out whether or not user paid
    full_ret_url = "http://%s%s" % (request.META['HTTP_HOST'], return_url)
    approval_url = ppAcc.create_payment(amount, full_ret_url, full_ret_url, description)

    resp = {
        "approval_url": approval_url
    }
    return JsonResponse(resp)


def confirm_payment_delete_topic(request, gfaqs_topic_id):
    topic = visibility_manager.get_topic(gfaqs_topic_id)
    if not topic:
        messages.error(request, PAYMENT_ERROR_MSG)
        log.error("Topic %s could not be found" % (gfaqs_topic_id))
        return HttpResponseRedirect(redirect_url)
    board_id = topic.board.alias
    redirect_url = reverse(views.show_board, args=[board_id])
    success = _confirm_payment(request)
    if not success:
        messages.error(request, PAYMENT_ERROR_MSG)
        log.error("Payment failed for topic %s" % (gfaqs_topic_id))
        return HttpResponseRedirect(redirect_url)
    visibility_manager.hide_topic(topic)
    messages.success(request, PAYMENT_DELETE_TOPIC_SUCCESS_MSG % (topic.gfaqs_id, topic.creator.username))
    log.info("Successfully processed payment and hid topic %s!" % topic)
    return HttpResponseRedirect(redirect_url)

def confirm_payment_delete_post(request, gfaqs_topic_id, post_num):
    post = visibility_manager.get_post(gfaqs_topic_id, post_num)
    if not post:
        messages.error(request, PAYMENT_ERROR_MSG)
        log.error("Post %s,%s could not be found" % (gfaqs_topic_id, post_num))
        return HttpResponseRedirect(redirect_url)
    board_id, topic_id = post.topic.board.alias, post.topic.gfaqs_id
    redirect_url = reverse(views.show_topic, args=[board_id, topic_id])
    success = _confirm_payment(request)
    if not success:
        messages.error(request, PAYMENT_ERROR_MSG)
        log.error("Payment failed for post %s,%s" % (gfaqs_topic_id, post_num))
        return HttpResponseRedirect(redirect_url)
    visibility_manager.hide_post(post)
    messages.success(request, PAYMENT_DELETE_POST_SUCCESS_MSG % (post.post_num, post.creator.username))
    log.info("Successfully processed payment and hid post %s!" % post)
    return HttpResponseRedirect(redirect_url)


def _extract_payment_params(request):
    """ Example:
    ?paymentId=<PAYMENT_ID>&token=<TOKEN>&PayerID=<PAYER_ID>
    """
    qs_dict = request.GET
    payment_id = qs_dict.get(PaypalServiceAccessor.RESPONSE_QS_PAYMENT_ID)
    payer_id = qs_dict.get(PaypalServiceAccessor.RESPONSE_QS_PAYER_ID)
    return (payment_id, payer_id)

def _confirm_payment(request):
    if not ppAcc:
        raise Http404("Server not configured for payments")

    payment_id, payer_id  = _extract_payment_params(request)
    if not payment_id or not payer_id:
        return False
    return ppAcc.execute_payment(payment_id, payer_id)
