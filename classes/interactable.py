import sys
from collections.abc import Callable, Hashable, MutableSequence
from systems.event_system import Event
from classes.actions import *
from classes.actions import Effect
from classes.actions import EndStatusEffect
from classes.interactable import DamageEvent
from classes.interactable import EffectSelectorTarget
from classes.states import *
import classes.actions
import copy
import utility

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

class Ability:
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]):
        self.name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]= name
    def get_name(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return self.name
    def get_desc(self):
        return None
    def get_full(self):
        return utility.combine_text([self.get_name(), self.get_desc()])
    def apply(self, owner, effect : Effect):
        raise NotImplementedError("Subclasses must implement apply()")
    def end_of_round(self, dungeon, owner):
        pass

class Status(Ability):
    def get_name(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return self.ability.get_name()
    def get_desc(self):
        status_color : str
        duration_percent : float = self.current_duration / self.duration
        if duration_percent >= 0.666:
            status_color = "status_full"
        elif duration_percent >= 0.333:
            status_color = "status_depleted"
        else:
            status_color = "status_empty"
        return utility.combine_text([self.ability.get_desc(), ["(", (status_color, str(self.duration)), " rounds remaining)"]])
    def apply(self, owner, effect : Effect):
        self.ability.apply(owner, effect)
    def __init__(self, ability : Ability, duration : int):
        super().__init__("")
        self.ability = ability
        self.duration : int = duration
        self.current_duration : int = duration
    def end_of_round(self, dungeon, owner):
        self.ability.end_of_round(dungeon, owner)
        self.current_duration -= 1
        if self.current_duration <= 0:
            EndStatusEffect().execute_with_statics(dungeon, owner, self)

class Armor(Ability):
    def get_desc(self):
        return ("iron", "+" + str(self.armor_value) + " Armor")
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], armor_value : int = 1):
        super().__init__(name)
        self.armor_value = armor_value
    def apply(self, owner, effect : Effect):
        if isinstance(effect, DamageEvent) and effect.target == owner:
            effect.damage -= self.armor_value

class AbilityHandler(Interactable):
    def __init__(self, abilities : list[Ability] = []):
        super().__init__("Abilities")
        self.ability_list : list[Ability] = abilities
    
    def get_abilities(self):
        return self.ability_list

    def add_ability(self, new_ability : Ability):
        self.ability_list.append(new_ability)
    
    def remove_ability(self, remove : Ability):
        self.ability_list.remove(remove)
    
    def get_description(self):
        full_list = []
        for x in self.ability_list:
            full_list.append(x.get_full())
        return utility.combine_text(full_list)

    def apply(self, owner, effect : Effect):
        for x in self.ability_list:
            x.apply(owner, effect)
    
    def end_of_round(self, dungeon, owner):
        for x in self.ability_list:
            x.end_of_round(dungeon, owner)

class Actor(Interactable):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], ability_handler : AbilityHandler = AbilityHandler()) -> None:
        super().__init__(name)
        self.ability_handler : AbilityHandler = ability_handler

    def take_turn(self, dungeon) -> None:
        self.event.emit(action=None)
    
    def end_of_round(self, dungeon) -> None:
        self.ability_handler.end_of_round(dungeon, self)
    
    def apply_statics(self, effect : Effect):
        self.ability_handler.apply(self, effect)

class RoomObject(Actor):
    def add_to_action_queue(self, action_queue : list) -> None:
        action_queue.append(self)

class Campfire(RoomObject):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = AbilityHandler()) -> None:
        super().__init__(name, ability_handler)
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        if len(dungeon.actor.get_items_in_bag(lambda item : hasattr(item,"eat"))) > 0:
            return [classes.actions.PlayerCampfireInteractAction(self)]
        else:
            return [classes.actions.DummyAction(["You need food to rest at the ", self.name, "."])]

class Item(RoomObject):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = AbilityHandler()) -> None:
        super().__init__(name, ability_handler)
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        return [classes.actions.TakeItemAction(self)]

class Equipment(Item):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = AbilityHandler(), slot : str = "?") -> None:
        super().__init__(name, ability_handler)
        self.equipment_slot : str = slot
    
    def get_description(self):
        return self.ability_handler.get_description()
    
    def apply_statics_regarding(self, owner, effect : Effect):
        self.ability_handler.apply(owner, effect)

class Stat:
    def get_text():
        raise NotImplementedError("Subclasses must implement get_text()")

class HPContainer(Stat):
    def __init__(self, current : int, max : int):
        self.max : int = max
        self.current : int = current
    def get_text(self):
        status_color : str
        duration_percent : float = self.current / self.max
        if duration_percent >= 0.666:
            status_color = "status_full"
        elif duration_percent >= 0.333:
            status_color = "status_depleted"
        else:
            status_color = "status_empty"
        return utility.combine_text([(status_color, str(self.current)), " / ", str(self.max)], False)
    def get_current_health(self) -> int:
        return self.current
    def damage(self, amount : int) -> int:
        self.current -= amount
        return self.current
    def is_dead(self) -> bool:
        return self.current <= 0
    def heal(self, amount : int) -> int:
        self.current += amount
        if self.current > self.max:
            self.current = self.max
        return self.current

