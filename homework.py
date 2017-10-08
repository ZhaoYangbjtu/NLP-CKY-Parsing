
from tree import Tree, Node
from collections import defaultdict
from bigfloat import bigfloat
import math
import time
import sys


rules = {}
probability = {}
probability_rules = {}
terminal = {}
non_terminals = {}
transistions = []

x_axis = []
y_axis = []


import matplotlib.pyplot as plt
 
def plotgraph(x,y):
	# # x axis values
	# x = demogrammar.plot_x
	# # corresponding y axis values
	# y = demogrammar.plot_y
	 
	# plotting the points 
	# naming the x axis
	plt.xlabel('x - axis')
	# naming the y axis
	plt.ylabel('y - axis')
	 
	# giving a title to my graph
	plt.title('Parse time vs Sentence length!')
	plt.scatter(x, y)
	 
	# function to show the plot
	plt.show()	


def generate_transisition():
	for key in probability_rules:
		tokens = key.split(' ')
		
		if len(tokens) == 4:
			A = tokens[0]
			B = tokens[2]
			C = tokens[3]
			transistion = [A,B,C]
			transistions.append(transistion)	

def replace_word_by_unk(line):
	#replace <unk>
	modified_line = ""
	words = line.split(' ')
	for word in words:
		if word.strip() not in terminal:
			modified_line += "<unk>"
		else:
			modified_line += word
		modified_line += " "

	modified_line = modified_line.strip()
	return modified_line		


def generate_terminal():
	for key in rules:
		split_key = key.split(' ')
		if len(split_key) == 3:
			terminal[split_key[2]] = split_key[2]

def generate_rule(root):

	if root is not None:

		str = root.label + ' -> '
		for child in root.children:
			str += child.label + ' '

		#remove the last space.
		str = str.strip()
		#dont add rules that are begining in leaves.
		if len (root.children) != 0:

			non_terminals[root.label] = root.label

			if root.label in probability:
				probability[root.label] += 1
			else:
				probability[root.label] = 1

			if str in rules:
				rules[str] += 1
			else:
				rules[str] = 1

		#left child 
		if len(root.children) == 1:
			generate_rule(root.children[0])

		#right child
		if len(root.children) > 1:
			generate_rule(root.children[0])
			generate_rule(root.children[1])
 	else:
 		return

def parser(line):
	
	newLine = replace_word_by_unk(line)
	all_words = newLine.split(' ')
	n = len(all_words)

	
	no_of_non_terms = len(non_terminals)
	score = defaultdict(lambda:defaultdict(lambda:defaultdict(float)))
	back = defaultdict(lambda:defaultdict(lambda:defaultdict(tuple)))
	
	print score
	for i in range(n):
		for A in non_terminals:
			rule = A + " -> "+all_words[i]
			if rule in probability_rules:
				score[i][i+1][A] = probability_rules[rule]
				back[i][i+1][A] = (i, all_words[i], '', A)
	for span in range(2,n+1):
		for begin in range(n-span+1):
			end = begin+span
			for split in range(begin+1,end):
				for rule in transistions:
					A = rule[0]
					B = rule[1]
					C = rule[2]
					rule2 = A+" -> "+B+" "+C
					prob =  (score[begin][split][B]) * (score[split][end][C])  * probability_rules[rule2]
					
					if prob > score[begin][end][A]:
						score[begin][end][A] = prob
						back[begin][end][A] = (split,B,C,A)
	
	t = Tree(Node('TOP',[]))
	build_tree(back[0][n]['TOP'],back,0,n,t.root)
	


	return t	


def build_tree(node,back,begin,end,root):
	
	left_tnode = Node(node[1],[])
	right_tnode = Node(node[2],[])

	root.append_child(left_tnode)
	root.append_child(right_tnode)
	if node[2]=='':
		return
	left = back[begin][node[0]][node[1]]
	build_tree(left,back,begin,node[0],left_tnode)

	right = back[node[0]][end][node[2]]
	build_tree(right,back,node[0],end,right_tnode)


#open file and generate rules
file = open ('train.trees.pre.unk')
for line in file:
	tree_parsed = Tree.from_str(line)
	generate_rule(tree_parsed.root)


#identify the max rule count 
# adnd compute the probability of each rule 
max = 0
for key in rules:
	probability_rules[key] =  (rules[key]  * 1.0) / (probability[key.split(' ')[0]])
	if max < rules[key]:
		max = rules[key]

#genereate all the terminals.
generate_terminal()

#generate all the transistions.
generate_transisition()

#generate on dev data the parse tree.
dev_file = open ('dev.strings')
for line in dev_file:
	line = line.strip('\n')
	
	x_axis.append(math.log10(len(line.split(' '))))
	parse_tree = ""
	try:
		start = time.clock()
		parse_tree = parser(line)
		duration = time.clock() - start
		y_axis.append(math.log10(duration * 1000))
		print parse_tree
	except IndexError:
		duration = time.clock() - start
		y_axis.append(math.log10(duration * 1000))
		print ""





