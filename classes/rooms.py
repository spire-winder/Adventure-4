import typing
from collections.abc import Callable, Hashable, MutableSequence
from classes.roomobjects import Player
if typing.TYPE_CHECKING:
    from classes.roomobjects import RoomObject

class Room:
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], room_contents : MutableSequence["RoomObject"]) -> None:
        self.name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]] = name
        self.choices : "MutableSequence"["RoomObject"] = room_contents
    
    def add_roomobject(self, obj_to_add : "RoomObject") -> None:
        self.choices.append(obj_to_add)

    def remove_roomobject(self, obj_to_remove : "RoomObject") -> bool:
        for x in self.choices:
            if x == obj_to_remove:
                self.choices.remove(x)
                return True
        return False
    
    def get_nonplayers(self) -> list["RoomObject"]:
        new_list : list["RoomObject"] = []
        for x in self.choices:
            if not isinstance(x, Player):
                new_list.append(x)
        return new_list

    def get_player(self) -> Player:
        for x in self.choices:
            if isinstance(x, Player):
                return x
        return None