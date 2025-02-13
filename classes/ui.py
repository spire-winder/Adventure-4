from __future__ import annotations
import urwid
import typing
if typing.TYPE_CHECKING:
    from classes.actions import InteractionAction
    from collections.abc import Callable, Hashable, MutableSequence

base_palette = [
    ("stone", "light gray", ""),
    ("iron", "dark gray", ""),
    ("wood", "brown", ""),
    ("magic", "light magenta", ""),
    ("goblin", "light green", ""),
    ("fire", "light red", ""),
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

class SaveButton(ActionButton):
    def __init__(
        self,
        caption: str | tuple["Hashable", str] | list[str | tuple["Hashable", str]],
        callback: Callable[[ActionButton], typing.Any],
        save_file : str
    ) -> None:
        super().__init__(caption, callback)
        self.save_file = save_file

class InteractableActionButton(urwid.Button):
    def __init__(
        self,
        dungeon,
        action : InteractionAction
    ) -> None:
        self.dungeon = dungeon
        self.action = action
        super().__init__("", self.execute)
        self._w = urwid.AttrMap(urwid.SelectableIcon(self.action.get_name(), 0), None, focus_map=focus_dict)
    
    def execute(self, button):
        self.action.execute(self.dungeon)

class QuestionBox(urwid.Edit):
    def __init__(
        self,
        caption: str | tuple["Hashable", str] | list[str | tuple["Hashable", str]],
        callback: Callable
    ) -> None:
        super().__init__(caption)
        self.callback : Callable = callback
    def keypress(self, size, key: str) -> str | None:
        if key != "enter":
            return super().keypress(size, key)
        else:
            if self.get_edit_text() != "":
                self.callback.__call__()
            return None