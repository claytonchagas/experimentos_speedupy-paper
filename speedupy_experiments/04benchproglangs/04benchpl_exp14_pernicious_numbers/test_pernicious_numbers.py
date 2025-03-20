import sys
import time
from speedupy.speedupy import initialize_speedupy, deterministic

@deterministic
def is_prime_number(n):
    """
      Deterine if a positive integer is prime or not.
    """
    if n in (2, 3):
        return True
    if 2 > n or 0 == n % 2:
        return False
    if 9 > n:
        return True
    if 0 == n % 3:
        return False
    return not any(map(lambda x: 0 == n % x or 0 == n % (2 + x), range(5, 1 + int(n ** 0.5), 6)))

@deterministic
def get_number_of_ones(n):
    """
      Deterine the number of 1s ins the binary representation of
      and integer n.
    """
    temp = bin(n)
    return temp.count('1')

@deterministic
def find_pernicious_numbers(n):
    """
       Find the nth pernicious number.
    """
    i = 1
    counter = 0
    while counter < n:
        if is_prime_number(get_number_of_ones(i)):
            counter += 1
        i += 1
    return (i - 1, counter)

@initialize_speedupy
def main(N):
    find_pernicious_numbers(N)
if __name__ == '__main__':
    N = int(sys.argv[1])
    dti = time.perf_counter()
    main(N)
    print(time.perf_counter() - dti)