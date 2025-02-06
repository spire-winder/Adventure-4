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
        self._w = urwid.AttrMap(urwid.SelectableIcon(caption, 0), None, focus_map="reversed")

class Room(urwid.WidgetWrap[ActionButton]):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], room_contents : MutableSequence[RoomObject]) -> None:
        super().__init__(ActionButton([" > go to ", name], self.enter_place))
        self.heading : urwid.Widget = urwid.Text(["Location: ", name])
        self.choices : MutableSequence[RoomObject] = room_contents
    
    def enter_place(self, button:ActionButton) -> None:
        pass

    def add_roomobject(self, obj_to_add : RoomObject) -> None:
        self.choices.append(obj_to_add)

    def remove_roomobject(self, obj_to_remove : RoomObject) -> bool:
        for x in self.choices:
            if x == obj_to_remove:
                self.choices.remove(x)
                return True
        return False
    
    def get_nonplayers(self) -> list[RoomObject]:
        new_list : list[RoomObject] = []
        for x in self.choices:
            if not isinstance(x, Player):
                new_list.append(x)
        return new_list

class RoomObject(urwid.WidgetWrap[ActionButton]):
    def __init__(self, name:str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]) -> None:
        super().__init__(ActionButton([name], self.interact))
        self.name = name
    
    def interact(self, button:ActionButton) -> None:
        pass

    def take_turn(self, advgame : AdventureGame) -> None:
        advgame.end_current_turn()

class Item(RoomObject):
    def interact(self, button : ActionButton) -> None:
        game.take_thing(self)

class Entity(RoomObject):
    def interact(self, button : ActionButton) -> None:
        pass

class Player(Entity):
    def take_turn(self, advgame : AdventureGame) -> None:
        game.room_center()

class Passage(RoomObject):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], destination_id : str):
        super().__init__(name)
        self.destination_id : str = destination_id
    
    def interact(self, button : ActionButton) -> None:
        game.enter_passage(self)

map : dict = {
    "map_top": Room("Starting room", [Passage(("stone", u"Stone door"),"stone_room"), Passage(("iron",u"Iron door"),"iron_room"), Item(("wood", u"Wooden Sword"))]),
    "stone_room": Room(("stone", u"Stone Room"), [Passage(("wood", u"Wooden door"),"map_top"), Passage(("iron",u"Iron door"),"iron_room"), Item(("magic", "Glyph-covered arm")), Item(("wood", u"Wooden Shield"))]),
    "iron_room": Room(("iron", u"Iron Room"), [Passage(("stone", u"Stone door"),"stone_room"), Passage(("wood", u"Wooden door"),"map_top"), Item(("magic", u"Dragon Dreams"))]),
}

class AdventureGame:
    def __init__(self) -> None:
        self.header : urwid.Widget = urwid.AttrMap(urwid.Text("Adventure 4", align="center"), "header")
        self.center : urwid.Widget = urwid.ListBox(urwid.SimpleFocusListWalker([ActionButton("Start", self.start_game)]))
        self.top : urwid.Frame = urwid.Frame(self.center, header=self.header)
        self.inventory = set()
        self.init_location("map_top")
        self.player = Player("Player Name")
        self.place.add_roomobject(self.player)
    
    def change_center(self, new_center : urwid.Widget):
        self.top.body = urwid.SolidFill(" ")
        loop.draw_screen()
        time.sleep(0.1)
        self.center = new_center
        self.top.body = self.center

    def return_to_room(self, button : urwid.Button):
        self.room_center()

    def room_center(self):
        center_widget : urwid.ListBox = urwid.ListBox(urwid.SimpleFocusListWalker([self.place.heading, urwid.Divider(), *self.place.get_nonplayers()]))
        self.change_center(center_widget)
    
    def notif_center(self, message : str):
        li : list = []
        li.append(urwid.Text(message))
        li.append(urwid.Divider())
        li.append(ActionButton(["Okay"], self.return_to_room))
        notif_widget = urwid.ListBox(urwid.SimpleFocusListWalker(li))
        self.change_center(notif_widget)

    def enter_passage(self, passage : Passage):
        if not passage.destination_id in map:
            sys.exit('Room ID not found in map!')
        place : Room = map[passage.destination_id]
        self.place.remove_roomobject(self.actor)
        self.place : Room = place
        self.place.add_roomobject(self.actor)
        self.add_to_message_queue(urwid.Text([self.actor.name, " entered the ", passage.name, "."]))
        self.end_current_turn()
    
    def init_location(self, destination_id : str):
        if not destination_id in map:
            sys.exit('Room ID not found in map!')
        place : Room = map[destination_id]
        self.place : Room = place
        #center_widget : urwid.ListBox = urwid.ListBox(urwid.SimpleFocusListWalker([self.place.heading, urwid.Divider(), *self.place.get_nonplayers()]))
        #self.center = center_widget
        #self.top.body = self.center

    def take_thing(self, thing : Item) -> None:
        if not self.place.remove_roomobject(thing):
            sys.exit('Object not found in room!')
        self.inventory.add(thing.name)
        self.add_to_message_queue(urwid.Text([self.actor.name, " picked up the ", thing.name, "."]))
        self.end_current_turn()

    def add_to_message_queue(self, message : str):
        self.messagequeue.append(message)

    def show_message_queue(self):
        li : list = self.messagequeue
        li.append(urwid.Divider())
        li.append(ActionButton(["Okay"], self.end_round))
        notif_widget = urwid.ListBox(urwid.SimpleFocusListWalker(li))
        self.change_center(notif_widget)

    def start_game(self, button : ActionButton) -> None:
        self.start_round()

    def start_round(self) -> None:
        self.messagequeue = []
        self.actionqueue = self.place.get_nonplayers()
        self.actionqueue.append(self.player)
        self.start_next_turn()
    
    def start_next_turn(self):
        if len(self.actionqueue) == 0:
            self.show_message_queue()
        else:
            self.actor : RoomObject = self.actionqueue[-1]
            self.actionqueue.pop(-1)
            self.actor.take_turn(self)

    def end_current_turn(self):
        self.start_next_turn()

    def end_round(self, button : ActionButton) -> None:
        self.start_round()

palette = [
    ("stone", "light gray", ""),
    ("iron", "dark gray", ""),
    ("wood", "brown", ""),
    ("magic", "light magenta", ""),
    ("reversed", "standout", "")
]

game = AdventureGame()
loop = urwid.MainLoop(game.top, palette=palette)
loop.run()