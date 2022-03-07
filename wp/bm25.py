import re
import nltk
import pandas as pd
from nltk.stem import PorterStemmer
from rank_bm25 import *
from nltk.tokenize import word_tokenize
from gensim.parsing.preprocessing import STOPWORDS

def __spl_chars_removal__(text):
	"""
	This method is used to remove any 
	non-alpha numeric characters except 
	for space
	"""
	str_ = re.sub("[^0-9a-zA-Z]",' ',text)
	return str_

def __stopwords_removal__(text):
	"""
	This method is used to remove the stopwords from text
	"""
	text_tokens = word_tokenize(text)
	tokens_without_sw = [word for word in text_tokens if not word in STOPWORDS]
	str_ = ' '.join(tokens_without_sw)
	return str_


def __stemmer__(sentence):
	"""
	This method is used to perform porter stemmer
	and return the list of words
	"""
	temp = []
	ps = PorterStemmer()
	for word in sentence.split():
		temp.append(ps.stem(word))
	return temp


def bm25_score(active, docs):
	"""
	Parameters:

	active: The active paper or the query set
	docs: In our case, these are the paper we want to find that are 
			   relevant to the query 

	The steps involve,
	1) Remove non-alphabet characters except for spaces
	2) Remove the stopwords
	4) Perform porter stemmer
	4) Use bm25 package to find the score
	"""
	tokenized_query = __stemmer__(__stopwords_removal__(__spl_chars_removal__(active)))
	tokenized_corpus = [__stemmer__(__stopwords_removal__(__spl_chars_removal__(docs[key]))) 
							for key in docs.keys()]

	bm25 = BM25Okapi(tokenized_corpus)
	doc_scores = bm25.get_scores(tokenized_query)

	doc_names = list(docs.keys())
	temp = {}
	for i in range(len(doc_names)):
		temp[doc_names[i]] = doc_scores[i]

	return dict(sorted(temp.items(), key=lambda x: x[1], reverse=True))