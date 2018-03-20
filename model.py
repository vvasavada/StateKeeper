import sys
import random
import timeit
from collections import defaultdict


############################## NETWORK TOPOLOGY ##################################
class Destination:
	"""
	This class represents a destination.
	Destination only has input and ID.
	"""
	def __init__(self, id):
		self.id = id
		self.input = None  # {fr: ___ , total_throughput, total_delay}

	def __str__(self):
		"""
		String representation of Port class
		"""
		result = "Destination #"
		result += str(self.id) + "\n"
		result += "Output FR: " + str(self.input["fr"]) + "\n"
		result += "Total Delay: " + str(self.input["total_delay"]) + "\n"
		result += "Total Throughput: " + str(self.input["total_throughput"])

		return result

class Port:
	"""
	This class represents a port.
	Port has Id,Forwarding Rules, connecting ports, and input atomic predicates (output of prior port in the path)
	"""
	def __init__(self, id, fr=[], nxt={}):
		self.id = id
		self.fr = fr
		self.next = nxt  # {porti:{throughput: x, delay:y}, portj:{throughput: m, delay:n}}  throughput in Mbps, delay in ms
		self.input = None  # {fr: ___ , total_throughput, total_delay}

	def output(self):
		"""
		This method simply intersects input rules with its filters (S(F) and S(A) in the paper)
		"""
		if self.fr:
			output_fr = list(set(self.fr).intersection(self.input["fr"]))
		else:
			if not self.input:
				print self.id
			output_fr = self.input["fr"]
		return {"fr": output_fr}

	def set_inputs(self):
		"""
		Set inputs for the next connecting ports in the path
		"""
		for node in self.next:
			node.input = self.output()

			total_delay = self.input["total_delay"] + self.next[node]["delay"]
			node.input["total_delay"] = total_delay

			total_throughput = min(self.input["total_throughput"], self.next[node]["throughput"])
			node.input["total_throughput"] = total_throughput

	def __str__(self):
		"""
		String representation of Port class
		"""
		result = "Port #"
		result += str(self.id) + "\n"
		result += "Input: " + str(self.input) + "\n"
		result += "S(F): " + str(self.fr) + "\n"
		result += "Output FR: " + str(self.output()["fr"]) + "\n"
		result += "Total Delay: " + str(self.input["total_delay"]) + "\n"
		result += "Total Throughput: " + str(self.input["total_throughput"])

		return result

class Network:
	"""
	This class represents the network topology.
	It is basically a graph of ports.
	"""
	def __init__(self, ports):
		self.ports = self._map(ports)
		self.graph = defaultdict(list)

	def _map(self, ports):
		result = {}
		for port in ports:
			result[port.id] = port
		return result

	def add_edge(self, port1, port2):
		self.graph[port1.id].append(port2.id)

	def _print_paths(self, u, d, visited, path):
		visited[u-1] = True
		port = self.ports[u]
		if port.__class__ == Port:
			port.set_inputs()
		path.append(port)
		if u == d:
			for port in path:
				print port
				print "\n"
			print "-----------"
		else:
			for i in self.graph[u]:
				if not visited[i-1]:
					self._print_paths(i, d, visited, path)

		path.pop()
		visited[u-1] = False

	def print_paths(self, src, dst):
		visited = [False]*(len(self.ports))

		path = []

		self._print_paths(src, dst, visited, path)

###################3 For calculation of runtime #######################

'''def generate_random_network(n):
	forwarding_rules = [0, 1, 2, 3, 4, 5, 6, 7, 8]
	nodes = []
	destination = Destination(n)
	nxt = {destination: {"delay": random.randint(0, n), "throughput": random.randint(0, 50)}}


	nodes.insert(0, destination)
	for i in range(n-1, 0, -1):
		port = Port(id=i, fr=forwarding_rules, nxt=nxt)
		nxt = {port: {"delay": random.randint(0, n), "throughput": random.randint(0, 50)}}
		nodes.insert(0, port)

	nodes[0].input = {"fr": forwarding_rules, "total_delay": random.randint(0, n), "total_throughput": random.randint(0, 50)}
	network = Network(nodes)
	for i in range(n-1):
		network.add_edge(nodes[i], nodes[i+1])

	return network'''



################################ EXAMPLE ###############################
if __name__ == "__main__":

	# moving on to reachability

	print "\n"
	print "Reachability"
	print "\n"

	D = Destination(7)
	C = Destination(8) 

	p6 = Port(6, fr=[1], nxt={C:{"delay": 1, "throughput": 10}})
	p5 = Port(5, fr=[0], nxt={D:{"delay": 1, "throughput": 5}})
	p2 = Port(2, fr=[0], nxt={D:{"delay": 5, "throughput": 30}})


	p4 = Port(4, nxt={p6:{"delay": 0, "throughput": 20}, p5:{"delay": 0, "throughput": 20}})
	p3 = Port(3, fr=[0, 1, 2], nxt={p4:{"delay": 3, "throughput": 20}})
	p1 = Port(1, nxt={p2:{"delay": 0, "throughput": 10}, p3:{"delay": 0, "throughput": 10}})

	network = Network([p1, p2, p3, p4, p5, p6, D, C])
	network.add_edge(p1, p2)
	network.add_edge(p1, p3)
	network.add_edge(p3, p4)
	network.add_edge(p4, p5)
	network.add_edge(p4, p6)
	network.add_edge(p2, D)
	network.add_edge(p5, D)
	network.add_edge(p6, C)

	p1.input = {"fr": [0, 1, 2, 3], "total_delay": 0, "total_throughput": 10}

	# Print reachability tree which is basically Depth First Search
	network.print_paths(p1.id, D.id)

	######## For calculation of runtime #######

	'''sys.setrecursionlimit(1000000)
	elapsed_times = []
	n = 5
	while n > 0:
		network = generate_random_network(250)
		start_time = timeit.default_timer()
		network.print_paths(1, len(network.ports))
		elapsed = timeit.default_timer() - start_time
		elapsed_times.append(elapsed * 1000)
		n -= 1
	print sum(elapsed_times)/len(elapsed_times)'''