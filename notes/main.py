# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    for n in range(2, 10):
        for x in range(2, n):
            if n % x == 0:
                print(n, 'equals', x, '*', n // x)
                break
        else:
            print(n, 'is a prime number')
    string = 'abcdef'
    # a = string.
    print(string[::-1])


def get_factors(number):
    for i in range(1, number + 1):
        if number % i == 0:
            print("{} is a factor of {}.".format(i, number))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    # get_factors(10)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
