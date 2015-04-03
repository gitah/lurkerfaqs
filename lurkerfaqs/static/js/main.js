"use strict";

var POPUP_MODAL = "#deletePostModal";
var DONATE_BUTTON = "#donateButton";

var CREATE_PAYMENTS_DELETE_POST_URL = "/payment/delete_post";
var CREATE_PAYMENTS_DELETE_TOPIC_URL = "/payment/delete_topic";

var getCreatePaymentDeleteTopicUrl = function(topicId) {
    return CREATE_PAYMENTS_DELETE_TOPIC_URL + "/" + topicId;
}

var getCreatePaymentDeletePostUrl = function(topicId, postNum) {
    return CREATE_PAYMENTS_DELETE_POST_URL + "/" + topicId + "/" + postNum;
}

var showDeleteContentPopup = function(topicId, postNum) {
    var popupModal$ = $(POPUP_MODAL);
    // NOTE: postNum == undefined means delete topic
    popupModal$.data('contentId', {
        topicId: topicId,
        postNum: postNum
    });
    popupModal$.modal({})
};

var toggleDeletePostVisibility = function() {
    $(".deletePostButton").toggle();
}

$(function() {

    $(".deletePostButton").hide();

    var createDeletePostModal = function(modal, topicId, postNum) {
        modal.find('.modal-title').text("Delete Post #" + postNum);
        modal.find('.currency-text').text("$5.00");
        modal.find('.contentType').text("post");
    };

    var createDeleteTopicModal = function(modal, topicId, postNum) {
        modal.find('.modal-title').text("Delete Topic #" + topicId);
        modal.find('.currency-text').text("$15.00");
        modal.find('.contentType').text("topic");
    };

    $(POPUP_MODAL).on('show.bs.modal', function(event) {
        var modal = $(this);
        var data = modal.data('contentId');
        var topicId = data['topicId'];
        var postNum = data['postNum'];

        if(topicId && postNum) {
            createDeletePostModal(modal, topicId, postNum);
        } else {
            createDeleteTopicModal(modal, topicId);
        }

        // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
        //
    });

    $(DONATE_BUTTON).click(function(event) {
        var data = $(POPUP_MODAL).data('contentId');
        var topicId = data['topicId'];
        var postNum = data['postNum'];

        $(this).html('<i class="fa fa-spinner fa-spin"></i>');
        $(this).prop('disabled', true)

        var url = "";
        if(topicId && postNum) {
            url = getCreatePaymentDeletePostUrl(topicId, postNum);
        } else {
            url = getCreatePaymentDeleteTopicUrl(topicId);
        }

        $.getJSON(url, function(resp) {
            var approvalUrl = resp["approval_url"];
            window.location.replace(approvalUrl);
        });
    });
})
