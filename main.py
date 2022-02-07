import sqlite3
from acm_api.acm import acm_meta


doi_list = []

if __name__ == '__main__':
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

	for doi in doi_list:
		cursor = con.execute("SELECT * FROM PAPERS WHERE doi=" + doi + ";")

		if cursor.fetchall() == []:
			temp = acm_meta(doi)
			con.execute("INSERT INTO PAPERS (doi, data) VALUES (" + doi + ", " + str(temp) + ")")

	con.commit()
	con.close()