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

class LemmaTokenizer(object):
	def __init__(self):
		self.wnl = WordNetLemmatizer()
	def __call__(self, doc):
		verb_lem = [str(self.wnl.lemmatize(t,'v')) for t in nltk.TweetTokenizer().tokenize(doc)]
		return [str(self.wnl.lemmatize(t,'n')) for t in verb_lem]

def isNumber(token):
    try:
        int(token)
        return True
    except ValueError:
        return False
def preprocessDataset(dataset, foreign_characters, url, numbers, lemmatize):
	processed_set = dataset
	if foreign_characters:
		aux_set = []
		for line in processed_set:
			aux_set.append(" ".join([element for element in re.sub(r'[^\x00-\x7F]+',' ', line).rstrip().split(' ') if element != '']))
		processed_set = aux_set
	if numbers:
		aux_set = []
		for line in processed_set:
			aux_set.append(" ".join([element if isNumber(element) == False else convert(element) for element in line.rstrip().split(' ')]))
		processed_set = aux_set
	if url:
		aux_set = []
		for line in processed_set:
			aux_set.append(" ".join(['REDACTEDURL' if bool(urlparse(element)[1]) else element for element in line.rstrip().split(' ')]))
		processed_set = aux_set
	if lemmatize:
		tk = LemmaTokenizer()
		processed_set = [" ".join(tk(line.lower())) for line in processed_set]
	return processed_set
def filterTokens(tokens, stop_words, punctuation):
	aux_tokens = tokens
	if punctuation:
		aux_tokens = [re.sub(r'[^\w]', '', token) for token in aux_tokens if token not in string.punctuation]
	if stop_words:
		aux_tokens = [token for token in aux_tokens if token not in stopwords.words('english')]
	return aux_tokens
def countElements(input_set):
	element_statistics = {}
	for element in input_set:
		if not element_statistics.has_key(element):
			element_statistics.update({element:1})
		else:
			occurrences = element_statistics[element]
			element_statistics.update({element:occurrences+1})
	element_statistics = sorted(element_statistics.iteritems(),key=lambda x: x[1], reverse=True)
	return element_statistics
def multiwordExpressions(dataset, output_file):
	sentence_stream = []
	processed = preprocessDataset(dataset, True, True, True, True)
	for line in processed:
		sentence_stream.append(filterTokens(line.lower().split(' '), False, True))
	bigram = Phrases(sentence_stream, delimiter=' ')
	trigram = Phrases(bigram[sentence_stream],delimiter=' ')
	bigrams_phrases = bigram[sentence_stream]
	trigrams_phrases = trigram[bigram[sentence_stream]]
	list_trigrams = [str(i) for phrase in list(trigrams_phrases) for i in phrase if " " in i]
	print len(list_trigrams)
	countings_mwe = countElements(list_trigrams)
	with open('mwe_'+output_file,'w') as f:
		for element in countings_mwe:
			f.write(str(element[0].encode("utf-8")+' == '+str(element[1])+'\n'))

