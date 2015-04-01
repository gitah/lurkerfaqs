POPUP_MODAL = "#deletePostModal";
DONATE_BUTTON = "#donateButton";

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
        // Ajax call to API
        // Parse auth_url
        // Forward to auth_url
    });
})
