from typing import Union, List, Set, Tuple


def format_iterable(iterable = Union[List, Set, Tuple], seperator: str = ",") -> str:
    assert type(iterable) in [list, tuple, set], 'Provide an iterable, either list, set or tuple.'
    return f'{seperator} '.join(iterable)