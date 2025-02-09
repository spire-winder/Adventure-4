from classes.ui import ActionButton
import data.maps
import sys
import urwid
import typing
from systems.event_system import Event
from classes.roomobjects import Player
from classes.roomobjects import RoomObject
from classes.rooms import Room
import classes.actions

class Dungeon:
    def __init__(self, map : dict):
        self.map : dict = map
        self.set_center_event = Event()
        self.save_game_event = Event()
        self.debug_event = Event()

    def new_game_setup(self):
        self.init_location("starting_room")
        self.player = self.place.get_player()

    def locate_player(self):
        for room in self.map.keys():
            if self.map[room].get_player() != None:
                return room
        return None

    def load_game_setup(self):
        loc_id = self.locate_player()
        if loc_id == None:
            sys.exit('Player not found!')
        self.init_location(loc_id)
        self.player = self.place.get_player()

    def connect_signals(self):
        for room in self.map.values():
            for roomobj in room.choices:
                roomobj.handle_connecting_signals(self)

    def roomobject_event(self, action : classes.actions.InteractionAction):
        if action != None:
            action.execute(self, self.actor)
        else:
            self.end_current_turn()

    def init_location(self, destination_id : str):
        if not destination_id in self.map:
            sys.exit('Room ID not found in map!')
        self.place : Room = self.map[destination_id]
    
    def start_game(self) -> None:
        self.connect_signals()
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
            self.actor.take_turn()

    def add_to_message_queue(self, message):
        self.messagequeue.append(urwid.Text(message))

    def return_to_room(self, button : urwid.Button):
        self.room_center()

    def room_center(self):
        roomobjects = self.place.get_nonplayers()
        room_list = []
        room_list.append(urwid.Text(["Location: ", self.place.name]))
        room_list.append(urwid.Divider())
        for x in roomobjects:
            room_list.append(ActionButton(x.name, x.interact))
        room_list.append(ActionButton("Save and Quit", self.save_and_quit))
        center_widget : urwid.ListBox = urwid.ListBox(urwid.SimpleFocusListWalker(room_list))
        self.set_center_event.emit(new_center=center_widget)
    
    def show_message_queue(self):
        li : list = self.messagequeue
        li.append(urwid.Divider())
        li.append(ActionButton(["Okay"], self.end_round))
        notif_widget = urwid.ListBox(urwid.SimpleFocusListWalker(li))
        self.set_center_event.emit(new_center=notif_widget)

    def end_current_turn(self):
        self.start_next_turn()

    def save_and_quit(self, button : ActionButton) -> None:
        self.save_game_event.emit()

    def end_round(self, button : ActionButton) -> None:
        self.start_round()
