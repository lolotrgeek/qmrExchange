import unittest

class FeesTests(unittest.TestCase):

    def setUp(self):
        self.fees = Fees()

    def test_taker_fee(self):
        volume = 1000
        expected_fee = volume * self.fees.taker_fee_rate
        self.assertEqual(self.fees.taker_fee(volume), expected_fee)

    def test_maker_fee(self):
        volume = 1000
        expected_fee = volume * self.fees.maker_fee_rate
        self.assertEqual(self.fees.maker_fee(volume), expected_fee)

if __name__ == '__main__':
    unittest.main()