from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from scipy import spatial

def get_stemmer(sentence):
	"""
	This method is used to remove all the stop words and 
	perfom stemming. Later returns the list of stemmed
	words i.e., words without prefix
	"""
	temp = []
	stop_words = set(stopwords.words('english'))
	porter = PorterStemmer()

	word_tokens = word_tokenize(sentence)
	filtered_sentence = [w.lower() for w in word_tokens if not w.lower() in stop_words]

	temp = [porter.stem(word) for word in filtered_sentence]
	return temp


def __tfidf_obj__(sentence_dict):
	"""
	This method is used to generate the objects of countvectorizer
	and tfidfvectorizer
	"""
	countvectorizer = CountVectorizer(analyzer='word', stop_words='english')
	tfidfvectorizer = TfidfVectorizer(analyzer='word',stop_words='english')

	# convert th documents into a matrix
	countvectorizer.fit(sentence_dict.values())
	tfidfvectorizer.fit(sentence_dict.values())

	return countvectorizer, tfidfvectorizer


def __tfidf__(sentence_dict):
	"""
	This method is used to process the dictonary of
	sentence into a tf and idf format dataframe
	"""
	countvectorizer, tfidfvectorizer = __tfidf_obj__(sentence_dict)

	# transform with the dataset
	count_wm = countvectorizer.transform(sentence_dict.values())
	tfidf_wm = tfidfvectorizer.transform(sentence_dict.values())

	# retrieve the terms found in the corpora
	# if we take same parameters on both Classes(CountVectorizer and TfidfVectorizer) , 
	# it will give same output of get_feature_names() methods)
	count_tokens = countvectorizer.get_feature_names()
	tfidf_tokens = tfidfvectorizer.get_feature_names()

	df_countvect = pd.DataFrame(data=count_wm.toarray(),
					index=sentence_dict.keys(), columns = count_tokens)

	df_tfidfvect = pd.DataFrame(data=tfidf_wm.toarray(),
					index=sentence_dict.keys(), columns = tfidf_tokens)

	return df_countvect, df_tfidfvect



def tfidf_score(sentence_dict, active_paper_index):
	"""
	This method is used to calculate tf-idf score for each
	document and return dict of document as key and score as value
	"""
	scores = {}
	tf, idf = __tfidf__(sentence_dict)
	tf_idf = tf.mul(idf, axis=0)
	active = tf_idf.loc[active_paper_index]
	tf_idf.drop([active_paper_index], axis=0, inplace=True)

	for i in tf_idf.index.values:
		scores[i] = 1 - spatial.distance.cosine(active, tf_idf.loc[i])

	return scores




def bm25_score(sentence_dict, active_paper_index, d_k1=1.2, d_b=0.75, q_k1=1000, q_b=0):
	"""
	This method is used to calculate bm25 score for each
	document and return dict of document as key and score as value
	"""
	scores = {}
	countvectorizer, tfidfvectorizer = __tfidf_obj__({active_paper_index: sentence_dict[active_paper_index]})
	del sentence_dict[active_paper_index]

	# transform with the dataset
	count_wm = countvectorizer.transform(sentence_dict.values())
	tfidf_wm = tfidfvectorizer.transform(sentence_dict.values())

	# retrieve the terms found in the corpora
	# if we take same parameters on both Classes(CountVectorizer and TfidfVectorizer) , 
	# it will give same output of get_feature_names() methods)
	count_tokens = countvectorizer.get_feature_names()
	tfidf_tokens = tfidfvectorizer.get_feature_names()

	df_countvect = pd.DataFrame(data=count_wm.toarray(),
					index=sentence_dict.keys(), columns = count_tokens)

	avg_doc_len = df_countvect.sum(axis=0).mean()

	df_tfidfvect = pd.DataFrame(data=tfidf_wm.toarray(),
					index=sentence_dict.keys(), columns = tfidf_tokens)

	for i in sentence_dict.keys():
		total = 0.0
		doc_len = df_countvect.sum(axis=0)[i]
		for col in count_tokens:
			total += df_tfidfvect[col].loc[i] * ((d_k1 + 1) * \
					df_countvect[col].loc[i])/(d_k1*((1-d_b) + \
					(b * (doc_len/avg_doc_len))) + df_countvect[col].loc[i])

		scores[i] = total

	return scores





