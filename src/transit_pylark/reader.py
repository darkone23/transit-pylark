# from pathlib import Path
# import time
# import json

# from rich.pretty import pprint
from lark import Lark, Transformer, Discard, Tree

import time

from .cache import TransitCacheControl, CacheHandle
from .types import (
    frozendict,
    frozenlist,
    instant,
    transit_tag,
    mapkey,
    keyword,
    quoted,
    symbol,
)
from .codecs import TransitTagResolver, TransitDecoder

# basic json grammar needs to be extended to handle transit tagging and caching
# should support user defined extensions in the transformers

TRANSIT_STRING_GRAMMAR = """
value: "~" instruction [ chars ]

instruction: nil
         | escape_tilde
         | escape_hat
         | microtime
         | isotime
         | bool
         | int
         | base64
         | keyword
         | symbol
         | tag

nil: "_"
escape_tilde: "~"
escape_hat: "^"
bool: "?"
base64: "b"
microtime: "m"
isotime: "t"
int: "i" | "n"
keyword: ":"
symbol: "$"
tag: "#"

chars: /.+/
"""

TRANSIT_GRAMMAR = """
value: dict
     | list
     | transit_str
     | transit_num
     | false | true | null

false: "false"
true: "true"
null: "null"

list : "[" [ value ("," value)* ] "]"
dict : "{" [pair ("," pair)*] "}"
pair : transit_str ":" value

transit_str : ESCAPED_STRING
transit_num : SIGNED_NUMBER

%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING
%import common.WS
%ignore WS
"""


class TransitScalarTransformer(Transformer):

    def __init__(self, resolver: TransitTagResolver, control: TransitCacheControl):
        self.resolver = resolver
        self.control = control

    def value(self, args):
        arg_size = len(args)
        if arg_size == 1:
            (v,) = args
            # must be: escape str or nil
            # print("one args???")
            # print("you asked me to resolve a one arg mystery", v)
            res = self.resolver.resolve(k)
            return self.control.syn_cache_control(res)
        elif arg_size == 2:
            (k, v) = args
            # print("two args???", k, v)
            # print("you asked me to resolve a mystery", k, v)
            res = self.resolver.resolve(k, v)
            return self.control.syn_cache_control(res)
        else:
            raise ValueError(f"Unexpected transit str parser len... {len(args)}")

    def chars(self, c):
        (t,) = c
        # (c,) = t.children
        return t

    def instruction(self, s):
        (s,) = s
        return s.data

    # def str(self, s):
    #     (s,) = s
    #     return s

    # def chars(self, s):
    #     (s,) = s
    #     return s


