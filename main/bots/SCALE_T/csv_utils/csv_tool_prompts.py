


# Creating a new csv questionaires
def create_csv_questionaire():
    answers = {}
    print("=== CSV Creation ===")
    answers["total_cash"] = float(input("Enter total cash: "))
    print("Context on risk type, dictates, total number of lines, higher risk == more lines")
    answers["risk_type"] = int(input("Enter risk type (1 for low all the way to 5 for high): "))
    answers["percentage_diff"] = float(input("Enter percentage difference between buy and sell: "))
    answers["starting_buy_price"] = float(input("Enter starting buy price: "))
    answers["distribution_style"] = input("Enter distribution style (linear or exponential): ")
    return answers

# Manipulating an existing csv questionaires
def manipulate_csv_questionaire():
    answers = {}
    input("Hi there, we don't have manipulate functionality just yet")
    return answers
