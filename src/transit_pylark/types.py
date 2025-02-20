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
            tzinfo=a.tzinfo
        )

    @staticmethod
    def from_isostr(str):
        return instant.from_arrow(
            arrow.get(str)
        )

    @staticmethod
    def from_unixtime(epoch):
        return instant.from_arrow(
            arrow.get(epoch)
        )

class frozenlist(FrozenList):

    def __init__(self, items):
        super().__init__(items)
        self.freeze()

    def __repr__(self):
        frozenstr = super().__repr__()
        xs_part = frozenstr[25:-2]
        return f"frozenlist({xs_part})"

@dataclass(frozen=True)
class transit_tag:
    tag: str

    @staticmethod
    def tagged_value(tag: str, value):
        return (transit_tag(tag), value)

    def __len__(self):
        return len(self.tag)

    def __str__(self):
        return f":{self.tag}"

    @staticmethod
    def tag_key(name):
        return f"tag:{name}"


@dataclass(frozen=True)
class keyword:
    v: str

    def __len__(self):
        return len(self.v)

    def __str__(self):
        return f":{self.v}"


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
        return f"{self.v}"