def tokenizeAndCount(input_file, stop_words, punctuation, numbers, foreign_characters, lemmatize, url, output_file, multiword):
	if not os.path.exists(input_file):
		print "Input file not existent."
		sys.exit()
	#Load input fle.
	with open(input_file) as f:
		dataset = f.readlines()
	#If multiword option nothing else is done:
	if multiword:
		multiwordExpressions(dataset, output_file)
		sys.exit()
	#Preprocessing options: 1)Foreign characteres. 2)URLs. 3)Change numbers to words. 4)Lematize.
	dataset = [line.lower() for line in dataset]
	if foreign_characters or url or numbers or lemmatize:
		dataset = preprocessDataset(dataset, foreign_characters, url, numbers, lemmatize)
	#Tokenize using NLTK and extra multi word expresions. If the dataset was lematized
	# before, tokenizing step was performed at that time. No need to repeat again.
	tokenized_line = []
	if not lemmatize:
		tokens = nltk.TweetTokenizer().tokenize(" ".join(dataset))
		tokenized_line= [nltk.TweetTokenizer().tokenize(line) for line in dataset]
	else:
		tokens = [token for line in dataset for token in line.split(' ')]
		tokenized_line= [line.split(' ') for line in dataset]
	if len(tokenized_line) > 0:
		with open('tokenized_per_line_'+output_file,'w') as f:
			for element in tokenized_line:
				f.write(str(filterTokens(element,True,True)))
				f.write('\n')
	#Filter tokens to form list of words: 1)Stop words removal. 2)Punctuation removal.
	words_list = []
	if stop_words or punctuation:
		 words_list = filterTokens(tokens,stop_words,punctuation)
	#Obtaine all posible bigrams from list of words.
	bigrams = ngrams(words_list, 2)
	#Token and words countings.
	tokens_counting = countElements(tokens)
	words_counting = countElements(words_list)
	bigrams_counting = countElements([str(bigram[0])+' '+str(bigram[1]) for bigram in bigrams])
	with open('tokens_'+output_file,'w') as f:
		for element in tokens_counting:
			f.write(str(element[0].encode("utf-8")+' == '+str(element[1])+'\n'))
	if punctuation:
		with open('words_'+output_file,'w') as f:
			for element in words_counting:
				f.write(str(element[0].encode("utf-8")+' == '+str(element[1])+'\n'))
	if punctuation and stopwords:
		with open('bigrams_'+output_file,'w') as f:
			for element in bigrams_counting:
				f.write(str(element[0].encode("utf-8")+' == '+str(element[1])+'\n'))
	print "Total tokens found on dataset: " + str(sum([element[1] for element in tokens_counting]))
	print "Total different tokens (types) found on dataset: " + str(len(tokens_counting))
	print "Total unique tokens( appeared only once ): " + str(sum([element[1] for element in tokens_counting if element[1] == 1]))
	print "Type/token ratio for corpus: " + str(float(len(tokens_counting))/float(sum([element[1] for element in tokens_counting])))
	if punctuation:
		print "Total words found on dataset: " + str(sum([element[1] for element in words_counting]))
		print "Total different words found on dataset: " + str(len(words_counting))
		print "Total unique words( appeared only once ): " + str(sum([element[1] for element in words_counting if element[1] == 1]))
		print "Lexical diversity: " +  str(float(len(words_counting))/float(sum([element[1] for element in words_counting])))
	if punctuation and stop_words:
		print "Total bigrams found on dataset: " + str(sum([element[1] for element in bigrams_counting]))
		print "Total different bigrams found on dataset: " + str(len(bigrams_counting))
		print "Total unique bigrams( appeared only once ): " + str(sum([element[1] for element in bigrams_counting if element[1] == 1]))
		print "Lexical density: " +  str(float(len(bigrams_counting))/float(sum([element[1] for element in bigrams_counting])))
def main(argv):
	parser = argparse.ArgumentParser(description='Program regarding assignment 1 for NLP course.')
	parser.add_argument('INPUTFILE', type=str, help='Location of input file containing the dataset to be processed.')
	parser.add_argument('-o', '--output', type=str, default='OutputFile.txt', help='Name of output file contaning resulting tokens and countings.')
	parser.add_argument('-sw','--stopwords', action ='store_true', help='Remove stopwords.')
	parser.add_argument('-p','--punctuation', action ='store_true', help='Remove punctuation marks.')
	parser.add_argument('-n', '--numbers', action ='store_true',help='Translate digits to words.')
	parser.add_argument('-fc', '--foreign_characters', action ='store_true', help='Remove CJK characters and keep ASCII printables.')
	parser.add_argument('-l', '--lematize', action ='store_true',help='Lemmatize tokens.')
	parser.add_argument('-u', '--url', action ='store_true',help='Replacement of URLs')
	parser.add_argument('-mwe', '--multi', action ='store_true',help='Find multiword expressions on dataset.')
	args = parser.parse_args()
	tokenizeAndCount(args.INPUTFILE,args.stopwords,args.punctuation,args.numbers,args.foreign_characters,args.lematize,args.url,args.output,args.multi)

if __name__ == '__main__':
	main(sys.argv[1:])
