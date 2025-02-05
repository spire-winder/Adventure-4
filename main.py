from __future__ import annotations
import typing
import urwid
import sys
import time
if typing.TYPE_CHECKING:
    from collections.abc import Callable, Hashable, MutableSequence

import os
os.system('title Adventure 4')

class ActionButton(urwid.Button):
    def __init__(
        self,
        caption: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
        callback: Callable[[ActionButton], typing.Any],
    ) -> None:
        super().__init__("", on_press=callback)
        self._w = urwid.AttrMap(urwid.SelectableIcon(caption, 1), None, focus_map="reversed")

class Room(urwid.WidgetWrap[ActionButton]):
    def __init__(self, name : str, room_contents : MutableSequence[RoomObject]) -> None:
        super().__init__(ActionButton([" > go to ", name], self.enter_place))
        self.heading : urwid.Widget = urwid.Text("Location: " + name)
        self.choices : MutableSequence[RoomObject] = room_contents
    
    def enter_place(self, button:ActionButton) -> None:
        pass

    def remove_roomobject(self, obj_to_remove : RoomObject) -> bool:
        for x in self.choices:
            if x == obj_to_remove:
                self.choices.remove(x)
                return True
        return False

class RoomObject(urwid.WidgetWrap[ActionButton]):
    def __init__(self, name:str) -> None:
        super().__init__(ActionButton([name], self.interact))
        self.name = name
    
    def interact(self, button:ActionButton) -> None:
        pass

class Item(RoomObject):
    def interact(self, button : ActionButton) -> None:
        game.take_thing(self)

class Passage(RoomObject):
    def __init__(self, name : str, destination_id : str):
        super().__init__(name)
        self.destination_id : str = destination_id
    
    def interact(self, button : ActionButton) -> None:
        game.change_location(self.destination_id)

map_top = Room("Starting room", [RoomObject("thing 1"), RoomObject("thing 2")])

map : dict = {
    "map_top": Room("Starting room", [Passage("Stone door","stone_room"), Passage("Iron door","iron_room"), Item("Wooden Sword")]),
    "stone_room": Room("Stone Room", [Passage("Wooden door","map_top"), Passage("Iron door","iron_room"), Item("Glyph-covered arm"), Item("Wooden Shield")]),
    "iron_room": Room("Iron Room", [Passage("Stone door","stone_room"), Passage("Wooden door","map_top"), Item("Dragon Dreams")]),
}

class AdventureGame:
    def __init__(self) -> None:
        self.center : urwid.Widget = urwid.ListBox(urwid.SimpleFocusListWalker([urwid.Text("Original Body")]))
        self.top : urwid.Frame = urwid.Frame(self.center)
        self.inventory = set()
        self.change_location("map_top")
    
    def change_center(self, new_center : urwid.Widget):
        self.center = new_center
        self.top.body = self.center

    def return_to_room(self, button : urwid.Button):
        self.room_center()

    def room_center(self):
        center_widget : urwid.ListBox = urwid.ListBox(urwid.SimpleFocusListWalker([self.place.heading, urwid.Divider(), *self.place.choices]))
        self.change_center(center_widget)
    
    def notif_center(self, message : str):
        li : list = []
        li.append(urwid.Text(message))
        li.append(urwid.Divider())
        li.append(ActionButton(["Okay "], self.return_to_room))
        notif_widget = urwid.ListBox(urwid.SimpleFocusListWalker(li))
        self.change_center(notif_widget)

    def change_location(self, destination_id : str):
        if not destination_id in map:
            sys.exit('Room ID not found in map!')
        place : Room = map[destination_id]
        self.place = place
        self.room_center()

    def take_thing(self, thing : Item) -> None:
        if self.place.remove_roomobject(thing):
            self.inventory.add(thing.name)
            self.notif_center("You picked up the " + thing.name + ".")
        else:
            sys.exit('Object not found in room!')


game = AdventureGame()
loop = urwid.MainLoop(game.top, palette=[("reversed", "standout", "")])
loop.run()