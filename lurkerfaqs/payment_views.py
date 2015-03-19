# -*- coding: utf-8 -*-
import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.http import HttpResponseServerError, HttpResponseNotFound, Http404
from django.core.urlresolvers import reverse
from django.conf import settings

from gfaqs.admin import ContentVisibilityManager
from payments.paypal import PaypalServiceAccessor
from lurkerfaqs import views

log = logging.getLogger(settings.MISC_LOGGER)

DELETE_POST_AMOUNT_USD = 5.0
DELETE_TOPIC_AMOUNT_USD = 10.0
DELETE_USER_AMOUNT_USD = 25.0

DELETE_POST_DESCRIPTION_TMPL = "Payment to delete topic %s, post %s"

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
    return _create_payment(request, DELETE_POST_AMOUNT_USD, ret_url)

def _create_payment(request, amount, return_url):
    if not ppAcc:
        raise Http404("Server not configured for payments")

    # cancel url is same as return url since payment confirmation api will
    # figure out whether or not user paid
    approval_url = ppAcc.create_payment(amount, return_url, return_url, description)

    resp = {
        "approval_url": approval_url
    }
    return JsonResponse(resp)


def confirm_payment_delete_post(request, gfaqs_topic_id, post_num):
    """
        1. confirm payment and execute
        2. find post
        3. delete post
        4. redirect to original topic
    """
    redirect_url = reverse(views.show_topic, args=[gfaqs_topic_id, post_num])
    success = _confirm_payment(request, redirect_url)
    if not success:
        log.info("Payment failed for post %s,%s" % (gfaqs_topic_id, post_num))
        return HttpResponseRedirect(redirect_url)
    post = visibility_manager.get_post(gfaqs_topic_id, post_num)
    if not post:
        log.error("Post %s,%s could not be found" % (gfaqs_topic_id, post_num))
        return HttpResponseRedirect(redirect_url)
    visibility_manager.hide_post(gfaqs_topic_id, post_num)
    log.info("Successfully processed payment and hid post %s!" % post)
    return HttpResponseRedirect(redirect_url)


def _extract_payment_params(request):
    """ Example:
    ?success=true&paymentId=<PAYMENT_ID>&token=<TOKEN>&PayerID=<PAYER_ID>
    """
    qs_dict = request.GET
    success = qs_dict.get(PaypalServiceAccessor.RESPONSE_QS_SUCCESS, False)
    payment_id = qs_dict.get(PaypalServiceAccessor.RESPONSE_QS_PAYMENT_ID)
    payer_id = qs_dict.get(PaypalServiceAccessor.RESPONSE_QS_PAYER_ID)
    return (success, payment_id, payer_id)

# TODO: redirect with flash
def _confirm_payment(request):
    if not ppAcc:
        raise Http404("Server not configured for payments")

    success, payment_id, payer_id  = _extract_payment_params(request)
    if not success:
        return False
    return pp.execute_payment(payment_id, payer_id)
