from nltk import PorterStemmer
import numpy as np
from scipy.spatial import distance

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

def create_topic_document(db_topic):
    # aggregate words into set ???
    # return set of words
    pass

def document_to_vector(pk, doc):
    # apply porter stemmer
    # remove stop words or apply tf-idf
    # return vector (labeled with primary key)
    pass

def create_topic_documents(data_file):
    # create orm request
    # for topic in topics: doc = create_topic_documents(topic)
    # v = document_to_vector(topic.pk, doc)
    # write v to a output file
    pass

def calculate_similarities(input_file, results_file):
    # load input_file into memory
    # for each vector: run pdist with cosine distance
    # write result to result file
    pass

def load_results(results_file):
    # load results of similarities into database
    pass
