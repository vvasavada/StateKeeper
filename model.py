def complement(prefix):
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
	if bit1 == bit2:
		return bit1
	elif bit1 == "*":
		return bit2
	elif bit2 == "*":
		return bit1
	else:
		return "z"

def intersection(prefix1, prefix2):
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
	prefixes.sort(key=len)
	pairs = []

	for prefix in prefixes:
		pairs.append([prefix] + complement(prefix))

	result = pairs[0]
	temp = []

	for i in range(1, len(pairs)):
		for j in range(len(result)):
			for k in range(len(pairs[i])):
				retval = intersection(result[j], pairs[i][k])
				if retval != "z":
					append = True
					for l in range(len(temp)):
						if intersection(temp[l], retval) != "z":
							append = False
							if len(retval) - retval.count("*") < len(temp[l]) - temp[l].count("*"):
								temp[l] = retval
					if append:
						temp.append(retval)
		result = temp[:]
		temp = []
	return result


class Port:
	def __init__(self, acl=[], fr=[], nxt=None):

		self.acl = acl
		self.fr = fr
		self.next = nxt  # {porti:{throughput: x, delay:y}, portj:{throughput: m, delay:n}}  throughput in Mbps, delay in ms
		self.input = None  # {fr: ___ , acl: ____, total_throughput, total_delay}

	def output(self):
		# self.input.fr intersects fr 
		# self.input.acl intesects acl
		# keep track of throughput and delay (for each in self.next)
		return None

	def set_inputs(self):
		# for each in self.next, each.input = self.output()
		return None



class Box:
	def __init__(self, in_ports, out_ports, nxt):
		self.in_ports = in_ports
		self.out_ports = out_ports
		self.next = nxt

if __name__ == "__main__":

	print atomic_predicates(["10*", "11*", "101*", "1001*"])

	p11 = Port(fr=["*"])
	p10 = Port()
	p9 = Port(acl=["1001*"])
	p8 = Port(fr=["11*"], nxt={p10:{"throughput": 1, "delay": 10}})
	p7 = Port()
	p6 = Port(fr=["*"], nxt={p9:{"throughput": 1, "delay": 10}})
	p5 = Port(fr=["101*"])
	p4 = Port()
	p3 = Port(fr=["11*"], nxt={p7:{"throughput": 1, "delay": 1}})
	p2 = Port(fr=["10*"], nxt={p4:{"throughput": 1, "delay": 1}})
	p1 = Port()

	r4 = Box(in_ports=[p9, p10], out_ports=[p11], nxt=None)
	r3 = Box(in_ports=[p7], out_ports=[p8], nxt=[r4])
	r2 = Box(in_ports=[p4], out_ports=[p5, p6], nxt=[r4, None])
	r1 = Box(in_ports=[p1], out_ports=[p2, p3], nxt=[r2, r3])