from collections.abc import Callable, Hashable, MutableSequence

def combine_text(text : list[str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]], add_newlines : bool = True) -> list[str | tuple[Hashable, str]]:
    new_list : list[str | tuple[Hashable, str]] = []
    for x in text:
        if add_newlines and x != text[0]:
            new_list.append("\n")
        if isinstance(x, str) or isinstance(x, tuple):
            new_list.append(x)
        elif x == None:
            continue
        else:
            for y in x:
                new_list.append(y)
    return new_list

def tab_text(text : list[str | tuple[Hashable, str]]) -> list[str | tuple[Hashable, str]]:
    new_list : list[str | tuple[Hashable, str]] = ["    "]
    for x in text:
        new_list.append(x)
        if x == "\n":
            new_list.append("    ")
    return new_list