


# Creating a new csv questionaires
def create_csv_questionaire():
    answers = {}
    print("=== CSV Creation ===")
    answers["total_cash"] = float(input("Enter total cash: "))
    print("Context on risk type, dictates, total number of lines, higher risk == more lines")
    answers["risk_type"] = float(input("Enter risk type (1 for low all the way to 5 for high): "))
    answers["percentage_diff"] = float(input("Enter percentage difference between buy and sell: "))
    answers["starting_buy_price"] = float(input("Enter starting buy price: "))
    answers["distribution_style"] = input("Enter distribution style (linear or exponential): ")
    return answers


def get_information_on_csv_questionaire():
    answers = {}
    input("No questions for information retrieval yet")
    return answers

def chase_price_questionaire():
    answers = {}
    answers["current_price"] = float(input("Enter current price: "))
    return answers

def update_csv_questionaire():
    answers = {}
    print("=== CSV Update ===")
    print("Which update do you want to do?")
    update_type = int(input(f"1. Chase price\n"))
    if update_type == 1:
        print("Chasing price")
        answers = chase_price_questionaire()
    else:
        print("No other options yet")
    answers["update_type"] = update_type
    return answers
