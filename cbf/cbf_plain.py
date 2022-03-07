from tqdm import tqdm
# import tqdm.notebook as tqdm
import pandas as pd
import numpy as np
from acm_api.acm import download_search_acm
import json
import sqlite3
from wp.bm25 import bm25_score

class CBF:

	def __init__(self, search_query, active_paper_path='doi/doi.txt'):
		self.search_query = search_query
		self.active_paper_path = active_paper_path
		_, _, _, self.dois = download_search_acm(search_query)


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

	def __meta_2_doc__(self, meta):
		"""
		This method is used to produce the document/string out
		of a meta data
		"""
		str_ = meta.get('title', '') + ' ' + meta.get('abstract', '')
		return str_

	def __active__(self):
		"""
		This method is used to return the active paper
		string i.e., title + abstract
		"""
		dois = []
		temp = None

		with open(self.active_paper_path, 'r') as f:
			temp = f.readlines()

		for line in temp:
			dois.append(line.strip())

		full_str = ''

		for doi in dois:
			full_str += self.__meta_2_doc__(self.__searchDB__(doi)) + ' '

		return full_str, dois


	def __recommend__(self):
		"""
		This method is used to provide the recommendations
		for the exisiting doi file. It does not limit on
		the final output

		Do not use it for regular predictions. It is used 
		in the subgraphing method
		"""
		scores = None
		docs = {}
		active_paper, active_dois = self.__active__()

		for doi in self.dois:
			if doi not in active_dois:
				docs[doi] = self.__meta_2_doc__(self.__searchDB__(doi))

		scores = bm25_score(active_paper, docs)
		return scores, active_dois

	def recommend(self):
		"""
		This method is used to provide the recommendations
		for the exisiting doi file. It does not limit on
		the final output
		"""
		scores = None
		docs = {}
		active_paper, active_dois = self.__active__()

		for doi in self.dois:
			if doi not in active_dois:
				docs[doi] = self.__meta_2_doc__(self.__searchDB__(doi))

		scores = bm25_score(active_paper, docs)
		return scores

	
