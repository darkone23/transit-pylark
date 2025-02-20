from dataclasses import dataclass

from frozenlist import FrozenList
from immutabledict import immutabledict

import arrow


class frozendict(immutabledict):

    def __repr__(self):
        frozenstr = super().__repr__()
        xs_part = frozenstr[11:]
        return f"frozendict({xs_part}"


class instant(arrow.Arrow):

    @staticmethod
    def from_arrow(a: arrow.Arrow):
        return instant(
            year=a.year,
            month=a.month,
            day=a.day,
            hour=a.hour,
            minute=a.minute,
            second=a.second,
            microsecond=a.microsecond,
            tzinfo=a.tzinfo,
        )

    @staticmethod
    def from_isostr(str):
        return instant.from_arrow(arrow.get(str))

    @staticmethod
    def from_unixtime(epoch):
        return instant.from_arrow(arrow.get(epoch))


class frozenlist(FrozenList):

    def __init__(self, items):
        super().__init__(items)
        self.freeze()

    def __repr__(self):
        frozenstr = super().__repr__()
        xs_part = frozenstr[25:-2]
        return f"frozenlist({xs_part})"


@dataclass(frozen=True)
class CacheHandle:
    cursor: int
    item: any


@dataclass(frozen=True)
class transit_tag:
    tag: str

    @staticmethod
    def tagged_value(tag: str, value):
        return (transit_tag(tag), value)

    def __len__(self):
        return len(self.tag)

    def __str__(self):
        return f"#{self.tag}"

    @staticmethod
    def tag_key(k):
        k_type = type(k)
        name: str
        if k_type is str:
            name = k
        elif k_type is transit_tag:
            name = k.tag
        elif k_type is CacheHandle and type(k.item) is transit_tag:
            name = k.item.tag
        else:
            raise KeyError(f"Incorrect key provided to tag key: {k}")
        return f"tag:{name}"

    @staticmethod
    def is_transit_tag(x):
        x_type = type(x)
        return x_type is transit_tag or (
            x_type is CacheHandle and type(x.item) is transit_tag
        )


@dataclass(frozen=True)
class keyword:
    v: str

    def __len__(self):
        return len(self.v)

    def __str__(self):
        return f":{self.v}"


@dataclass(frozen=True)
class symbol:
    v: str

    def __len__(self):
        return len(self.v)

    def __str__(self):
        return f"${self.v}"


@dataclass(frozen=True)
class mapkey:
    k: str

    def __len__(self):
        return len(self.k)

    def __str__(self):
        return f"{self.k}"


@dataclass(frozen=True)
class quoted:
    v: str

    def __len__(self):
        return len(self.v)

    def __str__(self):
        return f"'{self.v}"
