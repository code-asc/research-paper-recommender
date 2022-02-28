import random
import sqlite3
import json

def dummy_data(dummy_paper=200, size=100):
	"""
	This method is used to generate the synthetic dataset
	Parameters:
	dummy_paper : Starting range (doi) of the citation pages.
	It is better put it higher than the dooi range of root or
	query set papers. Each paper in the query set will also be 
	assigned with fake citation doi. The # of citations can be
	specified in parameter size

	Note: All the data is outputted to fake.db data file
	"""

	random_citedby_doi = {}
	for i in random.sample(range(dummy_paper+200, dummy_paper + 300), size):
		random_citedby_doi[i] = set()


	con = sqlite3.connect('fake.db')
	cur = con.cursor()
	insert_statement = 'INSERT INTO PAPERS(doi, data) VALUES(?, ?)'

	is_table_exists = cur.execute("""SELECT name FROM sqlite_master 
							WHERE type='table' AND name='PAPERS'; """).fetchall()

	if is_table_exists == []:
		cur.execute("""CREATE TABLE PAPERS (doi TEXT, data TEXT);""")

	dummy_citations = set()

	for paper in range(1, dummy_paper):
		temp = {}
		temp_ = {}
		citations = random.sample(range(dummy_paper, dummy_paper+100), size)
		cited_by = random.sample(random_citedby_doi.keys(), int(size/2))

		for citation in citations:
			temp[str(citation)] = {"Google Scholar": str(citation), "Digital Library": "/doi/"+str(citation)}
		
		for citation_ in cited_by:

			random_citedby_doi[citation_].update([paper])
			temp_[str(citation_)] = {"Digital Library": "/doi/"+str(citation_), "Others": str(citation_)}

		temp_reference = {}
		temp_reference["references"] = temp
		temp_reference["cited_by"] = temp_

		con.execute(insert_statement, (str(paper), str(json.dumps(temp_reference))))

	for key in random_citedby_doi.keys():
		temp = {}
		for doi in random_citedby_doi[key]:
			temp[str(doi)] = {"Google Scholar": str(doi), "Digital Library": "/doi/"+str(doi)}

		temp_reference = {}
		temp_reference["references"] = temp
		con.execute(insert_statement, (str(key), str(json.dumps(temp_reference))))

	con.commit()
	con.close()


def get_dummy_info(doi):
	"""
	This paper is used to retrive the info such as 'references' and 
	'cited by' for a doi
	"""
	con = sqlite3.connect('fake.db')
	cur = con.cursor()
	cursor = con.execute("SELECT * FROM PAPERS WHERE doi=?;", (doi,))
	fetch_data = cursor.fetchone()

	if fetch_data is None:
		return None

	return fetch_data[1]


def dummy_doi(num_of_doi, default_path='doi/', default_file='doi.txt'):
	"""
	This method is used to generate fake doi and store the data in the
	specified file
	"""
	with open(default_path+default_file, 'wt') as f:
		for i in range(num_of_doi):
			f.write(str(i) + '\n')

