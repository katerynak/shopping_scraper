import unittest as ut

import data_processing.product_similarity as prod_sim


class TestProductSimilarity(ut.TestCase):
    """
    Tests product similarity functions.
    """

    def test1(self):
        self.assertEqual(prod_sim.quantity_similarity("2 x 50   kg", "100 l"), 1)

    def test2(self):
        self.assertEqual(prod_sim.quantity_similarity("2 x 100   kg", "100 l"), 0)

    def test3(self):
        self.assertEqual(prod_sim.quantity_similarity("2 x 100   kg", "100 l"), 0)

    def test4(self):
        self.assertEqual(prod_sim.quantity_similarity("2 stuk(s)", "2 stuks"), 1)

    def test5(self):
        self.assertEqual(prod_sim.quantity_similarity("per stuk", "1 stuk(s)"), 1)

    def test6(self):
        self.assertEqual(
            prod_sim.names_similarity(
                "Dr. Ristorante pizze tonni", "Dr. Oetker Pizza Ristorante Tonno"
            ),
            0,
        )

    def test7(self):
        self.assertEqual(
            prod_sim.names_similarity(
                "Dr. oetker Ristorante pizze tonni", "Dr. Oetker Pizza Ristorante Tonno"
            ),
            1,
        )

    def test8(self):
        self.assertEqual(
            prod_sim.names_similarity(
                "dr. oetker ristorante pizze tonni", "Dr. Oetker Pizza Ristorante Tonno"
            ),
            1,
        )

    def test9(self):
        self.assertEqual(prod_sim.find_measure("100kg"), "kg")

    def test10(self):
        self.assertEqual(prod_sim.find_measure("100pounds"), "pounds")

    def test11(self):
        self.assertEqual(prod_sim.find_quantity("100pounds", "pounds"), 100)

    def test12(self):
        self.assertEqual(prod_sim.convert_measure(10, "kg"), (10000, "g"))

    def test13(self):
        self.assertEqual(prod_sim.convert_measure(10, "pounds"), (10, "pounds"))
