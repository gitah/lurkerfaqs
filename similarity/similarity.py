import itertools

from nltk import PorterStemmer
from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords

import numpy as np
from scipy.spatial import distance

from gfaqs.models import User, Topic, Post
from batch.models import UserTopicCount, UserPostCount

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

def create_user_document(user_id):
    user_topics = Topic.objects.filter(creator_id=user_id)
    user_posts = Post.objects.filter(creator_id=user_id)

    # TODO: Signatures ?? will have to normalize them though...
    topic_words = [topic.title for topic in user_topics]
    post_words = [post.contents for post in user_posts]
    tokens = wordpunct_tokenize(' '.join(topic_words + post_words))
    stemmer = PorterStemmer()
    return {stemmer.stem(tok) for tok in tokens if tok \
            not in stopwords.words('english')}

def create_user_documents(data_file):
    # need this count information to filter users
    UserCountBatch().start()

    # clear the output file
    with open(data_file, 'w') as fp:
        pass

    with open(data_file, 'w+') as fp:
        for user in UserPostCount.objects.filter(count_gte=MIN_USER_POSTS):
            doc = create_user_document(user.pk)
            fp.write("%s\t%s" % (user.pk, ' '.join(list(vec))))

def calculate_similarities(input_file, results_file):
    # load input_file into memory
    # turn into feature vector via bag of words model
    # for each vector: run pdist with cosine distance
    # write result to result file
    pass

def load_results(results_file):
    # load results of similarities into database
    pass
