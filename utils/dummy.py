import random
import sqlite3
import json

def dummy_data(dummy_paper=200):
	"""
	This method is used to generate the synthetic dataset
	Parameters:
	dummy_paper : # of number to be paper(doi) to be 
	generated. Each paper will also be assigned with
	fake citation details

	Note: All the data is outputted to fake.db data file
	"""
	con = sqlite3.connect('fake.db')
	cur = con.cursor()

	is_table_exists = cur.execute("""SELECT name FROM sqlite_master 
							WHERE type='table' AND name='PAPERS'; """).fetchall()

	if is_table_exists == []:
		cur.execute("""CREATE TABLE PAPERS (doi TEXT, data TEXT);""")

	dummy_citations = set()
	for paper in range(1, dummy_paper):
		temp = {}
		citations = random.sample(range(dummy_paper, dummy_paper+100), 50)

		for citation in citations:
			temp[str(citation)] = {"Google Scholar": str(citation), "Digital Library": "/doi/"+str(citation)}

		temp_reference = {}
		temp_reference["references"] = temp
		insert_statement = 'INSERT INTO PAPERS(doi, data) VALUES(?, ?)'
		con.execute(insert_statement, (str(paper), str(json.dumps(temp_reference))))

	con.commit()
	con.close()


def dummy_doi(num_of_doi, default_path='doi/', default_file='doi.txt'):
	"""
	This method is used to generate fake doi and store the data in the
	specified file
	"""
	with open(default_path+default_file, 'wt') as f:
		for i in range(num_of_doi):
			f.write(str(i) + '\n')

