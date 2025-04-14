

def find_least_decimal_digit_for_shares(buy_price: float) -> int:
    test_share_count = 100
    dollar_amount_min = 2

    while test_share_count*buy_price > dollar_amount_min:
        test_share_count /= 10
    return test_share_count*10


