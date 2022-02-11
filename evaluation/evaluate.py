import random
import numpy as np
import pandas as pd
from pprint import pprint


class Train_test_split:
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

	Find more details from the paper
	https://dl.acm.org/doi/10.1145/1864708.1864740
	"""
	def __init__(self, train_size=0.5, min_ref_limit= 15, random_state=31):
		self.train_size = train_size
		self.min_ref_limit = min_ref_limit
		self.random_state = 31

	def __split__(self, dois):
		"""
		This method split the data into train and test set
		"""
		random.seed(self.random_state)
		random.shuffle(dois)

		train_size = float(len(dois)) * self.train_size

		train_set = dois[:train_size]
		test_set = dois[train_size:]

		return (train_set, test_set)

	def __pickout__(self, data, test_set):
		for 

	def fit(self, doi_dict):
		doi_dict = doi_dict.copy()
		doi_less_than_limit = {}
		dois = []

		for doi in doi_dict.keys():
			if len(doi_dict[doi]) < min_ref_limit:
				doi_less_than_limit[doi] = len(doi_dict[doi])
				doi_dict.pop(doi, None)
			else:
				dois.append(doi)

		print("The following doi's are ignored because of low reference :")
		pprint(doi_less_than_limit)

