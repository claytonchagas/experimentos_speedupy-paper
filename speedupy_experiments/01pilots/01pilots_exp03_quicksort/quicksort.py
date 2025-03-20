import time
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from speedupy.speedupy import initialize_speedupy, deterministic

@deterministic
def quicksort(list):
    if len(list) <= 1:
        return list
    pivot = list[0]
    equal = [x for x in list if x == pivot]
    greater = [x for x in list if x > pivot]
    lesser = [x for x in list if x < pivot]
    return quicksort(lesser) + equal + quicksort(greater)

@initialize_speedupy
def main(unsort_list):
    print(quicksort(unsort_list))
if __name__ == '__main__':
    import random
    random.seed(0)
    unsort_list = [random.randint(1, 1000000000000) for i in range(int(float(sys.argv[1])))]
    start = time.perf_counter()
    main(unsort_list)
    print(time.perf_counter() - start)