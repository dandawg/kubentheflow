from typing import NamedTuple

def hello(
    name: str
) -> NamedTuple("Output", [("greeting", str)]):
    import re
    # check if name matches a single word,
    # 2 or more letters in length,
    # first letter is optionally capitalized
    n = name if re.match('^[A-z][a-z]+$', name) else ''
    s = f"Hello {n}!" if n else "Hello!"
    print(s)
    return (s,)
