  
from collections import defaultdict

################# HELPER FUNCTIONS ####################

def print_aps(aps):
	'''
	Gives serial number of atomic predicates
	Example:
	0 0*
	1 10*
	'''
	i = 0
	for ap in aps:
		print str(i) + " " + str(ap)
		i += 1

################## HEADER SPACE ALGEBRA #########################
def complement(prefix):
	'''
	Given a prefix, return its complement
	Example:
	0* -> [1*]
	10* -> [0**, *1*]
	'''
	result = []
	star_str = "*" * len(prefix)
	i = 0
	ch = prefix[i]
	while ch != "*":
		if ch == "1":
			s = star_str[:i] + "0" + star_str[i + 1:]
		else:
			s = star_str[:i] + "1" + star_str[i + 1:]
		result.append(s)
		star_str = "*" * len(prefix)
		i += 1
		ch = prefix[i]
	return result

def _intersection(bit1, bit2):
	'''
	Helper function for intersection
	Defines intersection of two bits
	1/0 1/0 -> 1/0
	1 0 -> z (empty)
	1/0 * -> 1/0
	'''
	if bit1 == bit2:
		return bit1
	elif bit1 == "*":
		return bit2
	elif bit2 == "*":
		return bit1
	else:
		return "z"

def intersection(prefix1, prefix2):
	'''
	Gives intersection of two prefixes based on rules above
	'''
	result = ""
	limit = min(len(prefix1), len(prefix2))
	for i in range(limit):
		retval = _intersection(prefix1[i], prefix2[i])
		if retval == "z":
			return "z"
		result += retval
	if len(prefix1) < len(prefix2):
		result += prefix2[limit:]
	else:
		result += prefix1[limit:]

	return result

def atomic_predicates(prefixes):
	'''
	Gives atomic predicates of the given prefixes
	'''

	# Sort the prefixes based on their length in increasing order
	prefixes.sort(key=len)

	# Get the {P, not (P)} for each prefix
	pairs = []
	for prefix in prefixes:
		pairs.append([prefix] + complement(prefix))

	# if there is only one prefix, {P, not (P)}
	#  will be the set of atomic predicates
	if len(pairs) == 1:
		return [pairs[0][0], list(pairs[0][1:])]

	# Take first pair and intersect it with second pair
	# Take the resulting set and intersect it with third pair and so on...
	# However, this might also generate two intersecting prefixes (e.g. 0** and 01*)
	# in the resulting set. Hence, keep the bigger of the two and get rid of the other
	# (here, keep 0** and get rid of 01*). In case where they represent same size universe, 
	# keep them as union (e.g. {1001*, [0****, *1***, **1**, ***0*]})
	result = pairs[0]
	temp = []
	for i in range(1, len(pairs)):
		for j in range(len(result)):
			for k in range(len(pairs[i])):
				retval = intersection(result[j], pairs[i][k])
				if retval != "z":
					append = True
					for l in range(len(temp)):
						if type(temp[l]) != list:
							if intersection(temp[l], retval) != "z":
								append = False
								if len(retval) - retval.count("*") < len(temp[l]) - temp[l].count("*"):
									temp[l] = retval
								elif len(retval) - retval.count("*") == len(temp[l]) - temp[l].count("*"):
									temp[l] = [temp[l]] + [retval]
						else:
							if intersection(temp[l][0], retval) != "z":
								append = False
								if len(retval) - retval.count("*") < len(temp[l]) - temp[l].count("*"):
									temp[l] = retval
								elif len(retval) - retval.count("*") == len(temp[l]) - temp[l].count("*"):
									temp[l].append(retval)
					if append:
					    temp.append(retval)
		result = temp[:]
		temp = []
	return result

############################## NETWORK TOPOLOGY ##################################
class Port:
	'''
	This class represents a port.
	Port has Id, ACLs, Forwarding Rules, connecting ports, and input atomic predicates (output of prior port in the path)
	'''
	def __init__(self, id, acl=[], fr=[], nxt={}):
		self.id = id
		self.acl = acl
		self.fr = fr
		self.next = nxt  # {porti:{throughput: x, delay:y}, portj:{throughput: m, delay:n}}  throughput in Mbps, delay in ms
		self.input = None  # {fr: ___ , acl: ____, total_throughput, total_delay}

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
		if self.acl:
			output_acl = list(set(self.acl).intersection(self.input["acl"]))
		else:
			output_acl = self.input["acl"]

		return {"fr": output_fr, "acl": output_acl}

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
		result += "S(A): " + str(self.acl) + "\n"
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

	# calculate forwarding rule atomic predicates
	f_aps = atomic_predicates(["11*", "101*", "10*"])
	
	# calculate acl atomic predicates
	acl_aps = atomic_predicates(["1001*"])

	# print the atomic predicates

	print "\nForwarding Rule APs"
	print_aps(f_aps)
	print "\n--------------------"
	print "\nACL Rule APs"
	print_aps(acl_aps)
	print "\n--------------------"


	# moving on to reachability

	print "\n"
	print "Reachability"
	print "\n"

	# Create the ports
	# Port -> id, forwarding rules, ACLs, Next (ports connected to) with delay and throughput

	p11 = Port(11)
	p10 = Port(10, nxt={p11:{"delay": 0}})
	p9 = Port(9, acl=[0], nxt={p11:{"delay": 0}})
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

	p1.input = {"fr": [0, 1, 2, 3], "acl": [0, 1], "total_delay": 0}

	# Print reachability tree which is basically Depth First Search
	network.print_paths(p1.id, p11.id)