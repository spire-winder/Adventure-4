import sys
from systems.event_system import Event
import systems.event_system
import systems.save_system
from classes.interactable import *
from classes.actions import *
import classes.actions

import typing
if typing.TYPE_CHECKING:
    from collections.abc import Callable, Hashable, MutableSequence

class Dungeon:
    def __init__(self):
        self.map : dict[str:Room] = systems.save_system.load_map("standard")
        self.new_game_setup()
        self.ui_event = Event()
        self.save_game_event = Event()
        self.game_over = False

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
        self.player : Player= self.place.get_player()

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
    
    def get_location_of_actor(self, actor : Actor) -> Room:
        if isinstance(actor, Room):
            return actor
        for x in self.map.values():
            if actor in x.room_contents:
                return x
        return None
        
    def start_game(self) -> None:
        self.connect_signals()
        self.start_round()

    def start_round(self) -> None:
        self.messagequeue = []
        self.generate_action_queue()
        self.current_interactable : Interactable = None
        self.previous_interactable : Interactable = None
        utility.log("starting round!")
        self.actor : Actor = self.player
        self.place = self.get_location_of_actor(self.actor)
        self.place.interact()
    
    def generate_action_queue(self):
        self.action_queue : list = []
        for x in self.map:
            self.map[x].add_to_action_queue(self.action_queue)
    
    def current_action_visible(self):
        return self.place == self.get_location_of_actor(self.player) or (self.get_location_of_actor(self.player)) in self.place.get_roomobjects()

    def actor_visible(self, actor : Actor):
        loc = self.get_location_of_actor(actor)
        if loc == None:
            return False
        return loc == self.get_location_of_actor(self.player) or (self.get_location_of_actor(self.player)) in loc.get_roomobjects()

    def add_to_message_queue(self, msg : str | tuple["Hashable", str] | list[str | tuple["Hashable", str]]):
        self.messagequeue.append(msg)
    
    def add_to_message_queue_if_visible(self, msg : str | tuple["Hashable", str] | list[str | tuple["Hashable", str]]):
        if self.current_action_visible():
            self.add_to_message_queue(msg)

    def add_to_message_queue_if_actor_visible(self, actor : Actor, msg : str | tuple["Hashable", str] | list[str | tuple["Hashable", str]]):
        if self.actor_visible(actor):
            self.add_to_message_queue(msg)

    def show_message_queue(self):
        self.ui_event.emit(action=classes.actions.MessageQueueAction(self.messagequeue))

    def update_location(self):
        self.place = self.get_location_of_actor(self.actor)

    def start_next_turn(self):
        if len(self.action_queue) == 0:
            utility.log("we're ending the round!")
            #self.actor : Actor = None
            self.end_of_round()
            utility.log("we're showing the queue!")
            self.show_message_queue()
        else:
            self.actor : Actor = self.action_queue.pop()
            self.update_location()
            if self.actor != None and self.place != None:
                utility.log(str(self.actor.get_name()) + " taking turn")
                self.actor.take_turn(self)
            else:
                self.end_current_turn()

    def end_of_round(self):
        chain : list = [self]
        for x in self.map:
            self.map[x].end_of_round(chain)

    def end_current_turn(self):
        utility.log("turn ended!")
        self.start_next_turn()

    def player_interact(self, inter : classes.actions.PlayerInteractAction):
        self.ui_event.emit(classes.actions.InteractAction(inter))
    
    def apply_statics(self, effect : Effect):
        chain : list = [self]
        self.place.apply_statics(chain, effect)