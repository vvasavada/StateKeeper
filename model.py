  
from collections import defaultdict


############################## NETWORK TOPOLOGY ##################################
class Port:
	'''
	This class represents a port.
	Port has Id,Forwarding Rules, connecting ports, and input atomic predicates (output of prior port in the path)
	'''
	def __init__(self, id, fr=[], nxt={}):
		self.id = id
		self.fr = fr
		self.next = nxt  # {porti:{throughput: x, delay:y}, portj:{throughput: m, delay:n}}  throughput in Mbps, delay in ms
		self.input = None  # {fr: ___ , total_throughput, total_delay}

	def output(self):
		'''
		This method simply intersects input rules with its filters (S(F) and S(A) in the paper)
		'''
		if self.fr:
			output_fr = list(set(self.fr).intersection(self.input["fr"]))
		else:
			if not self.input:
				print self.id
			output_fr = self.input["fr"]
		return {"fr": output_fr}

	def set_inputs(self):
		'''
		Set inputs for the next connecting ports in the path
		'''
		for port in self.next:
			port.input = self.output()

			total_delay = self.input["total_delay"] + self.next[port]["delay"]

			port.input["total_delay"] = total_delay

	def __str__(self):
		'''
		String representation of Port class
		'''
		result = "Port #"
		result += str(self.id) + "\n"
		result += "Input: " + str(self.input) + "\n"
		result += "S(F): " + str(self.fr) + "\n"
		result += "Output: " + str(self.output()) + "\n"
		result += "Total Delay: " + str(self.input["total_delay"])

		return result

class Network:
	'''
	This class represents the network topology.
	It is basically a graph of ports.
	'''
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


################################ EXAMPLE ###############################
if __name__ == "__main__":

	# moving on to reachability

	print "\n"
	print "Reachability"
	print "\n"

	# Create the ports
	# Port -> id, forwarding rules, Next (ports connected to) with delay and throughput

	p11 = Port(11)
	p10 = Port(10, nxt={p11:{"delay": 0}})
	p9 = Port(9, nxt={p11:{"delay": 0}})
	p8 = Port(8, fr=[0], nxt={p10:{"delay": 1}})
	p7 = Port(7, nxt={p8:{"delay": 0}})
	p6 = Port(6, nxt={p9:{"delay": 1}})
	p5 = Port(5, fr=[2])
	p4 = Port(4, nxt={p5:{"delay": 0}, p6:{"delay": 0}})
	p3 = Port(3, fr=[0], nxt={p7:{"delay": 1}})
	p2 = Port(2, fr=[2, 3], nxt={p4:{"delay": 1}})
	p1 = Port(1, nxt={p2:{"delay": 0}, p3:{"delay": 0}})

	# Build the network graph

	network = Network([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11])
	network.add_edge(p1, p2)
	network.add_edge(p1, p3)
	network.add_edge(p2, p4)
	network.add_edge(p3, p7)
	network.add_edge(p4, p5)
	network.add_edge(p4, p6)
	network.add_edge(p7, p8)
	network.add_edge(p6, p9)
	network.add_edge(p8, p10)
	network.add_edge(p9, p11)
	network.add_edge(p10, p11)

	# Give initial input to port 1 (all atomic predicates and total delay set to 0)

	p1.input = {"fr": [0, 1, 2, 3], "total_delay": 0}

	# Print reachability tree which is basically Depth First Search
	network.print_paths(p1.id, p11.id)