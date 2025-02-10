import typing
from collections.abc import Callable, Hashable, MutableSequence
from systems.event_system import Event
import classes.actions

class Interactable:
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]) -> None:
        self.name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]] = name
        self.event = Event()
    def get_choices(self) -> MutableSequence[classes.actions.InteractionAction]:
        return []
    def interact_wrapper(self, button) -> None:
        self.interact()
    def interact(self) -> None:
        self.event.emit(action=classes.actions.PlayerInteractAction(self))
    def handle_connecting_signals(self, dungeon):
        self.event.subscribe(dungeon.interaction_event)

class RoomObject(Interactable):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]) -> None:
        super().__init__(name)
    def take_turn(self) -> None:
        self.event.emit(action=None)

class Item(RoomObject):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]]) -> None:
        super().__init__(name)
    def get_choices(self) -> MutableSequence[classes.actions.InteractionAction]:
        return [classes.actions.TakeItemAction(self)]

class Entity(RoomObject):
    pass

class Player(Entity):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]) -> None:
        super().__init__(name)

class Passage(RoomObject):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], destination_id : str):
        super().__init__(name)
        self.destination_id : str = destination_id
    def get_choices(self) -> MutableSequence[classes.actions.InteractionAction]:
        return [classes.actions.EnterPassageAction(self)]

class Room(Interactable):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], room_contents : list["RoomObject"]) -> None:
        self.room_contents : list[RoomObject] = room_contents
        super().__init__(name)
    
    def get_choices(self) -> list[classes.actions.InteractionAction]:
        choices = []
        for x in self.room_contents:
            choices.append(classes.actions.PlayerInteractAction(x))
        return choices
    
    def handle_connecting_signals(self, dungeon):
        self.event.subscribe(dungeon.interaction_event)
        for object in self.room_contents:
            object.handle_connecting_signals(dungeon)
    
    def add_roomobject(self, obj_to_add : "RoomObject") -> None:
        self.room_contents.append(obj_to_add)

    def remove_roomobject(self, obj_to_remove : "RoomObject") -> bool:
        if self.room_contents.__contains__(obj_to_remove):
            self.room_contents.remove(obj_to_remove)
            return True
        return False
    
    def get_nonplayers(self) -> list["RoomObject"]:
        new_list : list["RoomObject"] = []
        for x in self.room_contents:
            if not isinstance(x, Player):
                new_list.append(x)
        return new_list

    def get_player(self) -> Player:
        for x in self.room_contents:
            if isinstance(x, Player):
                return x
        return None