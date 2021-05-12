
from time import sleep
import math

'''
AI maze solver.
'''
START = (0, 0)
FINISH = (9, 0)

class Vertex:
	'''
	Vertex class: base nodes for the graph.
	'''
	def __init__(self, *args, **kwargs):
		self.src = None
		self.dest = None
		self.edges = []

class Graph:
	'''
	Graph class to add edges to nodes
	'''
	nodes = {}
	def __init__(self, src, *args, **kwargs):
		self.v = Vertex()
		self.src = src
		self.nodes[self.src] = []
		self.v.src = self.src
		self.dest = None
		self.last_node = None
	
	def add_edge(self, src, dest):
		if dest not in self.nodes:
			return
		self.dest = dest
		self.v.dest = self.dest
		self.nodes[src].append(self.dest)
		self.v.edges.append(self.dest)
		
# TODO: implement a maze imaging system to test on more complex mazes.
maze = [
	[0,0,1,0,0,0,0],
	[1,0,1,0,1,1,0], 
	[1,0,1,0,0,1,0],
	[1,0,0,1,0,1,0],
	[1,1,0,1,0,1,0],
	[1,0,0,0,0,1,0],
	[1,1,0,1,1,0,0],
	[1,1,1,1,1,0,1],
	[1,1,0,1,1,0,1],
	[0,0,0,0,0,0,1],
	[1,1,1,1,1,1,1]
	]
	
v = '''
EEEE N   N DDD
E    NN  N D  D
EE   N N N D   D
E    N  NN D  D
EEEE N   N DDD
'''
	
class Runner (Graph):
	'''
	Sets the start and finish coords.
	TODO: automate the start/finish coord creation
	'''
	start = START
	finish = FINISH
	path=[]
	maze = maze
	def __init__(self):
		self.pos = self.start
		self.path.append(self.start)
		#self.map_maze()
		self.paths_list = []
	
	def map_maze(self):
		'''
		Creates nodes and edges for the graph from the maze array.
		nodes named by tuple of coords for maze map.
		'''
		for iy, y in enumerate(self.maze):
			for ix, x in enumerate(y):
				if x == self.maze[self.start[0]][self.start[1]]:
					Graph.__init__(self, (iy, ix))
		for node in self.nodes:
			y, x = node
			for i in [-1, 1]:
				try:
					self.add_edge(node, (y+i, x))
					self.add_edge(node, (y, x+i))
				except KeyError:
					pass
		self.run_maze()
		
	def run_maze(self):
		'''
		Run the maze, changes the position character representation.
		'''
		self.path = self.find_path(self.nodes, self.start, self.finish)
		for p in self.path:
			self.pos = p
			y, x = p
			self.maze[y][x] = 'O'
			self.viz()
			self.maze[y][x] = '•'
		if self.pos == self.finish:
			print(v)
			return self.path
		
	def find_path(self, maze_nodes, start, end, path=[]):
		path = path + [start]
		if start == end:
			return path
		if start not in maze_nodes:
			return None
		for node in maze_nodes[start]:
			if node not in path:
				newpath = self.find_path(maze_nodes, node, end, path)
				if newpath:
					return newpath
		return None	
		
	def viz(self):
		line_end = len(self.maze[-1]) - 1
		print('_'*(line_end + 5))
		for iy, y in enumerate(self.maze):
			print('||', end='')
			for ix, x in enumerate(y):
				if x == 0:
					x = ' '
				elif x == 1:
					x = '□' #'▘'
				if ix == line_end:
					print(str(x) + '||')
				else:
					print(x, end='')
		print('-' * (line_end + 5))
		#print(self.pos)
		sleep(.5)


if __name__ == '__main__':
	print('''
#########################
# AI maze runner v.0003 #
#########################
	''')
	input('press [Enter]')
	i = Runner()
	i.map_maze()


