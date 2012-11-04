# -*- coding: utf-8 -*-
import sunburnt
from django.conf import settings

"""
schema.xml
===========
<schema name="lurkerfaqs" version="1.5">
    <fields>
       <field name="title" type="text" indexed="true" stored="true" required="true"/>
       <field name="creator" type="string" indexed="true" stored="true" required="true"/>
       <field name="last_post_date" type="date" indexed="true" stored="true" required="true"/>
       <field name="number_of_posts" type="int" indexed="true" stored="true" required="true"/>

       <field name="topic_id" type="string" indexed="false" stored="true" required="true"/>

    </fields>

</schema>
"""
solr_interface = SolrInterface(settings.SOLR_URL)

def topic_to_doc(topic):
    doc = {
        "topic_id" = topic.pk,
        "title": topic.title,
        "creator": topic.creator.username,
        "last_post_date": topic.last_post_date,
        "number_of_posts": topic.number_of_posts
    }
    return doc

class SolrSearcher(object):
    def index_topics(self, topics):
        docs = [topic_to_doc(t) for t in topics]
        solr_interface.add(docs)

    def search_topic(self, query, start, count):
        return solr_interface.query(title=query) \
            .sortby("-last_post_date") \
            .paginate(start=start, rows=count)

# create singleton class
SolrSearcher = SolrSearcher()
