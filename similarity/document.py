# -*- coding: utf-8 -*-
import itertools
import re

from nltk import PorterStemmer
from nltk.tokenize import wordpunct_tokenize

import numpy as np
from scipy.spatial import distance

from gfaqs.models import User, Topic, Post
from batch.models import UserTopicCount, UserPostCount
from batch.user_counts import UserCountBatch
from similarity.stopwords import STOPWORDS
from util.linkify import HTML_RE

"""
Given a Document (ie. a Topic or User), this will generate Documents similar to
it via. cosine similarity.

Steps:
    1. Create Document from database
        - Topic => (topic title, Posts of topic)
        - User => (All topics made, All posts made, All signature)
        - skip if document is too small
            - Topic => # posts < 10
            - User => # topics + # posts < 50

    2. Turn Document into a vector
        - normalize document: porter stemmer
        - TODO: determine if I want to use tf-idf or (bag of words, remove stop words)

    3. Repeat step 1 and 2 to create a matrix of vectors (in csv)

    4. Calculate cosine similarity of entire matrix using scipy distance.pdist
        - http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html#scipy.spatial.distance.pdist

    5. For each Document, get top N similar Documents
        - via database pk

    6. Store Similar Documents in a db table

    7. Update views to display these similar documents


NOTE: steps 1 and 2 can be streamed
"""

MIN_USER_POSTS = 5;

TAG_RE = re.compile(r'<.*?>', re.IGNORECASE)
ALPHANUMERIC_RE = re.compile('^[a-zA-z0-9_]*$', re.IGNORECASE)
NUM_RE = re.compile('^\d*$')

stemmer = PorterStemmer()

def normalize_text(text):
    text = re.sub(HTML_RE, '', text)
    text = re.sub(TAG_RE, '', text)
    tokens = wordpunct_tokenize(text)
    normalized_words = {normalize_word(tok) for tok in tokens}
    return {word for word in normalized_words if word}

def normalize_word(word):
    if not re.match(ALPHANUMERIC_RE, word) or re.match(NUM_RE, word):
        return ''
    if len(word) <= 2:
        return ''

    word = word.lower()
    if word in STOPWORDS:
        return ''
    return stemmer.stem(word)

def create_user_document(username):
    creator = User.objects.get(username=username)
    user_topics = Topic.objects.filter(creator=creator)
    user_posts = Post.objects.filter(creator=creator)

    # TODO: Signatures ?? will have to normalize them though...
    topic_words = [topic.title for topic in user_topics]
    post_words = [post.contents for post in user_posts]

    all_words = ' '.join(topic_words + post_words)
    return normalize_text(all_words)

def create_user_documents(data_file):
    # need this count information to filter users
    UserCountBatch().start()

    # Create documents
    words = {}
    docs = []
    for user in UserPostCount.objects.filter(count__gte=MIN_USER_POSTS):
        doc = create_user_document(user.username)
        for word in doc:
            words[word] = words.get(word, 0) + 1
        docs.append(doc)

    # Create vectors from documents
    vecs = []

    # normalize list of words
    norm_words = set()
    for w in words:
        if words[w] > 1:
            norm_words.add(w)
    for doc in docs:
        vec = [1 if w in doc else 0 for w in norm_words]
        vecs.append(vec)

    # clear the output file
    with open(data_file, 'w') as fp:
        for vec in vecs:
            vec_str = ','.join([str(f) for f in vec])
            fp.write("%s,%s\n" % ('TODO', vec_str))

def create_feature_vectors_from_documents(data_file):
    # load input_file into memory
    # turn into feature vector via bag of words model
    # dictionary ???
    # output
    pass

def calculate_similarities(input_file, results_file):
    # for each vector: run pdist with cosine distance
    # write result to result file
    pass

def load_results(results_file):
    # load results of similarities into database
    pass
