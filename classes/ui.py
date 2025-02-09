from __future__ import annotations
import urwid
import typing
if typing.TYPE_CHECKING:
    from collections.abc import Callable, Hashable, MutableSequence

base_palette = [
    ("stone", "light gray", ""),
    ("iron", "dark gray", ""),
    ("wood", "brown", ""),
    ("magic", "light magenta", ""),
    ("header", "white", "dark gray")
]

unique_palette = [
    ("reversed", "standout", "")
]

full_palette = []
for x in base_palette:
    old_x = tuple(x)
    full_palette.append(x)
    name = old_x[0] + "_standout"
    attr = old_x[1] + ",standout"
    new_x = (name, attr, "default")
    full_palette.append(new_x)
for x in unique_palette:
    full_palette.append(x)
    
focus_dict = {None:"reversed"}

for x in base_palette:
    focus_dict[x[0]] = "reversed"


class ActionButton(urwid.Button):
    def __init__(
        self,
        caption: str | tuple["Hashable", str] | list[str | tuple["Hashable", str]],
        callback: Callable[[ActionButton], typing.Any],
    ) -> None:
        super().__init__("", on_press=callback)
        self._w = urwid.AttrMap(urwid.SelectableIcon(caption, 0), None, focus_map=focus_dict)
