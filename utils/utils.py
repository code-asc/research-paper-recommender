from tqdm import tqdm
import json

def get_citation_doi(references):
	"""
	This method is used to extract the doi's
	from the reference list

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


