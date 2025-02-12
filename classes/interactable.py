import sys
from collections.abc import Callable, Hashable, MutableSequence
from systems.event_system import Event
import classes.actions

class Interactable:
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]) -> None:
        self.name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]] = name
        self.event = Event()
    def get_description(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return ""
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        return []
    def interact_wrapper(self, button) -> None:
        self.interact()
    def interact(self) -> None:
        self.event.emit(action=classes.actions.PlayerInteractAction(self))
    def handle_connecting_signals(self, dungeon):
        self.event.subscribe(dungeon.interaction_event)
    def get_name(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return self.name

class RoomObject(Interactable):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]) -> None:
        super().__init__(name)
    def take_turn(self) -> None:
        self.event.emit(action=None)

class Item(RoomObject):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]]) -> None:
        super().__init__(name)
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        return [classes.actions.TakeItemAction(self)]

class Equipment(Item):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], slot : str) -> None:
        super().__init__(name)
        self.equipment_slot : str = slot

class EquipmentHandler(Interactable):
    def __init__(self, equipment : dict[str:Equipment] = {}):
        super().__init__("Equipment")
        self.equipment_dict : dict[str:Equipment] = equipment
    
    def can_equip(self, item : Equipment):
        if item.equipment_slot in self.equipment_dict:
            return True
        else:
            return False

    def can_equip_without_swap(self, item : Equipment):
        if self.can_equip(item) and self.equipment_dict[item.equipment_slot] == None:
            return True
        else:
            return False
    
    def equip(self, item : Equipment):
        self.equipment_dict[item.equipment_slot] = item
    
    def unequip_slot(self, slot : str) -> Equipment:
        equipment_to_return : Equipment = self.equipment_dict[slot]
        self.equipment_dict[slot] = None
        return equipment_to_return
    
    def get_item_in_slot(self, slot : str) -> Equipment:
        return self.equipment_dict[slot]
    
    def get_choices(self, dungeon) -> list[classes.actions.InteractionAction]:
        choices = []
        for x in self.equipment_dict:
            if self.equipment_dict[x] == None:
                choices.append(classes.actions.DummyAction([x, ": None"]))
            else:
                choices.append(classes.actions.PlayerEquippedInteractAction(self.equipment_dict[x]))
        return choices

class Bag(Interactable):
    def __init__(self, size : int = -1, items : list[Item] = []):
        super().__init__("Bag")
        self.items_list : list[Item] = items
        self.size = size
    
    def can_add_item(self, item : Item):
        if self.size == -1 or len(self.items_list) + 1 <= self.size:
            return True
        else:
            return False
    
    def add_item(self, item : Item):
        self.items_list.append(item)
    
    def remove_item(self, item : Item):
        self.items_list.remove(item)
    
    def get_description(self):
        return ["Size: ", str(self.size)]

    def get_items(self) -> list[Item]:
        return self.items_list

    def get_choices(self, dungeon) -> list[classes.actions.InteractionAction]:
        choices = []
        for x in self.items_list:
            choices.append(classes.actions.PlayerInventoryInteractAction(x))
        return choices
    
class Inventory(Interactable):
    def __init__(self, equipment_handler : EquipmentHandler = EquipmentHandler(), bag : Bag = Bag()):
        super().__init__("Inventory")
        self.equipment_handler : EquipmentHandler = equipment_handler
        self.bag : Bag = bag
    
    def can_take_item(self, item : Item):
        if isinstance(item, Equipment) and self.equipment_handler.can_equip_without_swap(item):
            return True
        elif self.bag.can_add_item(item):
            return True
        else:
            return False

    def can_equip(self, item : Equipment):
        return self.equipment_handler.can_equip(item)

    def take_item(self, item : Item):
        if isinstance(item, Equipment) and self.equipment_handler.can_equip_without_swap(item):
            self.equip_item(item)
        elif self.bag.can_add_item(item):
            self.bag.add_item(item)
        else:
            sys.exit('Item cannot be added to bag!')

    def equip_item(self, item : Equipment):
        if item in self.bag.get_items():
            self.bag.remove_item(item)
        if not self.equipment_handler.can_equip_without_swap(item):
            self.bag.add_item(self.equipment_handler.get_item_in_slot(item.equipment_slot))
        self.equipment_handler.equip(item)
    
    def unequip_item(self, item : Equipment):
        self.bag.add_item(item)
        self.equipment_handler.unequip_slot(item.equipment_slot)

    def get_item_in_slot(self, slot : str) -> Equipment:
        return self.equipment_handler.get_item_in_slot(slot)

    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        return [classes.actions.PlayerInteractAction(self.equipment_handler), classes.actions.PlayerInteractAction(self.bag)]

class Entity(RoomObject):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], inventory : Inventory = Inventory()):
        super().__init__(name)
        self.inventory = inventory
    
    def can_take_item(self, item : Item):
        return self.inventory.can_take_item(item)

    def take_item(self, item : Item):
        self.inventory.take_item(item)
    
    def equip_item(self, item : Equipment):
        self.inventory.equip_item(item)
    
    def unequip_item(self, item : Equipment):
        self.inventory.unequip_item(item)

    def can_equip(self, item : Equipment):
        return self.inventory.can_equip(item)
    
    def get_weapon(self) -> Equipment:
        if self.inventory.get_item_in_slot("Weapon") == None:
            return Equipment("Fists", "Weapon")
        else:
            return self.inventory.get_item_in_slot("Weapon")
    
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        return [classes.actions.AttackAction(self)]

class Player(Entity):
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        return [classes.actions.PlayerInteractAction(self.inventory)]

class Passage(RoomObject):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], destination_id : str):
        super().__init__(name)
        self.destination_id : str = destination_id
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        return [classes.actions.EnterPassageAction(self)]

class Room(Interactable):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], room_contents : list["RoomObject"]) -> None:
        self.room_contents : list[RoomObject] = room_contents
        super().__init__(name)
    
    def get_choices(self, dungeon) -> list[classes.actions.InteractionAction]:
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