# transformer can be responsible for cache reading layer
class TransitJsonTransformer(Transformer):

    CACHE_MAP_TOKEN = "^ "
    CACHE_TOKEN = "CACHECODE:^"

    def __init__(self, resolver: TransitTagResolver | None = None):
        self.control = TransitCacheControl()
        if resolver is None:
            resolver = TransitTagResolver.default()
        self.resolver = resolver
        self.transit = Lark(
            TRANSIT_STRING_GRAMMAR,
            start="value",
            parser="lalr",
            transformer=TransitScalarTransformer(
                resolver=resolver, control=self.control
            ),
        )

    def value(self, args):
        (s,) = args
        # print("value inspect:", s)
        result = s
        if self.control.cache_enabled:
            # cache_analysis = self.__cache_analysis(s)
            # print("do I think this is cacheable?", cache_analysis)
            if type(s) is CacheHandle:
                # cache_analysis.get("should_cache", False):
                # print("cache handle and committing", s)
                result = self.__commit_to_cache(s, s.item)
            if type(s) is str and s.startswith(self.CACHE_TOKEN):
                token = s[10:]
                result = self.control.get_cached_item(token)
        # print("result inspect:", result)
        return result

    def transit_num(self, args):
        (n,) = args
        return float(n)

    def pair(self, args):
        (k, v) = args
        return (k, v)

    def false(self, args):
        return False

    def true(self, args):
        return True

    def null(self, args):
        return None

    # list = list
    # pair = tuple

    def __list(self, args):
        if len(args) == 0:
            # print("empty list")
            return []
        if len(args) == 1:
            (s,) = args
            # print("list of one", args, s)
            return [s]
        else:
            head = args[0]
            # print("list", head, args)
            if head == self.CACHE_MAP_TOKEN:
                res = {}
                for n in range(int(len(args) / 2)):
                    idx = n * 2 + 1
                    # print("searching for ", idx, args[idx:idx+2])
                    (k, v) = args[idx : idx + 2]
                    res[mapkey(k)] = v
                return res
            else:
                return args

    def __dict(self, args):
        res = {}
        for pair in args:
            (k, v) = pair
            res[mapkey(k)] = v
        return res

    def __emit_dict(self, xs):
        if len(xs) and transit_tag.is_transit_tag(next(iter(xs.keys())).k):
            return self.__transit_tagged_dict(xs)
        obj = {}
        for k, v in xs.items():
            if type(k) is mapkey:
                obj[k.k] = v
            else:
                obj[k] = v
        return frozendict(obj)

    def dict(self, args):
        # print("I think I am a dict before a value...", args)
        xs = self.__dict(args)
        return self.__emit_dict(xs)

    def __commit_to_cache(self, key, res):
        # # code = TransitCacheControl.index_to_code(next)
        # # round = TransitCacheControl.code_to_index(code)
        # print("Adding to cache", res, self.control.control_stack)
        if self.control.cache_enabled:
            # print("At this time I am saving to the cache:", key, res)
            self.control.ack_cache_control(key, res)
        return res

    def __transit_tagged_list(self, xs):
        assert len(xs) == 2, "I don't know what to do with more than 2 entries"
        (k, v) = xs
        # print("dealing with transit tag list", type(k), k, v)
        tag_key = transit_tag.tag_key(k)
        res = self.resolver.resolve(tag_key, v)
        if type(k) is CacheHandle:
            return self.__commit_to_cache(k, res)
        else:
            return res

    def __transit_tagged_dict(self, xs):
        assert len(xs) == 1, "I don't know what to do with more than 2 entries"
        (k, v) = next(iter(xs.items()))
        if type(k) is mapkey:
            k = k.k
        # print("dealing with transit tag dict", type(k), k, v)
        tag_key = transit_tag.tag_key(k)
        res = self.resolver.resolve(tag_key, v)
        if type(k) is CacheHandle:
            return self.__commit_to_cache(k, res)
        else:
            return res

    def list(self, args):
        if args == [None]:
            return frozenlist([])
        xs = self.__list(args)
        # print("dealing with a list", xs, args, type(args))
        if type(xs) is dict:
            return self.__emit_dict(xs)
        elif len(xs) and transit_tag.is_transit_tag(xs[0]):
            # print("it is a transit list", xs)
            return self.__transit_tagged_list(xs)
        # print("about to make my result list:", xs)
        return frozenlist(xs)

    def transit_str(self, args):
        # self.parser.parse()
        (s,) = args
        encoded_str = str(s)
        # print("you casked me to handle trnsit str?", encoded_str)
        transit_part = encoded_str[1:-1]  # not needing "" parts of str
        if transit_part.startswith("~"):
            # special transit escaped string
            result = self.transit.parse(transit_part)
            # try:
            # except Exception as e:
            #     print("Exception parsing transit encoded str node!", e)
            #     # print(e)
            #     result = transit_part
        elif self.control.cache_enabled and transit_part.startswith("^"):
            # special cache instruction
            remainder = transit_part[1:]
            if remainder == " ":
                result = self.CACHE_MAP_TOKEN
            else:
                result = self.CACHE_TOKEN + remainder
        else:
            result = transit_part

        if type(result) is CacheHandle:
            if not transit_tag.is_transit_tag(result.item):
                result = self.__commit_to_cache(result, result.item)
        # print("result of transit str", result)
        return result


class TransitReader:

    def __init__(self):

        # from rich.pretty import pprint
        self.xformer = TransitJsonTransformer()
        self.parser: Lark = Lark(
            TRANSIT_GRAMMAR,
            start="value",
            parser="lalr",
            transformer=self.xformer,
        )

    def read(self, obj, enable_cache: bool = True, unquote_top: bool = True):
        # TODO: wouldn't hurt to add a threading lock here
        try:
            self.xformer.control.set_cache_enabled(enable_cache)
            parsed = self.parser.parse(obj)
            if unquote_top and type(parsed) is quoted:
                return parsed.v
            else:
                return parsed
        finally:
            self.xformer.control.reset()
