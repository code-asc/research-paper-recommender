import os
import numpy as np

class Node:
	"""
	This class is used to create a dictionary of nodes
	Each node class has the following data
	a) vertex
	b) meta
	c) out_link
	d) in_link
	"""
	def __init__(self):
		self.vertex = None
		self.meta = None
		self.score = 1.0
		self.out_link = set()
		self.in_link = set()

 
class Ranking:
	"""
	For better understanding of the concept use the following link:

	https://www.youtube.com/watch?v=-kiKUYM9Qq8
	"""
	def __init__(self, file_, root_nodes=[], iterations=100, 
					default_temp_file_path="temp/pair-way/temp-hits-base-node.txt"):

		self.file_name = file_
		self.default_temp_file_path  = default_temp_file_path
		self.root_nodes = set(root_nodes)
		self.potential_hub_nodes = set(self.__potential_hubs__()) -	self.root_nodes
		self.__base__()

		self.data = self.__create__()

		self.auth_score = self.__assign_auth_score__()

		self.iterations = iterations

	def __assign_auth_score__(self):
		"""
		This method is used to assign the authorative score to
		all the nodes in the base network. Default we are assigning
		value 1 to all the nodes in the base network
		"""
		temp_dict = {}
		for key in self.data.keys():
			temp_dict[key] = 1.0 

		return temp_dict


	def __base__(self):
		"""
		This method is used to create a base nodes for
		a given root nodes

		What is root nodes?
		These are the most relevant nodes for a given user
		query

		In our case, these are the query list of papers

		To form the base nodes, we find all the nodes or
		papers that has out-going edges to the root nodes
		and relation between them.

		"""
		required_nodes = set(self.root_nodes)
		required_nodes.update(self.potential_hub_nodes)

		base_network = []

		with open(self.file_name) as f:
			for line in f:
				from_, to_ = line.strip().replace('\n', '').split(',')

				if (from_ in required_nodes) and (to_ in required_nodes):
					base_network.append(line)

		with open(self.default_temp_file_path, 'w') as f:
			for edge in base_network:
				f.write(edge)

		
	def __potential_hubs__(self):
		"""
		This method is used to find all the pages that link to the 
		nodes/papers in the root nodes. These are called potential hubs
		"""
		potential_hub_nodes = []
		with open(self.file_name, 'r') as f:
			for line in f:
				from_, to_ = line.strip().replace('\n', '').split(',')

				if to_ in self.root_nodes:
					potential_hub_nodes.append(from_)

		return potential_hub_nodes 



	def __create__(self):
		""" 
		This method is used to create a graph and
		return the dict with key as node name and
		value as the Node class
		"""
		node_dict = {}
		with open(self.default_temp_file_path) as f:
			for line in f:
				from_, to_ = line.replace('\n', '').strip().split(',')

				if not node_dict.get(from_, False):
					temp = Node()
					temp.vertex = from_
					node_dict[from_] = temp


				if not node_dict.get(to_, False):
					temp = Node()
					temp.vertex = to_
					node_dict[to_] = temp


				from_node = node_dict[from_]
				to_node = node_dict[to_]

				from_node.out_link.add(to_)
				to_node.in_link.add(from_)

		return node_dict 

	def __calculate__(self):
		for _ in range(self.iterations):
			temp = {}
			total = 0.0
			for key in self.data.keys():
				temp_val = sum([self.auth_score[i] for i in self.data[key].in_link])
				temp[key] = temp_val
				total += temp_val

			# Normalize the values 
			for key in self.data.keys():
				if total > 0:
					temp[key] = temp[key]/total
				else: 
					temp[key] = 0.0

			self.auth_score = temp.copy()

	def scores(self):
		scores = {}
		self.__calculate__()

		for key in self.data.keys():
			scores[key] = self.auth_score[key]

		return scores

