import itertools

from transit_pylark.types import keyword, frozendict, frozenlist


def mapcat(f, i):
    return itertools.chain.from_iterable(map(f, i))


def pairs(i):
    return zip(*[iter(i)] * 2)


cycle = itertools.cycle


def take(n, i):
    return itertools.islice(i, 0, n)


def ints_centered_on(m, n=5):
    return tuple(range(m - n, m + n + 1))


def array_of_symbols(m, n=None):
    if n is None:
        n = m

    seeds = map(lambda x: keyword("key" + str(x).zfill(4)), range(0, m))
    return take(n, cycle(seeds))


def hash_of_size(n):
    return frozendict(zip(array_of_symbols(n), range(0, n + 1)))


powers_of_two = frozenlist(map(lambda x: pow(2, x), range(66)))
