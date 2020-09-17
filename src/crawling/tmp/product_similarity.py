"""
code for different product similarity functions
"""
import Levenshtein as lev

# hyperparameters
max_words_different = 2
max_word_character_diff = 1

measures = ["stuks", "per stuk", "stuk(s)", "kg", "g", "ml", "l"]

measures_mapping = {"ml": "g", "l": "kg", "stuks": "stuk(s)", "per stuk": "stuk(s)"}


def lower_str(s):
	s_new = s.lower().strip()
	s_new = " ".join(s_new.split())
	return s_new


def find_measure(s):
	"""
	extracts measure from a given string
	"""
	# sort measures to check for the possible substrings at the end
	sorted_measures = sorted(measures, key=len, reverse=True)
	for m in measures:
		if m in s:
			return m
	return ""


def find_quantity(q, m):
	"""
	converts quantity string to float
	"""

	if m == "per stuk":
		q = 1
		return q
	else:
		q = q.replace(m, "")

	# TODO: check for discounts
	# evaluate mathematical expressions
	q = q.replace("x", "*")
	try:
		q = float(eval(q))
	except:
		return 0

	return q


def convert_measures(q1, q2, m1, m2):
	"""
	converting m1 to corresponding m2, correcting quantities if needed
	"""
	# kg to grams, l to ml
	if m1 != m2:
		if m1 in measures_mapping.keys():
			m1 = measures_mapping[m1]
		if m2 in measures_mapping.keys():
			m2 = measures_mapping[m2]
		# if still different convert kg to g
		if m1 != m2:
			if m1 == "kg":
				q1 *= 1000
				m1 = "g"
			elif m2 == "kg":
				q2 *= 1000
				m2 = "g"
			# if still different we don't have a match
			if m1 != m2:
				return None
	# the measures are equal now
	return q1, q2, m1, m2


def names_similarity(name1, name2):
	# we consider two products names the same product if their names contain the same set of words
	"""
	returns names similarity between 0 and 1
	"""
	name1 = lower_str(name1)
	name2 = lower_str(name2)

	words_name1 = set(name1.split(" "))
	words_name2 = set(name2.split(" "))
	if words_name1 == words_name2:
		return 1

	# even one word difference is considered grave
	if len(words_name1) != len(words_name2):
		return 0

	diff1 = sorted(set(name1.split(" ")).difference(set(name2.split(" "))))
	diff2 = sorted(set(name2.split(" ")).difference(set(name1.split(" "))))

	lev_distance = []
	for i in range(len(diff1)):
		d = lev.distance(diff1[i], diff2[i])
		if d > max_word_character_diff:
			return 0
		lev_distance.append(d)

	if len(lev_distance) > max_words_different:
		return 0

	# TODO:to be adjusted by the total leverstein distance
	return 1


def quantity_similarity(q1, q2):
	"""
	decides if strings q1 and q2 are the same quantity strings
	"""
	q1 = lower_str(q1)
	q2 = lower_str(q2)

	if q1.replace(" ", "") == q2.replace(" ", ""):
		return 1

	m1 = find_measure(q1)
	m2 = find_measure(q2)

	q1 = find_quantity(q1, m1)
	q2 = find_quantity(q2, m2)

	new_measures_quantities = convert_measures(q1, q2, m1, m2)
	if new_measures_quantities is None:
		# corresponding measures were not found
		return 0
	else:
		# we have the same measures, let's check the quantity
		if q1 == q2:
			return 1
		else:
			return 0


def same_product(product1, product2):
	"""
	checks if product1 and product2 are the same product
	"""
	# check names and quantities
	if names_similarity(product1["name"], product2["name"]) and quantity_similarity(product1["quantity"], product2["quantity"]):
		return 1
	return 0

	# TODO: define product SIMILARITY, check image and/or indgredients as well,
	#  return something between 0 and 1 based on similarity


if __name__ == "__main__":
	# tests, to be tested in a separate dir
	assert quantity_similarity("2 x 50   kg", "100 l") == 1
	assert quantity_similarity("2 x 100   kg", "100 l") == 0
	assert quantity_similarity("2 x 100   kg", "100 l") == 0
	assert quantity_similarity("2 stuk(s)", "2 stuks") == 1
	assert quantity_similarity("per stuk", "1 stuk(s)") == 1
	assert names_similarity("Dr. Ristorante pizze tonni", "Dr. Oetker Pizza Ristorante Tonno") == 0
	assert names_similarity("Dr. oetker Ristorante pizze tonni", "Dr. Oetker Pizza Ristorante Tonno") == 1
	assert names_similarity("dr. oetker ristorante pizze tonni", "Dr. Oetker Pizza Ristorante Tonno") == 1
