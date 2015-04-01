"use strict";

var POPUP_MODAL = "#deletePostModal";
var DONATE_BUTTON = "#donateButton";

var CREATE_PAYMENTS_DELETE_POST_URL = "/payment/delete_post";

var getCreatePaymentDeletePostUrl = function(topic_id, post_num) {
        return CREATE_PAYMENTS_DELETE_POST_URL + "/" + topic_id + "/" + post_num;
}

var showDeletePostPopup = function(topic_id, post_num) {
    var popupModal$ = $(POPUP_MODAL);
    popupModal$.data('post_id', {
        topic_id: topic_id,
        post_num: post_num
    });
    popupModal$.modal({})
};

$(function() {

    $(POPUP_MODAL).on('show.bs.modal', function(event) {
        var modal = $(this);
        var data = modal.data('post_id');
        var topic_id = data['topic_id'];
        var post_num = data['post_num'];

        // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
        modal.find('#post_num_display').text(post_num)
    });

    $(DONATE_BUTTON).click(function(event) {
        var data = $(POPUP_MODAL).data('post_id');
        var topic_id = data['topic_id'];
        var post_num = data['post_num'];

        $(this).html('<i class="fa fa-spinner fa-spin"></i>');
        $(this).prop('disabled', true)

        var url = getCreatePaymentDeletePostUrl(topic_id, post_num);
        $.getJSON(url, function(resp) {
            var approvalUrl = resp["approval_url"];
            window.location.replace(approvalUrl);
        });
    });
})
