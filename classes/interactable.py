import sys
from collections.abc import Callable, Hashable, MutableSequence
from systems.event_system import Event
from classes.actions import *
from classes.actions import Effect
from classes.states import *
from classes.ability import Ability
from classes.ability import Sharpness
from classes.ability import ManaCost
from data.abilities import get_ability
import classes.actions
import copy
import utility

class Interactable:
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]) -> None:
        self.name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]] = name
        self.event = Event()
        self.notif = Event()
        self.include_back = True
    def get_description(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return ""
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        return []
    def interact_wrapper(self, button) -> None:
        self.interact()
    def interact(self) -> None:
        self.event.emit(action=classes.actions.PlayerInteractAction(self))
    def notify(self, dungeon, notif : Notif) -> None:
        self.notif.emit(dungeon, notif)
    def handle_connecting_signals(self, dungeon):
        self.event.subscribe(dungeon.interaction_event)
    def get_name(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return self.name

class AbilityHandler(Interactable):
    def __init__(self, abilities : list[Ability] = None):
        super().__init__("Abilities")
        self.ability_list : list[Ability] = abilities or []
    
    def get_abilities(self):
        return self.ability_list

    def add_ability(self, new_ability : Ability, index : int = 0):
        self.ability_list.insert(index,new_ability)
    
    def remove_ability(self, remove : Ability):
        self.ability_list.remove(remove)
    
    def has_abilities(self) -> bool:
        return len(self.ability_list) != 0

    def get_description(self):
        full_list = []
        for x in self.ability_list:
            full_list.append(x.get_full())
        return utility.combine_text(full_list)

    def apply(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.ability_list:
            x.apply(new_chain, effect)
    
    def end_of_round(self, chain):
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.ability_list:
            x.end_of_round(new_chain)
    
    def has_ability(self, id) -> bool:
        for x in self.ability_list:
            if x.is_id(id):
                return True
        return False
    
    def get_ability(self, id) -> Ability:
        for x in self.ability_list:
            if x.is_id(id):
                return x
        return None

class Actor(Interactable):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], ability_handler : AbilityHandler = None) -> None:
        super().__init__(name)
        self.ability_handler : AbilityHandler = ability_handler or AbilityHandler()

    def take_turn(self, dungeon) -> None:
        self.event.emit(action=None)
    
    def end_of_round(self, chain) -> None:
        new_chain = chain.copy()
        new_chain.append(self)
        self.ability_handler.end_of_round(new_chain)
    
    def apply_statics(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        self.ability_handler.apply(new_chain, effect)
    
    def has_ability(self, id : str) -> bool:
        return self.ability_handler.has_ability(id)
    
    def get_ability(self, id : str) -> Ability:
        return self.ability_handler.get_ability(id)
    
    def remove_ability(self, abil : Ability):
        self.ability_handler.remove_ability(abil)

class RoomObject(Actor):
    def add_to_action_queue(self, action_queue : list) -> None:
        action_queue.append(self)

class Campfire(RoomObject):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None) -> None:
        super().__init__(name, ability_handler)
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        if len(dungeon.actor.get_items_in_bag(lambda item : hasattr(item,"eat"))) > 0:
            return [classes.actions.PlayerCampfireInteractAction(self)]
        else:
            return [classes.actions.DummyAction(["You need food to rest at the ", self.name, "."])]

class Item(RoomObject):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, drop_chance : float = 1) -> None:
        super().__init__(name, ability_handler)
        self.drop_chance = drop_chance
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        return [classes.actions.TakeItemAction(self, dungeon.previous_interactable)]

class DestructionTool(Item):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, drop_chance : float = 1, quality : float = 1.0) -> None:
        super().__init__(name, ability_handler, drop_chance)
        self.quality = quality

class Shovel(DestructionTool):
    def dig(self):
        pass

class UsableItem(Item):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, drop_chance : float = 1, effect : classes.actions.Effect = None) -> None:
        super().__init__(name, ability_handler, drop_chance)
        self.effect = effect or Effect()
    
    def get_targets(self, dungeon):
        return dungeon.place.get_roomobjects()

    def can_use(self, dungeon) -> bool:
        return len(self.get_targets(dungeon)) > 0

    def get_description(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        if hasattr(self.effect, "get_desc"):
            return utility.combine_text([self.effect.get_desc(), self.ability_handler.get_description()])
        else:
            return None

    def use(self, dungeon, target):
        copy.deepcopy(self.effect).execute_with_statics(dungeon, self, target)

class Potion(UsableItem):
    def get_targets(self, dungeon):
        return dungeon.place.get_roomobjects(lambda x : isinstance(x, Player))

class Sharpener(UsableItem):
    def get_targets(self, dungeon):
        all_items = dungeon.actor.inventory.get_all_items()
        targets = []
        for x in all_items:
            if hasattr(x, "sharpen"):
                targets.append(x)
        return targets

class Equipment(Item):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, drop_chance : float = 1, slot : str = "?") -> None:
        super().__init__(name, ability_handler, drop_chance)
        self.equipment_slot : str = slot
    
    def get_description(self):
        return self.ability_handler.get_description()

