from pathlib import Path
from rich.pretty import pprint
import time
import arrow
from transit_pylark.reader import TransitReader
from transit_pylark.types import (
    frozendict,
    frozenlist,
    transit_tag,
    instant,
    mapkey,
    symbol,
    keyword,
    quoted,
)

from nose2.tools import params

from dataclasses import dataclass

import sys

sys.path.append(Path(__file__).parent)

from transit_test_helpers import (
    mapcat,
    ints_centered_on,
    powers_of_two,
    hash_of_size,
    make_hash_exemplar,
)


@dataclass
class ExemplarSpec:
    name: str
    expected: any


cmap_null_key = frozendict(
    {None: "null as map key", frozenlist([1, 2]): "Array as key to force cmap"}
)

cmap_pathological = frozenlist(
    [
        frozendict(
            {
                keyword(v="any-value"): frozendict(
                    {
                        frozenlist(["this vector makes this a cmap"]): "any value",
                        "any string": keyword(v="victim"),
                    }
                )
            }
        ),
        frozendict({keyword(v="victim"): keyword(v="any-other-value")}),
    ]
)

dates_interesting = frozenlist(
    [
        instant.from_isostr("1776-07-04T12:00:00.000-00:00"),
        instant.from_unixtime(0),
        instant.from_isostr("2000-01-01T12:00:00.000-00:00"),
        instant.from_unixtime(1396909037000 / 1000),
    ]
)

doubles_interesting = frozenlist([-3.14159, 3.14159, 4.0e11, 2.998e8, 6.626e-34])

doubles_small = frozenlist(map(float, ints_centered_on(0)))

false = False

ints = frozenlist(range(128))

ints_interesting = frozenlist(mapcat(lambda x: ints_centered_on(x, 2), powers_of_two))

ints_interesting_neg = frozenlist(map(lambda x: -x, ints_interesting))

keywords = [
    keyword("a"),
    keyword("ab"),
    keyword("abc"),
    keyword("abcd"),
    keyword("abcde"),
    keyword("a1"),
    keyword("b2"),
    keyword("c3"),
    keyword("a_b"),
]

list_empty = frozenlist([])
list_mixed = frozenlist(
    [0, 1, 2.0, True, False, "five", keyword("six"), symbol("seven"), "~eight", None]
)
list_simple = frozenlist([1, 2, 3])
list_nested = frozenlist([list_simple, list_mixed])

map_10_items = hash_of_size(10)
map_10_nested = make_hash_exemplar(10)
map_1935_nested = None
map_1936_nested = None
map_1937_nested = None
map_mixed = None
map_nested = None
map_numeric_keys = None
map_simple = None
map_string_keys = None
map_unrecognized_vals = None
map_vector_keys = None
maps_four_char_keyword_keys = None
maps_four_char_string_keys = None
maps_four_char_sym_keys = None
maps_three_char_keyword_keys = None
maps_three_char_string_keys = None
maps_three_char_sym_keys = None
maps_two_char_keyword_keys = None
maps_two_char_string_keys = None
maps_two_char_sym_keys = None
maps_unrecognized_keys = None
nil = None
one = 1
one_date = instant.from_isostr("2000-01-01T12:00:00+00:00")
one_keyword = keyword(v="hello")
one_string = "hello"
one_symbol = None
one_uri = None
one_uuid = None
set_empty = None
set_mixed = None
set_nested = None
set_simple = None
small_ints = None
small_strings = None
strings_hash = None
strings_hat = None
strings_tilde = None
symbols = None
true = True
uris = None
uuids = None
vector_1935_keywords_repeated_twice = None
vector_1936_keywords_repeated_twice = None
vector_1937_keywords_repeated_twice = None
vector_empty = None
vector_mixed = None
vector_nested = None
vector_simple = None
vector_special_numbers = None
vector_unrecognized_vals = None
zero = 0

