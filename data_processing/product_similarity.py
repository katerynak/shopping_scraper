"""
Different product similarity functions.
"""
import Levenshtein as lev
import re

# Product comparison hyperparameters.
MAX_WORDS_DIF = 2
MAX_WORD_CHARACTER_DIFF = 1

# Possible measures that can be found on the web shops.
MEASURES = ["gram", "stuks", "per stuk", "stuk(s)", "kg", "g", "ml", "l"]
# Mapping of each measure to a common measure used to compare product quantity
# with other products.
MEASURES_MAPPING = {
    "ml": "g",
    "l": "kg",
    "stuks": "stuk(s)",
    "per stuk": "stuk(s)",
    "gram": "g",
}
# Conversion of both measures and quantities.
CONVERSION = {
    "kg": lambda q: [q * 1000, "g"],
    "l": lambda q: [q * 1000, "g"],
    "gram": lambda q: [q, "g"],
    "ml": lambda q: [q, "g"],
    "g": lambda q: [q, "g"],
    "stuks": lambda q: [q, "stuk(s)"],
    "per stuk": lambda q: [1, "stuk(s)"],
    "stuk(s)": lambda q: [q, "stuk(s)"],
}


def lower_str(s):
    """
    Convert all the characters in a given string to lowercase.

    :param s: string to convert
    :return: converted string
    """
    s_new = s.lower().strip()
    s_new = " ".join(s_new.split())
    return s_new


def find_measure(s):
    """
    Extract measure from a given string.

    :param s: string to extract from
    :return: extracted measure
    """
    # Sort measures to check for the possible substrings at the end.
    s = lower_str(s)
    sorted_measures = sorted(MEASURES, key=len, reverse=True)
    for m in sorted_measures:
        if m in s:
            return m
    # If the measure is unknown try to parse it anyway assuming that it is
    # placed at the end of the string after the last numerical character.
    return re.split("(\d+)", s)[-1].strip()


def find_quantity(s, m):
    """
    Convert quantity string to float.

    :param s: string containing both measure and quantity
    :param m: measure string
    :return: quantity string
    """
    if m == "per stuk":
        q = 1
        return q
    else:
        q = s.replace(m, "")

    # TODO: check for discounts
    # Sometimes quantities are written as "2x3", or "2*3".
    # Evaluate mathematical expressions to convert such quantities.
    q = q.replace("x", "*")
    q = q.replace(",", ".")
    try:
        q = float(eval(q))
    except:
        print(f"Failed to convert numerical expression: {q}")
    return q


def convert_measure(q, m):
    """
    Convert measure and quantity to the default measure.

    Convert measure and quantity to the default measure useful to compare the
    product to other products in the db. E.g., kg, l, ml, gram --> g;
    stuk, stuk(s), per stuk --> stuks
    :param q: quantity
    :param m: measure
    """
    try:
        q_new, m_new = CONVERSION[m](q)
    except KeyError:
        print(f"Unknown measure: {m}, not converted to any comparable measures.")
        q_new, m_new = q, m
    return q_new, m_new


# TODO: replace usages of this function with the function above.
def _convert_measures(q1, q2, m1, m2):
    """
    Convert m1 to corresponding m2, correcting quantities if needed.
    """
    # kg to grams, l to ml.
    if m1 != m2:
        if m1 in MEASURES_MAPPING.keys():
            m1 = MEASURES_MAPPING[m1]
        if m2 in MEASURES_MAPPING.keys():
            m2 = MEASURES_MAPPING[m2]
        # Ff still different convert kg to g.
        if m1 != m2:
            if m1 == "kg":
                q1 *= 1000
                m1 = "g"
            elif m2 == "kg":
                q2 *= 1000
                m2 = "g"
            # If still different we don't have a match.
            if m1 != m2:
                return None
    # The measures are equal now.
    return q1, q2, m1, m2


