
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

if __name__ == "__main__":
	# calculate forwarding rule atomic predicates
	f_aps = atomic_predicates(["11*", "101*", "10*"])
	
	# print the atomic predicates

	print "\nForwarding Rule APs"
	print_aps(f_aps)
	print "\n--------------------"