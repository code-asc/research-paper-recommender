import numpy as np
import pandas as pd


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
	def __init__(self, train_size=0.5, random_state=31):
		None