class Weapon(Equipment):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, drop_chance : float = 1, effect : classes.actions.Effect = None) -> None:
        super().__init__(name, ability_handler, drop_chance, "Weapon")
        self.effect = effect or Effect()
    
    def get_description(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        if hasattr(self.effect, "get_desc"):
            return utility.combine_text([self.effect.get_desc(), self.ability_handler.get_description()])
        else:
            return None

    def attack(self, dungeon, target):
        copy.deepcopy(self.effect).execute_with_statics(dungeon, self, target)

class MeleeWeapon(Weapon):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, drop_chance : float = 1, effect : classes.actions.Effect = None, sharpness : float = 1.0) -> None:
        super().__init__(name, ability_handler, drop_chance, effect)
        self.ability_handler.add_ability(get_ability("melee"))
        self.ability_handler.add_ability(Sharpness("sharpness","Sharpness",sharpness))
    
    def attack(self, dungeon, target):
        super().attack(dungeon, target)
        DullWeaponEvent().execute(dungeon, target, self)
     
    def dull(self, amount : float):
        self.ability_handler.get_ability("sharpness").dull(amount)
    def sharpen(self, amount : float):
        self.ability_handler.get_ability("sharpness").sharpen(amount)

class MagicWeapon(Weapon):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, drop_chance : float = 1, effect : classes.actions.Effect = None, mana_cost : int = 10) -> None:
        super().__init__(name, ability_handler, drop_chance, effect)
        self.ability_handler.add_ability(get_ability("magic"))
        self.ability_handler.add_ability(ManaCost("manacost","Mana Cost", mana_cost))

