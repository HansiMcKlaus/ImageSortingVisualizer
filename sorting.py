def bubble_sort_steps(values):
    values = values.copy()
    n = len(values)

    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if values[j] > values[j + 1]:
                values[j], values[j + 1] = values[j + 1], values[j]
                swapped = True
            # yields the live list, callers must copy it themselves
            yield values
        if not swapped:
            break


def insertion_sort_steps(values):
    values = values.copy()
    n = len(values)

    for i in range(1, n):
        key = values[i]
        j = i - 1
        while j >= 0 and values[j] > key:
            values[j + 1] = values[j]
            j -= 1
            # yields the live list, callers must copy it themselves
            yield values
        values[j + 1] = key
        yield values


def selection_sort_steps(values):
    values = values.copy()
    n = len(values)

    for i in range(n):
        min_index = i
        for j in range(i + 1, n):
            if values[j] < values[min_index]:
                min_index = j
            # yields the live list, callers must copy it themselves
            yield values
        if min_index != i:
            values[i], values[min_index] = values[min_index], values[i]
            yield values


def quick_sort_steps(values):
    values = values.copy()
    yield from _quick_sort(values, 0, len(values) - 1)


def _quick_sort(values, low, high):
    if low < high:
        pivot_index = yield from _partition(values, low, high)
        yield from _quick_sort(values, low, pivot_index - 1)
        yield from _quick_sort(values, pivot_index + 1, high)


def _partition(values, low, high):
    pivot = values[high]
    i = low - 1
    for j in range(low, high):
        if values[j] <= pivot:
            i += 1
            values[i], values[j] = values[j], values[i]
        # yields the live list, callers must copy it themselves
        yield values
    values[i + 1], values[high] = values[high], values[i + 1]
    yield values
    return i + 1


def merge_sort_steps(values):
    values = values.copy()
    yield from _merge_sort(values, 0, len(values) - 1)


def _merge_sort(values, low, high):
    if low < high:
        mid = (low + high) // 2
        yield from _merge_sort(values, low, mid)
        yield from _merge_sort(values, mid + 1, high)
        yield from _merge(values, low, mid, high)


def _merge(values, low, mid, high):
    left = values[low:mid + 1]
    right = values[mid + 1:high + 1]

    i = j = 0
    k = low
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            values[k] = left[i]
            i += 1
        else:
            values[k] = right[j]
            j += 1
        k += 1
        # yields the live list, callers must copy it themselves
        yield values

    while i < len(left):
        values[k] = left[i]
        i += 1
        k += 1
        yield values

    while j < len(right):
        values[k] = right[j]
        j += 1
        k += 1
        yield values


def heap_sort_steps(values):
    values = values.copy()
    n = len(values)

    for i in range(n // 2 - 1, -1, -1):
        yield from _sift_down(values, i, n)

    for end in range(n - 1, 0, -1):
        values[0], values[end] = values[end], values[0]
        # yields the live list, callers must copy it themselves
        yield values
        yield from _sift_down(values, 0, end)


def _sift_down(values, root, end):
    while True:
        child = 2 * root + 1
        if child >= end:
            break
        if child + 1 < end and values[child] < values[child + 1]:
            child += 1
        if values[root] >= values[child]:
            break
        values[root], values[child] = values[child], values[root]
        yield values
        root = child


def shaker_sort_steps(values):
    values = values.copy()
    start, end = 0, len(values) - 1

    while start < end:
        swapped = False
        for i in range(start, end):
            if values[i] > values[i + 1]:
                values[i], values[i + 1] = values[i + 1], values[i]
                swapped = True
            # yields the live list, callers must copy it themselves
            yield values
        end -= 1
        if not swapped:
            break

        swapped = False
        for i in range(end, start, -1):
            if values[i - 1] > values[i]:
                values[i - 1], values[i] = values[i], values[i - 1]
                swapped = True
            yield values
        start += 1
        if not swapped:
            break


def comb_sort_steps(values):
    values = values.copy()
    n = len(values)
    gap = n
    shrink = 1.3
    swapped = True

    while gap > 1 or swapped:
        gap = max(1, int(gap / shrink))
        swapped = False
        for i in range(n - gap):
            if values[i] > values[i + gap]:
                values[i], values[i + gap] = values[i + gap], values[i]
                swapped = True
            # yields the live list, callers must copy it themselves
            yield values


def pancake_sort_steps(values):
    values = values.copy()

    for size in range(len(values), 1, -1):
        max_index = 0
        for i in range(1, size):
            if values[i] > values[max_index]:
                max_index = i

        if max_index == size - 1:
            continue

        if max_index != 0:
            _flip(values, max_index)
            # yields the live list, callers must copy it themselves
            yield values

        _flip(values, size - 1)
        yield values


def _flip(values, k):
    values[:k + 1] = values[:k + 1][::-1]


def radix_sort_steps(values):
    values = values.copy()
    if not values:
        return

    place = 1
    max_value = max(values)
    while max_value // place > 0:
        yield from _counting_sort_by_digit(values, place)
        place *= 10


def _counting_sort_by_digit(values, place):
    n = len(values)
    output = [0] * n
    count = [0] * 10

    for value in values:
        count[(value // place) % 10] += 1
    for digit in range(1, 10):
        count[digit] += count[digit - 1]

    for i in range(n - 1, -1, -1):
        digit = (values[i] // place) % 10
        count[digit] -= 1
        output[count[digit]] = values[i]

    for i in range(n):
        values[i] = output[i]
        # yields the live list, callers must copy it themselves
        yield values
