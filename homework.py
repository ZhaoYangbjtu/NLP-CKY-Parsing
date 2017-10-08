
from tree import Tree, Node
from collections import defaultdict
from bigfloat import bigfloat
import math
import time
import sys
import matplotlib.pyplot as plt

rules = {}
probability = {}
probability_rules = {}
terminal = {}
non_terminals = {}
transistions = []

x_axis = []
y_axis = []

score = defaultdict(lambda:defaultdict(lambda:defaultdict(float)))
back = defaultdict(lambda:defaultdict(lambda:defaultdict(tuple)))
	
def plotgraph(x,y):
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
			if split_key[2] in terminal:
				terminal[split_key[2]] += 1
			else:
				terminal[split_key[2]] = 1

def generate_rule(root):

	if root is not None:
		
		#left child 
		if len(root.children) == 1:
			generate_rule(root.children[0])

		#right child
		if len(root.children) > 1:
			generate_rule(root.children[0])
			generate_rule(root.children[1])

		#dont add rules that are begining in leaves.
		if len (root.children) != 0:

			str = ""
			if len(root.children) == 1:

				str = root.label + '$' + root.parent.label + ' -> '
				non_terminals[str] = str
				
				for child in root.children:
					#create the rule 
					str += child.label + ' '
					
					#add the child non terminals to the count (N)
					if child.label in probability:
						probability[child.label] += 1
					else:
						probability[child.label] = 1

			elif len(root.children) == 2:

				#generate the rule 
				if root.parent is not None:
					str = root.label + '$' + root.parent.label + ' -> '
				else:
					str = root.label + ' -> '
				
				#for root nodes
				non_terminals[str] = str
				
				for child in root.children:
					str += child.label + '$' + root.label + ' '

					#for each child nodes	
					non_terminals[(child.label+ '$' + root.label)] = child.label+ '$' + root.label

					if (child.label+ '$' + root.label) in probability:
						probability[child.label+ '$' + root.label] += 1
					else:
						probability[child.label+ '$' + root.label] = 1

			#remove the last space.
			str = str.strip()

			if str in rules:
				rules[str] += 1
			else:
				rules[str] = 1
 	else:
 		return


def calculate_terminals_cky(n,all_words):
	i = 0
	while i < (n):
		for A in non_terminals:
			rule = A + " -> "+all_words[i]
			if rule in probability_rules:
				score[i][i+1][A] = probability_rules[rule]
				back[i][i+1][A] = (i, all_words[i], '', A)
		i += 1			

def calculate_non_terminals_cky(n):
	span = 2 
	while span < n+1:
		for begin in range(n-span+1):
			end = begin+span
			for split in range(begin+1,end):
				for rule in transistions:
					if rule[0] is not None:
						A = rule[0]
					if rule[1] is not None:
						B = rule[1]
					if rule[2] is not None:
						C = rule[2]
					rule2 = A+" -> "+B+" "+C
					prob =  (score[begin][split][B]) * (score[split][end][C])  * probability_rules[rule2]
					
					if prob > score[begin][end][A]:
						score[begin][end][A] = prob
						back[begin][end][A] = (split,B,C,A)
		span +=1 
		

def parser(line):
	
	newLine = replace_word_by_unk(line)
	all_words = newLine.split(' ')
	n = len(all_words)

	no_of_non_terms = len(non_terminals)
	
	calculate_terminals_cky(n,all_words)
	calculate_non_terminals_cky(n)
	
	t = Tree(Node('TOP',[]))
	build_tree(back[0][n]['TOP'],0,n,t.root)
	
	return t	


def build_tree(node,begin,end,root):
	
	left_tnode = Node(node[1],[])
	right_tnode = Node(node[2],[])

	root.append_child(left_tnode)
	root.append_child(right_tnode)
	if node[2]=='':
		return
	left = back[begin][node[0]][node[1]]
	build_tree(left,begin,node[0],left_tnode)

	right = back[node[0]][end][node[2]]
	build_tree(right,node[0],end,right_tnode)


#open file and generate rules
file = open (sys.argv[1])
for line in file:
	tree_parsed = Tree.from_str(line)
	generate_rule(tree_parsed.root)


print len(non_terminals)
print len(terminal)

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
dev_file = open (sys.argv[2])
for line in dev_file:
	line = line.strip('\n')
	
	x_axis.append(math.log10(len(line.split(' '))))
	parse_tree = ""
	try:
		start = time.clock()

		score = defaultdict(lambda:defaultdict(lambda:defaultdict(float)))
		back = defaultdict(lambda:defaultdict(lambda:defaultdict(tuple)))
		parse_tree = parser(line)
		
		duration = time.clock() - start
		
		y_axis.append(math.log10(duration * 1000))
		print parse_tree
	except IndexError:
		duration = time.clock() - start
		y_axis.append(math.log10(duration * 1000))
		print ""





