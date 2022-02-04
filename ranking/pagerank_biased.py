import os
import numpy as np


class Node:
	def __init__(self):
		self.vertex = None
		self.meta = None
		self.score = 1.0
		self.out_link = set()
		self.in_link = set()



class Ranking:
	"""
	This class is used to create a dictionary of nodes
	Each node class has the following data
	a) vertex
	b) meta
	c) out_link
	d) in_link

	For better understanding, please refer the following paper

	Algorithms for estimating relative importance in networks
	
	"""
	def __init__(self, file_, beta=0.5, prior_bias_node=[], iterations=100):
		self.file_name = file_
		self.data = self.__create__()
		self.prior_bias_node = self.__prior__(prior_bias_node)
		self.beta = beta
		self.iterations = iterations


	def __prior__(self, biased_nodes):
		"""
		This method is used to assign the prior proabilites
		for the root nodes.
		"""
		temp = {}
		for key in self.data.keys():
			if key in biased_nodes:
				temp[key] = 1.0/float(len(biased_nodes))
			else:
				temp[key] = 0.0

		return temp


	def __create__(self):
		node_dict = {}
		with open(self.file_name) as f:
			for line in f:
				from_, to_ = line.strip().split(',')

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
			for key in self.data.keys():
				self.data[key].score = (self.beta * self.prior_bias_node[key]) + (1.0 - self.beta) * \
									sum([(self.data[in_key].score)/float(len(self.data[in_key].out_link)) for in_key in self.data[key].in_link ])

	def scores(self, normalize=False):
		scores = {}
		self.__calculate__()

		for key in self.data.keys():
			scores[key] = self.data[key].score

		if normalize:
			total_score = sum([scores[key] for key in scores.keys()])

			for key in scores.keys():
				scores[key] /= total_score

		return scores