class Food(Item):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, effect : classes.actions.Effect = None) -> None:
        super().__init__(name, ability_handler)
        self.effect = effect or Effect()
    
    def get_description(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        if hasattr(self.effect, "get_desc"):
            return self.effect.get_desc()
        else:
            return []

    def eat(self, dungeon, target):
        copy.deepcopy(self.effect).execute_with_statics(dungeon, dungeon.actor, target)

class Stat:
    def get_text():
        raise NotImplementedError("Subclasses must implement get_text()")

class HPContainer(Stat):
    def __init__(self, current : int, max : int = -1):
        if max == -1:
            self.max : int = current
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

class MPContainer(Stat):
    def __init__(self, current : int, max : int = -1):
        if max == -1:
            self.max : int = current
        self.current : int = current
    def get_text(self):
        return utility.combine_text([("magic", str(self.current)), " / ", ("magic", str(self.max))], False)
    def get_current_mp(self) -> int:
        return self.current
    def spend(self, amount : int) -> bool:
        self.current -= amount
        if self.current < 0:
            self.current = 0
            return False
        return True
    def restore(self, amount : int) -> int:
        self.current += amount
        if self.current > self.max:
            self.current = self.max

class StatHandler(Interactable):
    def __init__(self, stats : dict[str:] = None):
        super().__init__("Stats")
        self.stat_dict : dict[str:] = stats or {}
    
    def has_stat(self, stat : str):
        return stat in self.stat_dict

    def get_stat(self, stat : str):
        return self.stat_dict[stat]

    def set_stat(self, stat : str, new_value):
        self.stat_dict[stat] = new_value
    
    def get_description(self):
        text_list = []
        for p in self.stat_dict:
            text_list.append([p,": ", self.stat_dict[p].get_text()])
        return utility.combine_text(text_list)

from data.dialogue import DialogueNode
from data.dialogue import get_dialogue

class DialogueManager(Interactable):
    def __init__(self, root_dialogue_id : str = None):
        super().__init__("Talk")
        self.set_dialogue(root_dialogue_id)
        self.include_back = False
    
    def set_dialogue(self, dialogue_id : str = None):
        self.root_dialogue : DialogueNode = None
        if dialogue_id != None:
            self.root_dialogue = get_dialogue(dialogue_id)

    def has_dialogue(self) -> bool:
        return self.root_dialogue != None

    def get_description(self):
        return self.root_dialogue.get_text()

    def get_choices(self, dungeon):
        dialogue_options = []
        if self.root_dialogue.has_choices():
            for x in self.root_dialogue.get_choices():
                dialogue_options.append(DialogueAction(self, get_dialogue(x)))
        else:
            dialogue_options.append(PlayerInteractAction(dungeon.place))
        return dialogue_options

class EquipmentHandler(Interactable):
    def __init__(self, equipment : dict[str:Equipment] = None):
        super().__init__("Equipment")
        self.equipment_dict : dict[str:Equipment] = equipment or {}
    
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
                if dungeon.actor.inventory.equipment_handler == self:
                    choices.append(classes.actions.PlayerEquippedInteractAction(self.equipment_dict[x], True))
                else:
                    choices.append(classes.actions.PlayerEquippedInteractAction(self.equipment_dict[x], False))
        return choices
    
    def apply_statics(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.equipment_dict.values():
            if not x == None:
                x.apply_statics(new_chain, effect)
    
    def get_items(self) -> list[Equipment]:
        equips : list[Equipment] = []
        for x in self.equipment_dict.values():
            if x != None:
                equips.append(x)
        return equips

class Bag(Interactable):
    def __init__(self, size : int = -1, items : list[Item] = None):
        super().__init__("Bag")
        self.items_list : list[Item] = items or []
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
            choices.append(classes.actions.PlayerBagInteractAction(x))
        return choices
    
    def apply_statics(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.items_list:
            x.apply_statics(new_chain, effect)

    def get_items_in_bag(self, condition = lambda item : True) -> list["Item"]:
        roomobjets : list["Item"] = []
        for x in self.items_list:
            if condition(x):
                roomobjets.append(x)
            else:
                pass
        return roomobjets
    
class Inventory(Interactable):
    def __init__(self, equipment_handler : EquipmentHandler = None, bag : Bag = None):
        super().__init__("Inventory")
        self.equipment_handler : EquipmentHandler = equipment_handler or EquipmentHandler()
        self.bag : Bag = bag or Bag()
    
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

    def apply_statics(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        self.equipment_handler.apply_statics(new_chain, effect)
        self.bag.apply_statics(new_chain, effect)
    
    def get_items_in_bag(self, condition = lambda item : True) -> list["Item"]:
        return self.bag.get_items_in_bag(condition)

class Passage(RoomObject):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], ability_handler : AbilityHandler = None, destination_id : str = "?"):
        super().__init__(name, ability_handler)
        self.destination_id : str = destination_id
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        return [classes.actions.EnterPassageAction(self)]

class Container(RoomObject):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], ability_handler : AbilityHandler = None, contents : list[RoomObject] = None):
        super().__init__(name, ability_handler)
        self.contents : list[RoomObject] = contents or []
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        choices = []
        for x in self.contents:
            choices.append(PlayerInteractAction(x))
        if len(choices) == 0:
            choices.append(classes.actions.DummyAction(["There is nothing in the ", self.name, "."]))
        return choices
    def add_roomobject(self, obj_to_add : "RoomObject") -> None:
        self.contents.append(obj_to_add)

    def remove_roomobject(self, obj_to_remove : "RoomObject") -> bool:
        if self.contents.__contains__(obj_to_remove):
            self.contents.remove(obj_to_remove)
            return True
        return False
    
    def handle_connecting_signals(self, dungeon):
        super().handle_connecting_signals(dungeon)
        for object in self.contents:
            object.handle_connecting_signals(dungeon)

class Destructible(RoomObject):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], ability_handler : AbilityHandler = None, contents : list[RoomObject] = None, action_type : str = "dig"):
        super().__init__(name, ability_handler)
        self.contents : list[RoomObject] = contents or []
        self.action_type : str = action_type
    
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        if len(dungeon.actor.get_items_in_bag(lambda item : hasattr(item,self.action_type))) > 0:
            return [classes.actions.PlayerDestructibleInteractAction(self)]
        else:
            return [classes.actions.DummyAction(["You need an item that can ", self.action_type, " the ", self.name, "."])]

    def add_roomobject(self, obj_to_add : "RoomObject") -> None:
        self.contents.append(obj_to_add)

    def remove_roomobject(self, obj_to_remove : "RoomObject") -> bool:
        if self.contents.__contains__(obj_to_remove):
            self.contents.remove(obj_to_remove)
            return True
        return False
    
    def handle_connecting_signals(self, dungeon):
        super().handle_connecting_signals(dungeon)
        for object in self.contents:
            object.handle_connecting_signals(dungeon)
    
    def get_drops(self, item : Item) -> list[Item]:
        drops : list[Item] = []
        for x in self.contents:
            if random.random() ** item.quality <= (x.drop_chance):
                drops.append(x)
        return drops