exemplar_files = [
    ExemplarSpec("cmap_null_key", cmap_null_key),
    ExemplarSpec("cmap_pathological", cmap_pathological),
    ExemplarSpec("dates_interesting", dates_interesting),
    ExemplarSpec("doubles_interesting", doubles_interesting),
    ExemplarSpec("doubles_small", doubles_small),
    ExemplarSpec("false", false),
    ExemplarSpec("ints", ints),
    ExemplarSpec("ints_interesting", ints_interesting),
    ExemplarSpec("ints_interesting_neg", ints_interesting_neg),
    ExemplarSpec("keywords", keywords),
    ExemplarSpec("list_empty", list_empty),
    ExemplarSpec("list_mixed", list_mixed),
    ExemplarSpec("list_nested", list_nested),
    ExemplarSpec("list_simple", list_simple),
    ExemplarSpec("map_10_items", map_10_items),
    ExemplarSpec("map_10_nested", map_10_nested),
    # ExemplarSpec("map_1935_nested", map_1935_nested),
    # ExemplarSpec("map_1936_nested", map_1936_nested),
    # ExemplarSpec("map_1937_nested", map_1937_nested),
    # ExemplarSpec("map_mixed", map_mixed),
    # ExemplarSpec("map_nested", map_nested),
    # ExemplarSpec("map_numeric_keys", map_numeric_keys),
    # ExemplarSpec("map_simple", map_simple),
    # ExemplarSpec("map_string_keys", map_string_keys),
    # ExemplarSpec("map_unrecognized_vals", map_unrecognized_vals),
    # ExemplarSpec("map_vector_keys", map_vector_keys),
    # ExemplarSpec("maps_four_char_keyword_keys", maps_four_char_keyword_keys),
    # ExemplarSpec("maps_four_char_string_keys", maps_four_char_string_keys),
    # ExemplarSpec("maps_four_char_sym_keys", maps_four_char_sym_keys),
    # ExemplarSpec("maps_three_char_keyword_keys", maps_three_char_keyword_keys),
    # ExemplarSpec("maps_three_char_string_keys", maps_three_char_string_keys),
    # ExemplarSpec("maps_three_char_sym_keys", maps_three_char_sym_keys),
    # ExemplarSpec("maps_two_char_keyword_keys", maps_two_char_keyword_keys),
    # ExemplarSpec("maps_two_char_string_keys", maps_two_char_string_keys),
    # ExemplarSpec("maps_two_char_sym_keys", maps_two_char_sym_keys),
    # ExemplarSpec("maps_unrecognized_keys", maps_unrecognized_keys),
    ExemplarSpec("nil", nil),
    ExemplarSpec("one", one),
    ExemplarSpec("one_date", one_date),
    ExemplarSpec("one_keyword", one_keyword),
    ExemplarSpec("one_string", one_string),
    # ExemplarSpec("one_symbol", one_symbol),
    # ExemplarSpec("one_uri", one_uri),
    # ExemplarSpec("one_uuid", one_uuid),
    # ExemplarSpec("set_empty", set_empty),
    # ExemplarSpec("set_mixed", set_mixed),
    # ExemplarSpec("set_nested", set_nested),
    # ExemplarSpec("set_simple", set_simple),
    # ExemplarSpec("small_ints", small_ints),
    # ExemplarSpec("small_strings", small_strings),
    # ExemplarSpec("strings_hash", strings_hash),
    # ExemplarSpec("strings_hat", strings_hat),
    # ExemplarSpec("strings_tilde", strings_tilde),
    # ExemplarSpec("symbols", symbols),
    ExemplarSpec("true", true),
    # ExemplarSpec("uris", uris),
    # ExemplarSpec("uuids", uuids),
    # ExemplarSpec("vector_1935_keywords_repeated_twice", vector_1935_keywords_repeated_twice),
    # ExemplarSpec("vector_1936_keywords_repeated_twice", vector_1936_keywords_repeated_twice),
    # ExemplarSpec("vector_1937_keywords_repeated_twice", vector_1937_keywords_repeated_twice),
    # ExemplarSpec("vector_empty", vector_empty),
    # ExemplarSpec("vector_mixed", vector_mixed),
    # ExemplarSpec("vector_nested", vector_nested),
    # ExemplarSpec("vector_simple", vector_simple),
    # ExemplarSpec("vector_special_numbers", vector_special_numbers),
    # ExemplarSpec("vector_unrecognized_vals", vector_unrecognized_vals),
    ExemplarSpec("zero", zero),
]

reader = TransitReader()

# exemplar_files = [
#     ExemplarSpec("cmap_pathological", cmap_pathological),
# ]


@params(*exemplar_files)
def test_exemplar(spec: ExemplarSpec):
    verbose_file = f"./tests/test_data/simple/{spec.name}.verbose.json"
    verbose_txt = Path(verbose_file).read_text()
    verbose_tree = reader.read(verbose_txt)
    # pprint(verbose_tree)
    assert (
        verbose_tree == spec.expected
    ), f"verbose: {verbose_tree} did not match {spec.expected}"

    cache_file = verbose_file.replace(".verbose.json", ".json")
    cache_txt = Path(cache_file).read_text()
    cache_tree = reader.read(cache_txt)
    # pprint(cache_tree)
    assert (
        cache_tree == spec.expected
    ), f"cache: {cache_tree} did not match {spec.expected}"
