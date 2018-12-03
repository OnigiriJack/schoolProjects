

# Jack Fowler 4/16/18
# Ue Luhn's algorithm to check if a credit card number is valid Every company uses a specific amount of digits and starts cards with different numbers
# Notes: Definitely the trickiest part was finding specific digits.
from cs50 import get_float


def main():
    cc = get_float("Enter credit card number:  ")
    if check_sum(second_to_last_digit_sum(cc), last_digit_sum(cc)):
        company_check(cc, card_length(cc))
    else:
        print("INVALID")

def company_check(card, cc_len):
    """determine credit card company"""
    s = str(card)
    digit = int(s[0:2])
    if digit > 50 and digit < 56 and cc_len == 16:
        print("MASTERCARD")
    elif digit == 34 or digit == 37 and cc_len == 15:
        print("AMEX")
    elif (digit - digit % 10) / 10 == 4 and cc_len == 13 or cc_len == 16:
        print("VISA")
    else:
        print("INVALID")


def card_length(card_number):
    """return number of digits in credit card number"""
    cl = 0
    while True:
        card_number = card_number // 10
        cl += 1
        if card_number <= 0:
            break
    return cl


def last_digit_sum(card):
    """finds the sum of every other digit per luhn's algorithm starting last digit"""
    ldsum = 0
    while True:
        ldsum = ldsum + card % 10
        card = card // 100
        if card <= 0:
            break
    return ldsum


def second_to_last_digit_sum(card):
    """finds the sum of every other digit per luhn's algorithm starting from second to last digit"""
    ssum = 0
    card = card // 10
    while True:
        if card <= 0:
            break
        product = (card % 10) * 2
        if product >= 10:
            product = (product % 10) + (product - (product % 10)) // 10
        ssum = ssum + product
        card = card // 100
    return ssum


def check_sum(sum1, sum2):
    """Luhn's check sum algorithm"""
    if ((sum1 + sum2) % 10) == 0:
        return True
    else:
        return False


if __name__ == "__main__":
    main()