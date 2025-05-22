import unittest
from main.bots.SCALE_T.csv_utils.csv_tool_helper import find_least_decimal_digit_for_shares, clip_decimal_place_shares


# import debugpy

# debugpy.listen(("0.0.0.0", 5678))  # Or ("localhost", 5678)
# print("Waiting for debugger attach...")
# debugpy.wait_for_client()

class TestCSVService(unittest.TestCase):
    def test_find_least_decimal_digit_for_shares(self):
        """
        Test the find_least_decimal_digit_for_shares function.
        example for 100, lets walk through the math
        decimal place is -2
        100 we test with 100*100 = 10000 > 2
        100/10 = 10, making decimal_place -1
        100*10 = 1000 > 2
        10/10 = 1, making decimal_place 0
        100*1 = 100 > 2
        1/10 = 0.1, making decimal_place 1
        100*0.1 = 10 > 2 
        0.1/10 = 0.01, making decimal_place 2
        100*0.01 = 1 > 2 false so we should get 1 for decimal place
        """
        self.assertEqual(find_least_decimal_digit_for_shares(100), .1)
        self.assertEqual(find_least_decimal_digit_for_shares(1000), .01)
        self.assertEqual(find_least_decimal_digit_for_shares(10000), .001)
        self.assertEqual(find_least_decimal_digit_for_shares(100000), .0001)

    def test_find_least_decimal_digit_for_shares_with_float(self):
        self.assertEqual(find_least_decimal_digit_for_shares(100.1), .1)
        self.assertEqual(find_least_decimal_digit_for_shares(1000.1), .01)
        self.assertEqual(find_least_decimal_digit_for_shares(10000.1), .001)
        self.assertEqual(find_least_decimal_digit_for_shares(100000.1), .0001)

    def test_clip_decimal_place_shares(self):
        """
        Test the clip_decimal_place_shares function.
        walking through some examples
        bp = 100, ts = .516, expected = .016
        """
        self.assertAlmostEqual(clip_decimal_place_shares(100, .516), .016)
        self.assertAlmostEqual(clip_decimal_place_shares(1000, .516), 0)
        


if __name__ == '__main__':
    unittest.main()
