
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
	neg = {"0": "1", "1": "0"}
	result = []
	star_str = "*" * len(prefix)
	i = 0
	while i != len(prefix):
		ch = prefix[i]
		if ch != "*":
			s = star_str[:i] + neg[ch] + star_str[i+1:]
			result.append(s)
		star_str = "*" * len(prefix)
		i += 1
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

def difference(prefix1, prefix2):
	'''
	Gives difference: prefix2 - prefix1
	ASSUMPTION: Prefix1 is only has 1 digit and rest stars
	'''
	return intersection(prefix2, complement(prefix1)[0])

def atomic_predicates(prefixes):
	'''
	Gives atomic predicate set for given list of prefixes
	'''
	# Sort prefixes based on increasing length
	prefixes.sort(key=len)

	# Calculate atomic predicates for each prefix
	groups = []
	for prefix in prefixes:
		result = [prefix]
		complement_list = complement(prefix)
		if len(complement_list) == 1:
			result += complement_list
		else:
			result += [complement_list[0]]
			for i in range(1, len(complement_list)):
				diff = complement_list[i]
				for j in range(i):
					diff = difference(complement_list[j], diff)
				result += [diff]
		groups.append(result)
	
	# Intersect the atomic predicate sets to get final result
	result = groups[0]
	temp = []
	for i in range(1, len(groups)):
		for j in range(len(result)):
			for k in range(len(groups[i])):
				retval = intersection(result[j], groups[i][k])
				if retval != "z":
					temp.append(retval)
		result = temp[:]
		temp = []
	return result

if __name__ == "__main__":
    # calculate forwarding rule atomic predicates
    f_aps = atomic_predicates(["1**", "10*", "110*"])

    print "\nForwarding Rule APs"
    print_aps(f_aps)
    print "\n--------------------"