# from tqdm import tqdm
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