class StatHandler(Interactable):
    def __init__(self, stats : dict[str:] = {}):
        super().__init__("Stats")
        self.stat_dict : dict[str:] = stats
    
    def get_stat(self, stat : str):
        return self.stat_dict[stat]

    def set_stat(self, stat : str, new_value):
        self.stat_dict[stat] = new_value
    
    def get_description(self):
        text_list = []
        for p in self.stat_dict:
            text_list.append([p,": ", self.stat_dict[p].get_text()])
        return utility.combine_text(text_list)

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
        if not slot in self.equipment_dict:
            return None
        return self.equipment_dict[slot]
    
    def get_choices(self, dungeon) -> list[classes.actions.InteractionAction]:
        choices = []
        for x in self.equipment_dict:
            if self.equipment_dict[x] == None:
                choices.append(classes.actions.DummyAction([x, ": None"]))
            else:
                choices.append(classes.actions.PlayerEquippedInteractAction(self.equipment_dict[x]))
        return choices
    
    def apply_statics_regarding(self, owner : Actor, effect : Effect):
        for x in self.equipment_dict.values():
            if not x == None:
                x.apply_statics_regarding(owner, effect)
    
    def get_items(self):
        equips : list[Equipment] = []
        for x in self.equipment_dict:
            if self.equipment_dict[x] != None:
                equips.append(x)
        return equips

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
    
    def get_items_in_bag(self, condition = lambda item : True) -> list["Item"]:
        roomobjets : list["Item"] = []
        for x in self.items_list:
            if condition(x):
                roomobjets.append(x)
            else:
                pass
        return roomobjets
    
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

    def get_all_items(self) -> list[Item]:
        return self.equipment_handler.get_items() + self.bag.get_items()

    def apply_statics_regarding(self, owner : Actor, effect : Effect):
        self.equipment_handler.apply_statics_regarding(owner, effect)
    
    def get_items_in_bag(self, condition = lambda item : True) -> list["Item"]:
        return self.bag.get_items_in_bag(condition)

class Passage(RoomObject):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], ability_handler : AbilityHandler = AbilityHandler(), destination_id : str = "?"):
        super().__init__(name, ability_handler)
        self.destination_id : str = destination_id
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        return [classes.actions.EnterPassageAction(self)]

class Entity(RoomObject):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = AbilityHandler(), inventory : Inventory = Inventory(), stathandler : StatHandler = StatHandler({"HP": 5})):
        super().__init__(name, ability_handler)
        self.inventory = inventory
        self.stathandler = stathandler
    
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
    
    def get_all_items(self) -> list["Item"]:
        return self.inventory.get_all_items()

    def get_items_in_bag(self, condition = lambda item : True) -> list["Item"]:
        return self.inventory.get_items_in_bag(condition)
    
    def remove_ability(self, remove : Ability):
        self.ability_handler.remove_ability(remove)
    
    def add_ability(self, addition : Ability):
        self.ability_handler.add_ability(addition)

    def has_weapon(self) -> bool:
        return self.inventory.get_item_in_slot("Weapon") != None

    def get_weapon(self) -> Equipment:
        if self.inventory.get_item_in_slot("Weapon") == None:
            return Weapon("Fists", AbilityHandler(), EffectSelectorTarget(DamageEvent(2)))
        else:
            return self.inventory.get_item_in_slot("Weapon")
    
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        return [classes.actions.AttackAction(self), classes.actions.PlayerInteractAction(self.stathandler), classes.actions.PlayerInteractAction(self.ability_handler)]

    def apply_statics(self, effect : Effect):
        super().apply_statics(effect)
        self.inventory.apply_statics_regarding(self, effect)

class Player(Entity):
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        return [classes.actions.PlayerInteractAction(self.inventory), classes.actions.PlayerInteractAction(self.stathandler), classes.actions.PlayerInteractAction(self.ability_handler)]

class StateEntity(Entity):
    def __init__(self, name, ability_handler = AbilityHandler(), inventory = Inventory(), stathandler = StatHandler({ "HP": 5 }), state : State = State()):
        super().__init__(name, ability_handler, inventory, stathandler)
        self.state : State= state
    def take_turn(self, dungeon) -> None:
        self.state.decide(dungeon, self)

class Weapon(Equipment):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = AbilityHandler(), effect : classes.actions.Effect = Effect()) -> None:
        super().__init__(name, ability_handler, "Weapon")
        self.effect = effect
    
    def get_description(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        if hasattr(self.effect, "get_desc"):
            return self.effect.get_desc()
        else:
            return ""

    def attack(self, dungeon, target : Entity):
        copy.deepcopy(self.effect).execute_with_statics(dungeon, dungeon.actor, target)

class Food(Item):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = AbilityHandler(), effect : classes.actions.Effect = Effect()) -> None:
        super().__init__(name, ability_handler)
        self.effect = effect
    
    def get_description(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        if hasattr(self.effect, "get_desc"):
            return self.effect.get_desc()
        else:
            return ""

    def eat(self, dungeon, target : Entity):
        copy.deepcopy(self.effect).execute_with_statics(dungeon, dungeon.actor, target)

class Room(Actor):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], ability_handler : AbilityHandler = AbilityHandler(), room_contents : list["RoomObject"] = []) -> None:
        self.room_contents : list[RoomObject] = room_contents
        super().__init__(name, ability_handler)
    
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
    
    def get_roomobjects(self, condition = lambda item : True) -> list["RoomObject"]:
        roomobjets : list["RoomObject"] = []
        for x in self.room_contents:
            if condition(x):
                roomobjets.append(x)
            else:
                pass
        return roomobjets

    def get_player(self) -> Player:
        for x in self.room_contents:
            if isinstance(x, Player):
                return x
        return None

    def add_to_action_queue(self, action_queue : list) -> None:
        action_queue.append(self)
        for x in self.room_contents:
            x.add_to_action_queue(action_queue)
    
    def apply_statics(self, effect : Effect):
        super().apply_statics(effect)
        for x in self.room_contents:
            x.apply_statics(effect)
    def end_of_round(self, dungeon) -> None:
        super().end_of_round(dungeon)
        for x in self.room_contents:
            x.end_of_round(dungeon)