class Entity(RoomObject):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, inventory : Inventory = None, stathandler : StatHandler = None, dialogue_manager : DialogueManager = None):
        super().__init__(name, ability_handler)
        self.inventory = inventory or Inventory()
        self.stathandler = stathandler or StatHandler()
        self.dialogue_manager = dialogue_manager or DialogueManager()
    
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
    
    def get_drops(self) -> list[Item]:
        all_items : list[Item] = self.inventory.get_all_items()
        drops : list[Item] = []
        for x in all_items:
            if random.random() <= x.drop_chance:
                drops.append(x)
        return drops

    def get_items_in_bag(self, condition = lambda item : True) -> list["Item"]:
        return self.inventory.get_items_in_bag(condition)
    
    def remove_item(self, remove : Item):
        self.inventory.bag.remove_item(remove)

    def remove_ability(self, remove : Ability):
        self.ability_handler.remove_ability(remove)
    
    def add_ability(self, addition : Ability):
        self.ability_handler.add_ability(addition)

    def has_weapon(self) -> bool:
        weapon = self.inventory.get_item_in_slot("Weapon")
        if weapon != None:
            return True
        else:
            return False

    def get_weapon(self) -> Equipment:
        if self.inventory.get_item_in_slot("Weapon") == None:
            return None
        else:
            return self.inventory.get_item_in_slot("Weapon")
    
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        choices : list[classes.actions.InteractionAction] = []
        if dungeon.actor.has_weapon():
            choices.append(classes.actions.AttackAction(self))
        if self.dialogue_manager.has_dialogue():
            choices.append(classes.actions.PlayerInteractAction(self.dialogue_manager))
        choices.append(classes.actions.PlayerInteractAction(self.stathandler))
        if self.ability_handler.has_abilities():
            choices.append(classes.actions.PlayerInteractAction(self.ability_handler))
        choices.append(classes.actions.PlayerInteractAction(self.inventory.equipment_handler))
        return choices

    def apply_statics(self, chain : list, effect : Effect):
        super().apply_statics(chain, effect)
        new_chain = chain.copy()
        new_chain.append(self)
        self.inventory.apply_statics(new_chain, effect)

class Player(Entity):
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.InteractionAction]:
        choices : list[classes.actions.InteractionAction] = []
        choices.append(classes.actions.PlayerInteractAction(self.inventory))
        choices.append(classes.actions.PlayerInteractAction(self.stathandler))
        if self.ability_handler.has_abilities():
            choices.append(classes.actions.PlayerInteractAction(self.ability_handler))
        return choices
    
class StateEntity(Entity):
    def __init__(self, name, ability_handler = None, inventory = None, stathandler = None, dialogue_manager : DialogueManager = None, state : State = None):
        super().__init__(name, ability_handler, inventory, stathandler, dialogue_manager)
        self.default_state : State= state or IdleState()
        self.state : State = None
        
        self.change_to_default_state(None, False)
    
    def change_to_default_state(self, dungeon = None, act : bool = True):
        self.change_state(self.default_state, dungeon, act)

    def change_state(self, new_state : State, dungeon = None, act : bool = True):
        if self.state != None:
            self.state.unregister(self)
        self.state : State = new_state
        self.state.register(self)
        if act:
            if dungeon != None:
                self.state.decide(dungeon)
            else:
                self.event.emit(action=None)

    def take_turn(self, dungeon) -> None:
        self.state.decide(dungeon)

class Room(Actor):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], ability_handler : AbilityHandler = None, room_contents : list["RoomObject"] = None) -> None:
        self.room_contents : list[RoomObject] = room_contents or None
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
        for x in self.get_roomobjects(lambda item : not isinstance(item, Player)):
            x.add_to_action_queue(action_queue)
    
    def apply_statics(self, chain : list, effect : Effect):
        super().apply_statics(chain, effect)
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.room_contents:
            x.apply_statics(new_chain, effect)
    def end_of_round(self, chain) -> None:
        super().end_of_round(chain)
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.room_contents:
            x.end_of_round(new_chain)