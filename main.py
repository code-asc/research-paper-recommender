import sqlite3
import numpy as np
import pandas as pd
from tqdm import tqdm
from utils.utils import get_citation_doi
from utils.utils import get_paper_citation_pairs
from acm_api.acm import acm_meta




if __name__ == '__main__':
	doi_list = []
	data = {}

	# reading the input file with doi of papers
	with open('doi/doi.txt', 'r') as doi_file:
		lines = doi_file.readlines()

	for line in lines:
		doi_list.append(line.strip())

	con = sqlite3.connect('papers.db')
	cur = con.cursor()

	is_table_exists = cur.execute(
		"""
		SELECT name FROM sqlite_master WHERE type='table'
		AND name='PAPERS'; """).fetchall()

	if is_table_exists == []:
		cur.execute(""" 
			CREATE TABLE PAPERS (doi TEXT, data TEXT);
		""")

	print('processing doi....')
	for doi in tqdm(doi_list):
		cursor = con.execute("SELECT * FROM PAPERS WHERE doi=?;", (doi,))
		fetch_data = cursor.fetchone()
		if fetch_data is None:
			temp = acm_meta(doi)
			insert_statement = 'INSERT INTO PAPERS(doi, data) VALUES(?, ?)'
			
			con.execute(insert_statement, (doi, str(temp)))

			data[doi] = get_citation_doi(temp)
		else:
			data[doi] = get_citation_doi(fetch_data[1])

	con.commit()
	con.close()

	########################################
	# code for creating the rating matrix
	citation_set = set()

	for key in data.keys():
		citation_set.update(data[key])
	
	index_ = data.keys()

	df = pd.DataFrame(np.zeros((len(index_), len(citation_set))), index=index_, columns=citation_set)

	for i in index_:
		for j in citation_set:
			if j in data[i]:
				df.loc[i][j] = 1

	df.to_csv('citation-web/matrix-way/citation-matrix.csv')
	########################################

	########################################
	# creating the citation pairs
	citation_pair_path = get_paper_citation_pairs(df, 'citation-pairs.txt')
	########################################