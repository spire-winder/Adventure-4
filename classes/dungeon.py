import sys
from systems.event_system import Event
import systems.save_system
from classes.interactable import Interactable
from classes.interactable import Player
from classes.interactable import RoomObject
from classes.interactable import Room
import classes.actions

import typing
if typing.TYPE_CHECKING:
    from collections.abc import Callable, Hashable, MutableSequence

class Dungeon:
    def __init__(self):
        self.map : dict = systems.save_system.load_map("standard")
        self.new_game_setup()
        self.ui_event = Event()
        self.save_game_event = Event()

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the event reference before pickling.
        if 'ui_event' in state:
            state['ui_event'] = Event()
        if 'save_game_event' in state:
            state['save_game_event'] = Event()
        return state

    def new_game_setup(self):
        self.init_location("starting_room")
        self.player = self.place.get_player()

    def connect_signals(self):
        for room in self.map.values():
            room.handle_connecting_signals(self)

    def interaction_event(self, action : classes.actions.InteractionAction):
        if action != None:
            action.execute(self)
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
        self.actionqueue = self.place.room_contents.copy()
        self.actor = self.player
        self.place.interact()
    
    def add_to_message_queue(self, msg : str | tuple["Hashable", str] | list[str | tuple["Hashable", str]]):
        self.messagequeue.append(msg)
    
    def show_message_queue(self):
        self.ui_event.emit(action=classes.actions.MessageQueueAction(self.messagequeue))

    def start_next_turn(self):
        if len(self.actionqueue) == 0:
            self.show_message_queue()
        else:
            self.actor : RoomObject = self.actionqueue[-1]
            self.actionqueue.pop(-1)
            self.actor.take_turn()

    def end_current_turn(self):
        self.start_next_turn()

    def interact(self, inter : Interactable):
        self.ui_event.emit(classes.actions.InteractAction(inter))