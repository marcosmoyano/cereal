from .utils import get_attribute_or_key
from typing import Any, Callable, Iterator, Union

__all__ = ['Field', 'ConstantField', 'IteratorField', 'SerializerField']


class Field:
    """ The base field for all other fields.
        Acts as a pass-through to the underlying object or dict.
    """
    pass


class ConstantField(Field):
    """ Returns a constant value each time the field is evaluated.
    """

    def __init__(self, value):
        self._value = value

    def value(self, obj, name: str):
        return self._value


class SerializerField(Field):

    def __init__(self, serializer: Callable) -> None:
        self._serializer = serializer()

    def value(self, obj, name: str):
        other = get_attribute_or_key(obj, name)
        if isinstance(other, (list, tuple, set)):
            return [self._serializer.asdict_(o) for o in other]
        elif hasattr(other, 'objects'):
            return [self._serializer.asdict_(o) for o in other.objects.all()]
        return self._serializer.asdict_(other)


class IteratorField(Field):
    """ Returns next value from iterator until StopIteration occurs.
        Once the iterator has been exhausted, this field will return None.
    """

    def __init__(self, container: Iterator[Any]) -> None:
        self._iter: Union[Iterator[Any], None] = iter(container)

    def value(self, obj, name: str):
        """ Return next value from the iterator
            or None if StopIteration has occured.
        """
        if self._iter:
            try:
                v = next(self._iter)
                return v
            except StopIteration:
                self._iter = None
