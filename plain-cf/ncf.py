from tqdm import tqdm
import pandas as pd
import numpy as np


class NCF:
	"""
	The file_ is the path for the input csv file.
	The data should be of following format
	1) First column represent the user or paper
	2) Second column represent the attributes or the citations
	"""
	def __init__(self, default_path='../citation-web/matrix-way/', file_):
		self.file_ = file_
		self.df = pd.read_csv(default_path + file_)

		self.index_col = self.df.columns[0]
		self.df.set_index(self.df[self.index_col], inplace=True)
		self.df.drop([self.index_col], axis=1, inplace=True)

		self.similarity_mat = self.__similarity__()
		self.column_names = self.df.columns

	def __normalize__(self):
		print('Normalizing dataframe....')
		for index in tqdm(self.index_col):
			self.df.loc[index] = self.df.loc[index].div(np.linalg.norm(self.df.loc[index]))

	def __similarity__(self):
		"""
		This method is used to calculate the similarity between each
		column in the dataframe
		"""
		cols = self.df.columns
		num_of_cols = len(cols)
		similarity_mat = pd.DataFrame(np.zeros((num_of_cols, num_of_cols)), columns=cols, index=cols)
		print('Creating similarity matrix....')
		for col_i in tqdm(cols):
			for col_j in cols:
				similarity_mat.loc[col_i][col_j] = np.dot(self.df[col_i], self.df[col_j])/(np.linalg.norm(self.df[col_i]) * np.linalg.norm(self.df[col_j]))
		return similarity_mat



	def __top__(self, item, n=20):
		"""
		This method returns the top N for each item or citations
		The parameter n represents # of items or citations to return in descending order
		"""
		return self.similarity_mat.loc[item].sort_values(ascending=False)[:n].iloc[1:]


	def recommendations(self, index, n=10, k=20):
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
		unknowns = set()
		already_known = set(self.df.loc[index][self.df.loc[index][self.column_names] > 0].index.values)
		for item in already_known:
			unknowns.update(self.__top__(n=k, item=item).index.values)

		unknowns = unknowns - already_known
		suggestions = pd.DataFrame(np.zeros((len(unknowns))), index = unknowns, columns=['score'])

		print('Computing recommendations for : ' + index)
		for unknown in tqdm(unknowns):
			temp = 0
			for known in already_known:
				temp += self.similarity_mat.loc[unknown][known]
			suggestions.loc[unknown] = temp

		 suggestions = suggestions.sort_values(by=['score'], ascending=False)
		 return suggestions.index.values[:n], suggestions['score'][:n].values




