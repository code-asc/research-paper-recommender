from tqdm import tqdm
# import tqdm.notebook as tqdm
import pandas as pd
import numpy as np
from acm_api.acm import download_search_acm
import json
import sqlite3
from wp.bm25 import bm25_score
from .cbf_plain import CBF
import utils.utils as utils
from cf.cf_full_hits import CFUH

class CBFH:

	def __init__(self, search_query, active_paper_path='doi/doi.txt'):
		self.path = 'citation-web/'
		self.full_matrix_file_name = 'matrix-way/citation-full-cbf-matrix.csv'
		self.pair_file_name = 'pair-way/citation-full-cbf-pairs.txt'

		self.search_query = search_query
		self.active_paper_path = active_paper_path
		print('init the CBF....')
		self.cbf_plain = CBF(search_query=search_query, 
							active_paper_path=active_paper_path)
		self.scores, self.active_dois = self.cbf_plain.__recommend__()

	def __searchDB__(self, doi):
		"""
		This method is used to retrive the doi meta info
		from the db

		We assume that the doi record is already in the
		database
		"""
		con = sqlite3.connect('data.db')
		cur = con.cursor()
		cursor = con.execute("SELECT * FROM PAPERS WHERE doi=?;", (doi,))
		fetch_data = cursor.fetchone()
		return json.loads(fetch_data[1])


	def __doi__(self, dois):
		"""
		This method is used to retrive the cited by
		and reference data for each doi 

		Return

		data is the collect of all references for each doi
		data_citedby is the collection of all the dois that site the paper
		"""
		data = {}
		data_citedby = {}

		for doi in dois:
			temp = self.__searchDB__(doi)
			data[doi] = utils.get_citation_doi(temp)
			
			for citedby_doi in utils.get_cited_by_doi(temp):
				if not data_citedby.get(citedby_doi, False):
					data_citedby[citedby_doi] = [doi]
				else:
					data_citedby[citedby_doi].append(doi)
		return data, data_citedby


	def __rmatrix__(self, data, data_citedby):
		citation_set = set()
		citation_set_with_cited_by = set()

		for key in data.keys():
			citation_set.update(data[key])
			citation_set_with_cited_by.update(data[key])

		citation_set_with_cited_by.update(data.keys())
		index_ = data.keys()
		index_with_citedby = set(data.keys())
		index_with_citedby.update(data_citedby.keys())
		index_with_citedby = list(index_with_citedby)
		df = pd.DataFrame(np.zeros((len(index_), len(citation_set))),\
					index=index_, columns=citation_set)

		df_with_cited_by = pd.DataFrame(np.zeros((len(index_with_citedby),\
					len(citation_set_with_cited_by))), \
                    index=index_with_citedby, \
                    columns=citation_set_with_cited_by)
		for i in index_:
			for j in citation_set:
				if j in data[i]:
					df.loc[i][j] = 1

		overall_ = {**data_citedby, **data}
		overall = utils.get_fully_connected_network(overall_, data_citedby.keys(), acm=False)
		for i in index_with_citedby:
			for j in citation_set_with_cited_by:
				if j in overall[i]:
					df_with_cited_by.loc[i][j] = 1

		df_with_cited_by.to_csv(self.path + self.full_matrix_file_name)



	def recommend(self):
		"""
		This method is used to provide the recommendations
		for the exisiting doi file. It does not limit on
		the final output
		"""
		union_dois = set(self.active_dois)
		union_dois.update(list(self.scores.keys())[:200])

		data, data_citedby = self.__doi__(union_dois)
		self.__rmatrix__(data, data_citedby)
		obj = CFUH(default_path=self.path, file_=self.full_matrix_file_name, \
				file_pair=self.pair_file_name, root_node_indexes=union_dois)

		temp = {}
		for doi in union_dois:
			temp[doi] = obj.recommend(doi)

		return temp


	
