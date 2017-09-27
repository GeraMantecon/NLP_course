import string
import re
import math
import os
import sys
import json
import collections
import nltk
import argparse
from nltk import word_tokenize
from n2w import convert
from nltk.corpus import words as nltk_words
from nltk.tokenize import RegexpTokenizer
from urlparse import urlparse
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.util import ngrams
from gensim.models import Phrases
from sklearn.metrics import confusion_matrix

tag_list = ['CC','CD','DT','EX','FW','IN','JJ','JJR','JJS','LS','MD','NN','NNS','NNP','NNPS','PDT','POS','PRP','PRP$','RB','RBR','RBS','RP','SYM',
            'TO','UH','VB','VBD','VBG','VBN','VBP','VBZ','WDT','WP','WP$','WRB','USR', 'HT', 'URL', 'RT']

def countTags(input_set):
    element_statistics = {}
    tags = [str(element.split('_')[1]) for element in input_set if "_" in element]
    tags = [tag for tag in tags if tag in tag_list]
    for element in tags:
        if not element_statistics.has_key(element):
            element_statistics.update({element:1})
        else:
            occurrences = element_statistics[element]
            element_statistics.update({element:occurrences+1})
    element_statistics = sorted(element_statistics.iteritems(),key=lambda x: x[1], reverse=True)
    return element_statistics

def calculateAccuracy(expected, predicted):
    with open(expected) as f:
        expected_tags = [str(token) for line in f.readlines() for token in line.rstrip().split(' ')]
        print 'Number of tags on expected: ' + str(len(expected_tags))
    with open(predicted) as f:
        predicted_tags = [str(token) for line in f.readlines() for token in line.rstrip().split(' ')]
        print 'Number of tags on predicted: ' + str(len(predicted_tags))
    true_positives = sum(1 for element in predicted_tags if element in expected_tags)
    print "Matches: "+str(true_positives)
    print "Accuracy: "+ str(float(true_positives)/float(len(expected_tags)))
    countings = countTags(predicted_tags)
    with open('POS_predicted_output.txt','w') as f:
		for element in countings:
			f.write(str(element[0].encode("utf-8")+' == '+str(element[1])+'\n'))

def main(expected, predicted):
    calculateAccuracy(expected, predicted)

if __name__ == '__main__':
	main(sys.argv[1],sys.argv[2])
