# print blocks for mario to jump over

# get user input
from cs50 import get_int

# Prompt user for a positive number
while True:
    n = get_int("Positive number: ")
    if n > 0 and n < 23:
        break

# Print out this many rows
# Print pyramid leaning to the right
for i in range(n):
    spaces = n - (1 + i)
    print(" " * spaces, end="")
    print("#" * (2 + i), end="")
    print("")
