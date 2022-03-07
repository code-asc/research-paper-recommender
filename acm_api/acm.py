import json
import requests
import re
from bs4 import BeautifulSoup
import sqlite3
from tqdm.notebook import tqdm
import utils.utils as utils


# Url to get citedBy
# example https://dl.acm.org/action/ajaxShowCitedBy?doi=10.5555%2F2387880.2387905

def acm_meta(doi):
	data = {}
	print('doi is ', doi)
	page = requests.get('https://dl.acm.org/doi/' + doi).text

	parser = BeautifulSoup(page, features='html.parser')

	data['title'] = parser.find('h1', {'class': 'citation__title'}).text

	refs_ = parser.find('ol', {'class': 'references__list'})

	refs = {} # all the references in the paper

	try:
		for ref in refs_:
			temp = ref.find('span', {'class', 'references__note'})

			p_name = temp.text.replace('"', '') # name of the paper
			src_ = {} # different sources of the paper

			for src in temp.find_all('span', {'class', 'references__suffix'}):
				src_[src.a.img.get('alt')] = src.a.get('href')
			refs[p_name] = src_
	except Exception as e:
		None

	data['references'] = refs

	try:
		data['abstract'] = parser.find('div', {'class': 'abstractSection'}).p.text
	except Exception as e:
		None

	# Code for citations
	cited_by = requests.get('https://dl.acm.org/action/ajaxShowCitedBy?doi=' + doi).text
	c_parser = BeautifulSoup(cited_by, features='html.parser')
	all_citations = {}
	for each_cite in c_parser.findAll('li', {'class': 'references__item'}):
		try:
			if re.search("^(https://doi.org/){1}.*", each_cite.p.a.get('href')):
				all_citations[each_cite.find('span', {'class':'references__article-title'}).text] = {'Digital Library': each_cite.p.a.get('href').replace('https://doi.org/', '')}
			else:
				all_citations[each_cite.find('span', {'class':'references__article-title'}).text] = {'Others' : each_cite.p.a.get('href')}
		except Exception as e:
			None

	data['cited_by'] = all_citations

	return json.dumps(data, indent=2)



def __get_search_list__(query):
	"""
	This method is used to retrive the list of doi for
	a query from a acm digital library after the search

	Example of query below:
	generative+adversarial+networks+audio+and+video

	We are retriving upto 300 records in the best case
	"""
	temp = []
	print("downloading paper meta data....")
	page = requests.get('https://dl.acm.org/action/doSearch?AllField='+query+'&startPage=0&pageSize=300').text
	parser = BeautifulSoup(page, features='html.parser')
	refs_ = parser.findAll('a', {'class': 'issue-item__doi dot-separator'})

	for a in refs_:
		temp.append(a['href'])

	return temp


def download_search_acm(query):
	"""
	This method is used to download the set of dois for 
	the seach query. First, it will check if doi is already
	in the db or not. Incase of the doi absence in the db, we
	download and save it in db

	Example of query below:
	generative+adversarial+networks+audio+and+video

	"""
	dois = __get_search_list__(query)
	doi_list, data, data_citedby = acm_db_init(dois, has_doi_set_ready=True)
	return doi_list, data, data_citedby, [doi.replace('https://doi.org/','').strip() for doi in dois]

	


def acm_db_init(dois=None, has_doi_set_ready=False):
	"""
	This method is used to process the doi files.
	It should be the starting point of the code
	"""
	doi_list = []
	data = {}
	data_citedby = {}

	# reading the input file with doi of papers
	if not has_doi_set_ready:
		with open('doi/doi.txt', 'r') as doi_file:
		    lines = doi_file.readlines()
		    
		for line in lines:
		    doi_list.append(line.strip())

	else:
		
		doi_list = [doi.replace('https://doi.org/', '').strip() for doi in dois]
	    
	con = sqlite3.connect('data.db')
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
	    	data[doi] = utils.get_citation_doi(temp)
	    	con.commit()
	    	print("added to database....")
	        
	    else:
	        data[doi] = utils.get_citation_doi(fetch_data[1])
	        
	        for citedby_doi in utils.get_cited_by_doi(fetch_data[1]):
	            if not data_citedby.get(citedby_doi, False):
	                data_citedby[citedby_doi] = [doi]
	            else:
	                # A paper can cite my papers in the query set
	                data_citedby[citedby_doi].append(doi)
	        
	
	con.close()

	return doi_list, data, data_citedby

