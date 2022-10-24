from shelve import DbfilenameShelf
from play_config import ENABLE_DIAGNOSTIC_MESSAGES


def debug_print(*args):
    if ENABLE_DIAGNOSTIC_MESSAGES:
        print(*args)


class RecursiveDict(dict):
    # defaultdict but smaller
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

    def __deepcopy__(self, memo):
        return self


class NoCopyShelf(DbfilenameShelf):
    def __deepcopy__(self, memo):
        return self

    def open(filename, flag='c', protocol=None, writeback=False):
        return NoCopyShelf(filename, flag, protocol, writeback)
