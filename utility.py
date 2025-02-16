from collections.abc import Callable, Hashable, MutableSequence

def log(msg):
    with open("log.txt", 'a') as f:
        f.write(str(msg) + "\n")
        f.close()

def combine_text(text : list[str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]], add_newlines : bool = True) -> list[str | tuple[Hashable, str]]:
    if text == None:
        return None
    if isinstance(text, str):
        return [text]
    while None in text:
        text.remove(None)
    new_list : list[str | tuple[Hashable, str]] = []
    for x in text:
        if add_newlines and x != text[0]:
            new_list.append("\n")
        if isinstance(x, str) or isinstance(x, tuple):
            new_list.append(x)
        else:
            for y in x:
                if y != None:
                    new_list.append(y)
    return new_list

def tab_text(text : list[str | tuple[Hashable, str]]) -> list[str | tuple[Hashable, str]]:
    if text == None:
        return None
    if isinstance(text, list):
        while None in text:
            text.remove(None)
    if len(text) == 0:
        return None
    new_list : list[str | tuple[Hashable, str]] = ["    "]
    for x in text:
        if x == None:
            continue
        new_list.append(x)
        if x == "\n":
            new_list.append("    ")
    return new_list

def alternate_colors(text : str | list[str], color_sequence : list[str]) -> list[tuple[Hashable, str]]:
    new_text : list[tuple[Hashable, str]] = []
    counter : int = 0
    for x in text:
        if isinstance(x, str):
            for y in x:
                new_text.append((color_sequence[counter % len(color_sequence)], y))
                counter += 1
        else:
            new_text.append((color_sequence[counter % len(color_sequence)], x))
            counter += 1
    return new_text