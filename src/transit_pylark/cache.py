import time

from dataclasses import dataclass

from .types import CacheHandle, keyword, symbol, mapkey, transit_tag


class TransitCacheControl:
    """
    implementation of the reader cache logic for transit format
    """

    CACHE_CODE_DIGITS = 44
    BASE_CHAR_INDEX = 48
    SUB_STR = "^"
    MAX_CACHE_SIZE = CACHE_CODE_DIGITS * CACHE_CODE_DIGITS

    CACHE_MAP_TOKEN = "^ "
    CACHE_TOKEN = "CACHECODE:^"

    def __init__(self):
        self.reset()
        self.cache_enabled = True
        self.__cache = {}

    def set_cache_enabled(self, enable: bool):
        # print("Setting cache enforce to:", enforce)
        self.cache_enabled = enable

    def reset(self):
        # print("Initializing fresh cache stack")
        # self.cache = {}
        self.cursor = 0

    def get_cached_item(self, token):
        """trade in a cache token for a cache entry"""
        round = TransitCacheControl.code_to_index(token)
        popped = self.__cache[round]
        # print("popped!", popped)
        return popped

    def ack_cache_control(self, item: CacheHandle, res):
        if self.cache_enabled:
            # print("thanks for popping", self.cursor, len(self.cache), item, self.cache.keys())
            # cursor = self.cache[item]
            # del self.cache[item]
            self.__cache[item.cursor] = res

    def syn_cache_control(self, item):
        """We need to grab our ID as soon as we see the cacheable token - not AFTER parsing the token!"""
        if self.cache_enabled:
            # if: I DONT THINK I SHOULD CACHE THIS
            # then quick return!
            interesting_type = False

            item_type = type(item)

            if item_type is keyword or item_type is symbol:
                interesting_type = True

            if item_type is transit_tag:
                interesting_type = True

            if item_type is mapkey:
                interesting_type = True

            if not interesting_type:
                return item

            if len(item) == 1:
                return item

            if self.cursor > TransitCacheControl.MAX_CACHE_SIZE:
                self.reset()
            # print("thanks for adding", self.cursor, len(self.cache), item)

            # TODO: we might not always want to hand out a cache handle
            # like if item is a very tiny 1 char object?

            handle = CacheHandle(
                cursor=self.cursor,
                item=item,
            )
            # self.cache[handle] = self.cursor
            self.cursor += 1
            return handle
        else:
            return item
            # print(self.control_stack)

    def __cache_analysis(self, value):
        v_type = type(value)
        res = dict(should_cache=False, v_type=v_type, cache_token=None)
        # print("running cache analysis", v_type, value)
        if v_type is str:
            v_size = len(value)
            if value == self.CACHE_MAP_TOKEN:
                res["v_type"] = "map-token"
                return res
            # else:
            # res["should_cache"] = v_size > 3
            # from transit spec:
        elif v_type is mapkey:
            # Strings more than 3 characters long are also cached when they are used as keys in maps whose keys are all "stringable"
            # pass
            # print("wow a mapkey!", value)
            v_size = len(value)
            res["should_cache"] = v_size > 3
        elif v_type is keyword or v_type is symbol:
            v_size = len(value)
            res["should_cache"] = v_size > 1

        return res

    @staticmethod
    def index_to_code(index: int) -> str:
        CACHE_CODE_DIGITS = TransitCacheControl.CACHE_CODE_DIGITS
        BASE_CHAR_INDEX = TransitCacheControl.BASE_CHAR_INDEX
        SUB_STR = TransitCacheControl.SUB_STR
        hi: int = int(index / CACHE_CODE_DIGITS)
        lo: int = index % CACHE_CODE_DIGITS
        if hi == 0:
            return SUB_STR + chr(lo + BASE_CHAR_INDEX)
        else:
            return SUB_STR + chr(hi + BASE_CHAR_INDEX) + chr(lo + BASE_CHAR_INDEX)

    @staticmethod
    def code_to_index(s: str) -> int:
        CACHE_CODE_DIGITS = TransitCacheControl.CACHE_CODE_DIGITS
        BASE_CHAR_INDEX = TransitCacheControl.BASE_CHAR_INDEX
        SUB_STR = TransitCacheControl.SUB_STR
        sz = len(s)
        if sz == 2:
            return ord(s[1]) - BASE_CHAR_INDEX
        else:
            return ((ord(s[1]) - BASE_CHAR_INDEX) * CACHE_CODE_DIGITS) + (
                ord(s[2]) - BASE_CHAR_INDEX
            )
