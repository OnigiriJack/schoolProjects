# get command line arguments
import sys
from cs50 import get_string


def main():
    if len(sys.argv) == 2:
        # convert string to int
        key = int(sys.argv[1])
    else:
        print("INVALID number of command line args")
        sys.exit(1)

    # get plain text to cipher
    s = get_string("plaintext: ")
    # encipher text
    ct = ""
    for c in s:
        ct += ptoc(c, key)
    print(f"ciphertext: {ct}")


def ptoc(char, keyV):
    ciph = char
    # Only rotate letters
    if char.isalpha():
        # for uppercase characters
        if char.isupper():
            ciph = chr(((ord(char) - 65 + keyV) % 26) + 65)
        else:
            # for lower casecahracters
            ciph = chr(((ord(char) - 97 + keyV) % 26) + 97)
    return ciph

if __name__ == "__main__":
    main()