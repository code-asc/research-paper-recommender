from ranking.hits import Ranking
from tqdm import tqdm
# import tqdm.notebook as tq
import pandas as pd
import numpy as np
import math


class CFUH:
	"""
	The file_ is the path for the input csv file.
	The data should be of following format
	1) First column represent the user or paper
	2) Second column represent the attributes or the citations
	"""
	def __init__(self, default_path='citation-web/', file_='matrix-way/citation-full-matrix.csv', 
					file_pair='pair-way/citation-full-pairs.txt', normalize_similarity=True, root_node_indexes=None):

		self.file_ = file_
		self.file_pair = file_pair
		self.default_path = default_path
		self.root_node_indexes = root_node_indexes
		self.deleted_index = []
		
		self.df = pd.read_csv(self.default_path + file_)

		self.index_col = self.df.columns[0]
		self.df.set_index(self.df[self.index_col], inplace=True)
		self.df.index = self.df.index.astype(str, copy = False)

		self.df.drop([self.index_col], axis=1, inplace=True)

		self.__clean__()
		self.__normalize_rank__()

		self.similarity_mat = self.__similarity__()
		self.column_names = self.df.columns
		

		if normalize_similarity:
			self.similarity_mat = self.__normalize_col__(self.similarity_mat)

 
	def __clean__(self):
		"""
		This method is used to remove the index for which there are 
		no items/citations
		"""
		indexes = self.df.index.values.copy()
		print('removing the indexes with no citations....')
		for index in indexes:
			if not (1 in self.df.loc[index].values):
				self.deleted_index.append(index)
				print('Deleting : ', index)
				self.df.drop(index, inplace=True)

	def get_deleted_index(self):
		return self.deleted_index

	def __normalize_rank__(self):
		print('page rank normalization on dataframe....')
		
		scores = Ranking(file_=self.default_path+self.file_pair, root_nodes=self.root_node_indexes).scores()

		for index in tqdm(self.df.index.values):
			self.df.loc[index] = self.df.loc[index] * scores.get(index, 0)

	def __similarity__(self):
		"""
		This method is used to calculate the similarity between each
		column in the dataframe
		"""
		cols = self.df.columns
		num_of_cols = len(cols)
		similarity_mat = pd.DataFrame(np.zeros((num_of_cols, num_of_cols)), columns=cols, index=cols)
		print('creating similarity matrix....')
		for col_i in tqdm(cols):
			for col_j in cols:
				similarity_mat.loc[col_i][col_j] = np.dot(self.df[col_i], self.df[col_j])/(np.linalg.norm(self.df[col_i]) * np.linalg.norm(self.df[col_j]))
		return similarity_mat


	def __normalize_col__(self, similarity_matrix):
		"""
		This method is used to normalize the similarity matrix.
		It is column-wise normalization, meaning the items are normalized
		to reduce the impact of moderate item overlap

		Reference below
		http://glaros.dtc.umn.edu/gkhome/node/124

		https://math.stackexchange.com/questions/278418/normalize-values-to-sum-1-but-keeping-their-weights
		
		"""
		data = similarity_matrix.copy()
		cols = data.columns
		
		print('normalizing the similarity matrix....')
		for col in tqdm(cols):
			data.loc[col][col] = 0
			data[col] = data[col].div(data[col].sum())

		return data


	def __top__(self, item, n=20):
		"""
		This method returns the top N for each item or citations
		The parameter n represents # of items or citations to return in descending order
		"""
		return self.similarity_mat.loc[item].sort_values(ascending=False)[:n].iloc[1:]


	def recommend(self, index, n=10, k=20):
		"""
		The following is way the algorithm works
		1) For each item, the k most similar items are computed using __top__ method to get {j1, j2, j3, j4 ....}
		   and also the similarity score {s1, s2, s3, s4, ....}
		2) Let U be the items purchased or citations by the customer
		3) Compute C candidate recommended items by taking the union of K most similar items for each item j ∈ U
		   and remove any item that are already in U
		4) For each item c ∈ C such that, find similarity wrt to items in U and sum them up. Output the top N
		   recommendations in decending order
		"""

		# Here we are index a user/paper. We are trying to find most relevant suggestion.
		# So we dine unknown. It points to the items/citations that are purchased or equals
		# to 1
		# Next we compute the top k relevant items for the user/paper
		# We remove the items that are already known/purchased
		# Then we find the similarity wrt to each item/citation to all in set U and sum them.

		unknowns = set()
		print(self.df.index.values)
		already_known = set(self.df.loc[index][self.df.loc[index][self.column_names] > 0.0].index.values)
		for item in already_known:
			unknowns.update(self.__top__(n=k, item=item).index.values)

		unknowns = unknowns - already_known
		suggestions = pd.DataFrame(np.zeros((len(unknowns))), index = unknowns, columns=['score'])

		for unknown in tqdm(unknowns):
			temp = 0
			for known in already_known:
				temp += self.similarity_mat.loc[unknown][known]
			suggestions.loc[unknown] = temp

		suggestions = suggestions.sort_values(by=['score'], ascending=False)
		return suggestions.index.values[:n], suggestions['score'][:n].values




