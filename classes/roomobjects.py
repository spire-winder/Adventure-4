
import typing
from systems.event_system import Event
import classes.actions
from collections.abc import Callable, Hashable, MutableSequence
if typing.TYPE_CHECKING:
    pass

class RoomObject:
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]]) -> None:
        self.name = name
        self.event = Event()
    def interact(self, button) -> None:
        pass
    def take_turn(self) -> None:
        self.event.emit(action=None)
    def handle_connecting_signals(self, dungeon):
        self.event.subscribe(dungeon.roomobject_event)
    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the event reference before pickling.
        if 'event' in state:
            state['event'] = Event()
        return state

class Item(RoomObject):
    def interact(self, button) -> None:
        self.event.emit(action=classes.actions.TakeItemAction(self))

class Entity(RoomObject):
    def interact(self, button) -> None:
        pass

class Player(Entity):
    def take_turn(self) -> None:
        self.event.emit(action=classes.actions.PlayerInputAction())

class Passage(RoomObject):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], destination_id : str):
        super().__init__(name)
        self.destination_id : str = destination_id
    
    def interact(self, button) -> None:
        self.event.emit(action=classes.actions.EnterPassageAction(self))