def names_similarity(name1, name2):
    """
    Compute names similarity.

    We consider two products names the same product if their names contain
    the same set of words.

    :param name1: first name
    :param name2: second name
    :return: names similarity between 0 and 1
    """
    # Convert all characters to lower case.
    name1 = lower_str(name1)
    name2 = lower_str(name2)
    # Extract set of words from each product. Comparing set of words is useful
    # for cases in which the same product name is written with some words in
    # different order.
    words_name1 = set(name1.split(" "))
    words_name2 = set(name2.split(" "))
    if words_name1 == words_name2:
        return 1
    # Even one word difference is considered enough for two products to be
    # different.
    if len(words_name1) != len(words_name2):
        return 0
    # Compute the word sets difference.
    # Extract words different in the first string wrt the second.
    diff1 = sorted(set(name1.split(" ")).difference(set(name2.split(" "))))
    # Extract words different in the second string wrt the first.
    diff2 = sorted(set(name2.split(" ")).difference(set(name1.split(" "))))
    # Compute Levenshtein distance for each pair of words that are different.
    # See https://en.wikipedia.org/wiki/Levenshtein_distance.
    lev_distance = []
    for i in range(len(diff1)):
        d = lev.distance(diff1[i], diff2[i])
        # If a Levenshtein distance of a single words pair is bigger then a
        # certain threshold, consider two product names different.
        if d > MAX_WORD_CHARACTER_DIFF:
            return 0
        lev_distance.append(d)
    # If the total Levenshtein distance is is bigger then a  certain threshold,
    # consider two product names different.
    if len(lev_distance) > MAX_WORDS_DIF:
        return 0
    else:
        # TODO:to be adjusted by the total leverstein distance.
        return 1


# TODO: obsolete, replace with the version with a dictionary to do it.
def match_measures(q1, q2):
    """
    Extract measures and quantities from input quantity strings.

    Extract measures from q1 and q2, then converts them, if measures cannot be
    converted returns None.

    :param q1: quantity string 1, containing both the measure and the quantity
    :param q2: quantity string 2 (format same as q1)
    """
    # Convert all characters to lower case.
    q1 = lower_str(q1)
    q2 = lower_str(q2)
    # Extract measure.
    m1 = find_measure(q1)
    m2 = find_measure(q2)
    # Extract quantity.
    q1 = find_quantity(q1, m1)
    q2 = find_quantity(q2, m2)
    # Convert measures and quantities in order to compare them.
    new_measures_quantities = _convert_measures(q1, q2, m1, m2)
    if new_measures_quantities is None:
        # If corresponding measures were not found, return None.
        return None
    else:
        return q1, q2, m1, m2


def quantity_similarity(q1, q2):
    """
    Decide if strings q1 and q2 are the same quantity strings.

    :param q1: quantity string 1
    :param q2: quantity string 2
    """
    # Convert all characters to lower case.
    q1 = lower_str(q1)
    q2 = lower_str(q2)
    # Remove white spaces and compare.
    if q1.replace(" ", "") == q2.replace(" ", ""):
        return 1
    # If two strings are different, extract and compare their measures and
    # quantities.
    m1 = find_measure(q1)
    m2 = find_measure(q2)
    q1 = find_quantity(q1, m1)
    q2 = find_quantity(q2, m2)
    # Obtain quantities of common measure.
    new_measures_quantities = _convert_measures(q1, q2, m1, m2)
    if new_measures_quantities is None:
        # If corresponding measures were not found, return 0.
        return 0
    else:
        # The measures are the same, check the quantity.
        if q1 == q2:
            return 1
        else:
            return 0


def same_product(product1, product2):
    """
    Check if product1 and product2 are the same product.

    If the products have the same (or very similar) names and the same quantity,
    they are considered the same product.

    :param product1: first product
    :param product2: second product
    """
    # Check names and quantities.
    if names_similarity(product1["name"], product2["name"]) and quantity_similarity(
        product1["quantity"], product2["quantity"]
    ):
        return 1
    else:
        return 0
