


# The intent of this code is to give u the least decimal place for shares
# that amount to 2 dollars or more.
def find_least_decimal_digit_for_shares(buy_price: float) -> int:
    test_share_count = 100
    dollar_amount_min = 2

    while test_share_count*buy_price > dollar_amount_min:
        test_share_count /= 10
    return test_share_count*10


# A variation of least_decimal_place_shares
# Basically, give me a buy_price and a target_share count
# and I'll clip the digits that when isolated are less than $2
# formula is shares_to_subtract = ((bp*ts)%dollar_clip)/bp
def clip_decimal_place_shares(buy_price: float, target_shares: float, dollar_clip=2) -> float:
    # Convert dollar_clip to shares and get the mod of target_shares return that
    clip_shares = dollar_clip / buy_price
    return target_shares % clip_shares # returning the shares to subtract

