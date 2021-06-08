"""Lists with features vnv.cli needs for arg parsing."""


class ChainList:
    """List-like access object for a series of sub-lists."""

    def __init__(self, *spans):
        self.spans = list(spans)

    def __contains__(self, key):
        return any(key in span for span in self.spans)

    def __delitem__(self, key):
        span, index = self._access(key)
        del span[index]

    def __getitem__(self, key):
        span, index = self._access(key)
        return span[index]

    def __iter__(self):
        for span in self.spans:
            yield from span

    def __len__(self):
        return sum(map(len, self.spans))

    def __repr__(self):
        args = ', '.join(map(repr, self.spans))
        return f'{type(self).__name__}({args})'

    def __setitem__(self, key, value):
        span, index = self._access(key)
        span[index] = value

    def _access(self, key):
        """Find the underlying span and index for `self[key]`."""
        if isinstance(key, slice):
            raise TypeError(f'{type(self).__name__} slicing is not supported')
        if key < 0:
            key += len(self)
        if key >= 0:
            index = key
            for span in self.spans:
                if index < len(span):
                    return span, index
                index -= len(span)
        raise IndexError(f'{type(self).__name__} index out of range')

    def count(self, value):
        return sum(span.count(value) for span in self.spans)

    def index(self, value):
        for span in self.spans:
            try:
                return span.index(value)
            except ValueError:
                pass
        raise ValueError(f'{value!r} is not in {type(self).__name__}')

    def pop(self, index=-1):
        span, span_index = self._access(index)
        return span.pop(span_index)

    def remove(self, value):
        for span in self.spans:
            try:
                span.remove(value)
                return
            except ValueError:
                pass
        raise ValueError(f'{value!r} is not in {type(self).__name__}')
