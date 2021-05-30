"""Lists with features vnv.cli needs for arg parsing."""


class Betterment:
    """Better popping features."""

    def eject(self, item):
        """Try to find and remove the item, returning whether it was found."""
        try:
            self.remove(item)
        except ValueError:
            return False
        return True

    def get(self, index, default=None):
        """Like `dict.get`."""
        try:
            return self[index]  # pylint: disable=unsubscriptable-object
        except IndexError:
            return default

    def safepop(self, index=-1, default=None):
        """Like `dict.pop`."""
        try:
            return self.pop(index)
        except IndexError:
            return default


class BetterList(list, Betterment):
    """List with better popping features."""


class ChainList(Betterment):
    """List-like access object for a series of sub-lists."""

    def __init__(self, *links):
        self.links = list(links)

    def __contains__(self, key):
        return any(key in link for link in self.links)

    def __delitem__(self, key):
        link, index = self._access(key)
        del link[index]

    def __getitem__(self, key):
        link, index = self._access(key)
        return link[index]

    def __iter__(self):
        for link in self.links:
            yield from link

    def __len__(self):
        return sum(map(len, self.links))

    def __repr__(self):
        args = ', '.join(map(repr, self.links))
        return f'{type(self).__name__}({args})'

    def __setitem__(self, key, value):
        link, index = self._access(key)
        link[index] = value

    def _access(self, key):
        """Find `link` and `i` such that `self[key]` <-> `link[i]`."""
        if key < 0:
            key += len(self)
        if key >= 0:
            index = key
            for link in self.links:
                if index < len(link):
                    return link, index
                index -= len(link)
        raise IndexError(f'{type(self).__name__} index out of range')

    def copy(self):
        return type(self)(*self.links)

    def count(self, value):
        return sum(link.count(value) for link in self.links)

    def index(self, value):
        for link in self.links:
            try:
                return link.index(value)
            except ValueError:
                pass
        raise ValueError(f'{value!r} is not in {type(self).__name__}')

    def pop(self, index=-1):
        link, link_index = self._access(index)
        return link.pop(link_index)

    def remove(self, value):
        for link in self.links:
            try:
                link.remove(value)
                return
            except ValueError:
                pass
        raise ValueError(f'{value!r} is not in {type(self).__name__}')
