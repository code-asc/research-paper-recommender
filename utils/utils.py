from utils.dummy import get_dummy_info
from acm_api.acm import acm_meta
from tqdm.notebook import tqdm
import requests
import json


def get_paper_citation_pairs(df, dir_='citation-web/pair-way/', out_file='citation-pairs.txt'):
	"""
	This method is used to extract the citation pairs from the dataframe.
	It return the path of the text file "citation_pairs.txt"
	"""
	indexs = df.index.values
	columns = df.columns.values
	path = dir_ + out_file
	with open(path, 'wt') as f:
		print('writing citation pairs....')
		for index in tqdm(indexs):
			for column in columns:
				if df.loc[index][column] == 1:
					f.write(index + ',' + column + '\n')
	return path
	

def get_citation_doi(references):
	"""
	This method is used to extract the doi's
	from the reference list

	We are looking to get the citations that
	exist in acm dl

	Note: Some papers may not have doi. In such 
	scenario, we completely ignore the reference
	"""
	doi = []
	if type(references).__name__ == 'str':
		references = json.loads(references)
	else:
		if not type(references).__name__ == 'dict':
			return []

	all_ref = references.get('references', None)
	
	if all_ref:
		print("extracting citation's doi....")
		for key in tqdm(all_ref.keys()):
			temp = all_ref[key].get('Digital Library', None)
			if temp:
				doi.append(temp.replace('/doi/', '').strip())
	return doi


def get_cited_by_doi(references):
	"""
	This method is used to extract all the doi from 
	the cited by list that exist in acm dl
	"""
	doi = []
	if type(references).__name__ == 'str':
		references = json.loads(references)
	else:
		if not type(references).__name__ == 'dict':
			return []

	all_cited_by = references.get('cited_by', None)

	if all_cited_by:
		print("extracting cited_by doi....")
		for key in tqdm(all_cited_by.keys()):
			temp = all_cited_by[key].get('Digital Library', None)
			if temp:
				doi.append(temp.replace('/doi/', '').strip())
	return doi



def get_fully_connected_network(overall, cited_by_doi, acm=True):
	"""
	This method is used to complete all the edges between 
	base graph for HITS algorithm. 

	Parameter:

	overall is dict of both query set + cited by papers as
	keys. For each key, the values are the list of citations.
	Our goal is to find the edges between cited by papers and 
	query set's citations

	cited_by_doi are the list of doi that cite the papers
	in query set
	"""
	overall_copy = overall.copy()
	all_possible_papers = set(overall.keys())
	citations = set()

	for key in overall.keys():
		all_possible_papers.update(overall[key])
		citations.update(overall[key])

	citations.update(cited_by_doi)

	for doi in tqdm(citations):

		if acm:
			papers_doi_cite = acm_meta(doi)
		else:
			papers_doi_cite = get_dummy_info(doi)

		if papers_doi_cite:
			for paper in papers_doi_cite:
				if paper in all_possible_papers:

					if not overall_copy.get(doi, False):
						overall_copy[doi] = [paper]
					else:
						if paper not in overall_copy[doi]:
							overall_copy[doi].append(paper)

	return overall_copy

