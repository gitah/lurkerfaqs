CREATE INDEX topic_composite_date ON gfaqs_topic(board_id, last_post_date);
CREATE INDEX post_composite_date ON gfaqs_post(creator_id, date);
