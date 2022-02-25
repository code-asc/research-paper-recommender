import os
import random
import numpy as np
import pandas as pd
from pprint import pprint
from tqdm.notebook import tqdm
from utils.utils import get_paper_citation_pairs


class Train_Test_Split_Plain:
	"""
	This class is used to input all the dois and split the
	data into two sets i.e., train and test set. The train
	set contains all the citations for the paper when forming 
	a citation web. But for test set, we pick the threseold of
	data as hidden and check them with the recommendations

	Rules for evaluation
	1) Each doi should have atleast 15 references from the dataset

	2) For test set, pick out 5 reference from each paper and use others
	   as normal in the citation web. After finding recommendtions, check it 
	   they match with the already picked 5 citations

	3) We evaluate the algorithm using the half-life α of 5

	Parameters:
	recommender : Any recommender that follows the standards of abstract class defined
	train_size : Size of the training set
	min_ref_limit : Minimum # of references required in each paper. If less than 
					threshold, then ignore them
	random_state : Similar to seed
	min_held_out_ref : # of references that need to be kept aside in each of the test 
						paper for evaluation
	reuse : If the matrix and pair-wise file already exists, then simply use them 
			instead of creating new files again. To activate, set it to true

	Find more details from the paper
	https://dl.acm.org/doi/10.1145/1864708.1864740
	"""
	def __init__(self, recommender, train_size=0.5, min_ref_limit= 15, random_state=31, 
					min_held_out_ref=5, r_max=3.6425, reuse=False, biased=False,
					normalize_similarity=True):
		self.recommender = recommender
		self.train_size = train_size
		self.min_ref_limit = min_ref_limit
		self.random_state = random_state
		self.min_held_out_ref = min_held_out_ref
		self.reuse = reuse
		self.r_max = r_max
		self.biased = biased
		self.normalize_similarity = normalize_similarity

	def __split__(self, dois):
		"""
		This method split the data into train and test set
		"""
		random.seed(self.random_state)
		random.shuffle(dois)

		train_size = int(float(len(dois)) * self.train_size)

		train_set = dois[:train_size]
		test_set = dois[train_size:]

		return (train_set, test_set)

	def __pickout__(self, data_, test_set):
		"""
		This method picks out the references from the test data
		paper and returns the hold out test references
		"""
		data = data_.copy()
		held_out = {}
		for test in test_set:
			held_out[test] = random.sample(data[test], self.min_held_out_ref)
			data[test] = [x for x in data[test] if x not in held_out[test]]
		
		return held_out, data

	def __recommendations__(self, test_set):
		"""
		This method is used to give recommendations based
		on inputted algorithm. The algorithm depends on the
		input variable recommender in the constructor

		Parameters:
		test_set : test_set is required to produce the recommendations and 
				   use them for evaluation later in __evaluate__ method
		"""
		recommendations = {}
		if self.recommender.__name__ == 'CFUPR':
			obj = self.recommender(default_path='temp/', file_='matrix-way/temp-citation-matrix.csv',
									file_pair='pair-way/temp-citation-pairs.txt', biased=self.biased,
									normalize_similarity=self.normalize_similarity)
		
		elif self.recommender.__name__ == 'CFUH':
			obj = self.recommender(default_path='temp/', file_='matrix-way/temp-citation-matrix.csv',
									file_pair='pair-way/temp-citation-pairs.txt')

		else:
			obj = self.recommender(default_path='temp/matrix-way/', file_='temp-citation-matrix.csv')

		for test in test_set:
			suggestions, _ = obj.recommend(test)

			recommendations[test] = suggestions

		return recommendations

	
	def __rating_matrix__(self, data_):
		"""
		This method is used to create rating matrix and also
		pair wise relations
		"""
		data = data_.copy()
		citation_set = set()
		for key in data.keys():
			citation_set.update(data[key])

		index_ = data.keys()
		df = pd.DataFrame(np.zeros((len(index_), len(citation_set))), index=index_, columns=citation_set)

		for i in index_:
			for j in citation_set:
				if j in data[i]:
					df.loc[i][j] = 1

		df.to_csv('temp/matrix-way/temp-citation-matrix.csv')
		get_paper_citation_pairs(df, dir_='temp/pair-way/', out_file='temp-citation-pairs.txt')

	def __evaluate__(self, dois_, suggestions_):
		"""
		This method evaluates the algorithm using the half-life formula	
		descibed in the paper

		Find more details from the paper
		https://dl.acm.org/doi/10.1145/1864708.1864740
		"""
		suggestions = suggestions_.copy()
		dois = dois_.copy()
		whole_sum = 0

		print('finishing evaluation....')
		for key in tqdm(suggestions.keys()):
			each_sum = 0
			for i in range(len(suggestions[key])):
				if suggestions[key][i] in dois_[key]:
					each_sum += 1.0/( 2 ** ((i) / (self.min_held_out_ref - 1)))

			whole_sum += each_sum

		return whole_sum/(len(suggestions.keys()) * self.r_max)


	def fit(self, doi_dict_):
		doi_dict = doi_dict_.copy()
		doi_less_than_limit = {}
		dois = []
		doi_keys = list(doi_dict.keys())
		for doi in doi_keys:
			if len(doi_dict[doi]) < self.min_ref_limit:
				doi_less_than_limit[doi] = len(doi_dict[doi])
				doi_dict.pop(doi, None)
			else:
				dois.append(doi)

		print("The following doi's are ignored because of low reference :")
		pprint(doi_less_than_limit)

		train_set, test_set = self.__split__(dois)
		held_out, renewed_data = self.__pickout__(doi_dict, test_set)


		if not self.reuse:
			self.__rating_matrix__(renewed_data)
		else:
			if not (os.path.isfile('temp/matrix-way/temp-citation-matrix.csv') and 
					os.path.isfile('temp/pair-way/temp-citation-pairs.txt')):
				self.__rating_matrix__(renewed_data)

		suggestions = self.__recommendations__(test_set)
		return self.__evaluate__(doi_dict, suggestions)