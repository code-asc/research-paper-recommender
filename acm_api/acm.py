import json
import requests
import re
from bs4 import BeautifulSoup


# Url to get citedBy
# example https://dl.acm.org/action/ajaxShowCitedBy?doi=10.5555%2F2387880.2387905

def acm_meta(doi):
	data = {}
	page = requests.get('https://dl.acm.org/doi/' + doi).text
	parser = BeautifulSoup(page, features='html.parser')
	refs_ = parser.find('ol', {'class': 'references__list'})

	refs = {} # all the references in the paper
	for ref in refs_:
		temp = ref.find('span', {'class', 'references__note'})

		p_name = temp.text.replace('"', '') # name of the paper
		src_ = {} # different sources of the paper

		for src in temp.find_all('span', {'class', 'references__suffix'}):
			src_[src.a.img.get('alt')] = src.a.get('href')
		refs[p_name] = src_

	data['references'] = refs

	data['abstract'] = parser.find('div', {'class': 'abstractSection'}).p.text

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