import sys
from collections.abc import Callable, Hashable, MutableSequence
from systems.event_system import Event
from classes.actions import *
from classes.actions import Effect
from classes.states import *
from classes.ability import Ability
from classes.ability import Sharpness
from classes.ability import ManaCost
from classes.ability import SingleUse
from data.abilities import get_ability
import classes.actions
import copy
import utility

class RandomElement:
    def __init__(self, possibilities : list):
        self.possibilities : list = possibilities
    
    def dungeon_init(self, chain):
        return random.choice(self.possibilities)
    def handle_connecting_signals(self, dungeon):
        pass

class Interactable:
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]) -> None:
        self.id : str = ""
        self.name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]] = name
        self.event = Event()
        self.notif = Event()
        self.include_back = True
    def get_description(self, dungeon) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return ""
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.PlayerAction]:
        return []
    def interact(self) -> None:
        self.event.emit(action=classes.actions.PlayerInteractAction(self))
    def notify(self, dungeon, notif : Notif) -> None:
        self.notif.emit(dungeon, notif)
    def handle_connecting_signals(self, dungeon):
        self.event.subscribe(dungeon.interaction_event)
    def get_name(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return self.name
    def is_id(self, eye_dee : str) -> bool:
        return eye_dee == self.id

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

    def get_description(self, dungeon):
        full_list = []
        for x in self.ability_list:
            full_list.append(x.get_full())
        return utility.combine_text(full_list)

    def apply(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.ability_list:
            x.apply(new_chain, effect)
    
    def reply(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.ability_list:
            x.reply(new_chain, effect)
        
    def dungeon_init(self, chain : list):
        new_chain = chain.copy()
        new_chain.append(self)
        for x in range(len(self.ability_list)):
            ele = self.ability_list[x]
            if isinstance(ele, RandomElement):
                self.ability_list[x] = ele.dungeon_init(new_chain)
        
    def apply_from_bag(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.ability_list:
            x.apply_from_bag(new_chain, effect)
    
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
        return
    
    def end_of_round(self, chain) -> None:
        new_chain = chain.copy()
        new_chain.append(self)
        self.ability_handler.end_of_round(new_chain)
    
    def dungeon_init(self, chain : list):
        new_chain = chain.copy()
        new_chain.append(self)
        self.ability_handler.dungeon_init(new_chain)

    def apply_statics(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        self.ability_handler.apply(new_chain, effect)
    
    def reply(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        self.ability_handler.reply(new_chain, effect)
    
    def apply_statics_in_bag(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        self.ability_handler.apply_from_bag(new_chain, effect)

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
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.PlayerAction]:
        choices = []
        if len(dungeon.actor.get_items_in_bag(lambda item : hasattr(item,"foodeffect"))) > 0:
            choices.append(classes.actions.CampfireAction(self))
        else:
            choices.append(classes.actions.DummyAction(["You need food to rest at the ", self.name, "."]))
        if len(dungeon.get_discovered_campfire_rooms()) > 1:
            choices.append(classes.actions.DreamAction(self))
        return choices

class Item(RoomObject):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, price : int = 0, drop_chance : float = 1) -> None:
        super().__init__(name, ability_handler)
        self.price = price
        self.drop_chance = drop_chance
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.PlayerAction]:
        if dungeon.player.can_take_item(self):
            if dungeon.player.can_equip(self):
                return [classes.actions.EquipItemAction(self, dungeon.previous_interactable), classes.actions.TakeItemAction(self, dungeon.previous_interactable)]
            else:
                return [classes.actions.TakeItemAction(self, dungeon.previous_interactable)]
        else:
            return [classes.actions.DummyAction("Your inventory is full.")]

class UsableItem(Item):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, price : int = 0, drop_chance : float = 1, useeffect : classes.actions.Effect = None) -> None:
        super().__init__(name, ability_handler, price, drop_chance)
        self.useeffect = useeffect or Effect()
    
    def get_targets(self, dungeon):
        return dungeon.place.get_roomobjects()

    def can_use(self, dungeon) -> bool:
        return len(self.get_targets(dungeon)) > 0

    def get_description(self, dungeon) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return utility.combine_text([self.useeffect.get_desc(), self.ability_handler.get_description(dungeon)])
    
    def get_effect(self, effect) -> Effect:
        return self.useeffect
    def use(self, dungeon) -> None:
        pass

class Potion(UsableItem):
    def get_targets(self, dungeon):
        return dungeon.place.get_roomobjects(lambda x : x == dungeon.actor)

class UsableWeapon(UsableItem):
    def get_targets(self, dungeon):
        return dungeon.place.get_roomobjects(lambda x : isinstance(x, Entity) and x != dungeon.actor)

class Scroll(UsableWeapon):
    def __init__(self, name, ability_handler = None, price = 0, drop_chance = 1, useeffect = None, mana_cost : int = 1):
        super().__init__(name, ability_handler, price, drop_chance, useeffect)
        self.ability_handler.add_ability(get_ability("magic"))
        self.ability_handler.add_ability(ManaCost("manacost","Mana Cost", mana_cost))

class UsableRoomObj(RoomObject):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, actions : dict[str:Effect] = None) -> None:
        super().__init__(name, ability_handler)
        self.actions = actions or {}
    
    def get_choices(self, dungeon):
        choices = []
        for x in self.actions:
            choices.append(UseAction(self, None, x))
        return choices

    def get_description(self, dungeon) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        acts = []
        for x in self.actions:
            acts.append(self.get_effect(UseEffect(None, None, None, verb=x)).get_desc())
        return utility.combine_text([utility.combine_text(acts), self.ability_handler.get_description(dungeon)])
    
    def get_effect(self, effect) -> Effect:
        return self.actions[effect.verb]
    def use(self, dungeon):
        pass

class Lever(UsableRoomObj):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, active : bool = False, oneffect : classes.actions.Effect = None, offeffect : classes.actions.Effect = None) -> None:
        super().__init__(name, ability_handler)
        self.oneffect : Effect = oneffect or Effect()
        self.offeffect : Effect = offeffect or Effect()
        self.active : bool = active

    def get_choices(self, dungeon):
        return [UseAction(self, None, "flip")]

    def get_description(self, dungeon) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return utility.combine_text([self.get_effect(Effect()).get_desc(), self.ability_handler.get_description(dungeon)])

    def get_effect(self, effect) -> Effect:
        return self.oneffect if self.active else self.offeffect
    def use(self, dungeon) -> None:
        self.active = not self.active

class Key(Item):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None,price : int = 0,  drop_chance : float = 1, keyeffect : classes.actions.Effect = None, key_id : str = "?") -> None:
        ability_handler = ability_handler or AbilityHandler([SingleUse()])
        super().__init__(name, ability_handler, price, drop_chance)
        self.keyeffect = keyeffect or UnlockEffect("item", "target")
        self.key_id = key_id
    
    def get_description(self, dungeon) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return utility.combine_text([self.keyeffect.get_desc(), self.ability_handler.get_description(dungeon)])

    def get_effect(self, effect) -> Effect:
        return self.keyeffect

    def use(self, dungeon) -> None:
        pass
 
    def can_unlock(self, id) -> bool:
        return self.key_id == id

class Tool(Item):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, price : int = 0, drop_chance : float = 1, tooleffect : classes.actions.Effect = None, tool_type : str = "?", tool_strength : str = "?") -> None:
        ability_handler = ability_handler or AbilityHandler()
        super().__init__(name, ability_handler, price,  drop_chance)
        self.tooleffect = tooleffect or DestroyEffect("item","target")
        self.tool_type : str = tool_type
        self.tool_strength : int= tool_strength
    
    def get_description(self, dungeon) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return utility.combine_text(["Type: " + self.tool_type,"Strength: " + str(self.tool_strength),self.tooleffect.get_desc(), self.ability_handler.get_description(dungeon)])

    def get_effect(self, effect) -> Effect:
        return self.tooleffect
    def use(self, dungeon) -> None:
        pass

    def can_destroy(self, id : str, strength : int) -> bool:
        return self.tool_type == id and self.tool_strength >= strength

class Explosive(UsableItem, Tool):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, price : int = 0, drop_chance : float = 1, tooleffect : classes.actions.Effect = None, tool_type : str = "?", tool_strength : str = "?", attackeffect : classes.actions.Effect = None) -> None:
        super().__init__(name, ability_handler, price, drop_chance,attackeffect)
        Tool.__init__(self, name, ability_handler, price, drop_chance, tooleffect , tool_type, tool_strength )
    def get_description(self, dungeon):
        return utility.combine_text([self.useeffect.get_desc(),Tool.get_description(self,dungeon)])
    def get_targets(self, dungeon):
        return dungeon.place.get_roomobjects(lambda x : (isinstance(x, Destructible) and self.can_destroy(x.tool_requirement, x.tool_strength)) or (isinstance(x, Entity) and x != dungeon.actor))
    def get_effect(self, effect) -> Effect:
        return self.tooleffect if isinstance(effect.target, Destructible) else self.useeffect

class Sharpener(UsableItem):
    def get_targets(self, dungeon):
        all_items = dungeon.actor.inventory.get_all_items()
        targets = []
        for x in all_items:
            if hasattr(x, "sharpen"):
                targets.append(x)
        return targets

class Equipment(Item):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None,price : int = 0,  drop_chance : float = 1, slot : str = "?") -> None:
        super().__init__(name, ability_handler, price, drop_chance)
        self.equipment_slot : str = slot
    
    def get_description(self, dungeon):
        return self.ability_handler.get_description(dungeon)

class Weapon(Equipment):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None,price : int = 0,  drop_chance : float = 1, attackeffect : classes.actions.Effect = None) -> None:
        super().__init__(name, ability_handler, price, drop_chance, "Weapon")
        self.attackeffect = attackeffect or Effect()
    
    def get_description(self, dungeon) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return utility.combine_text([self.attackeffect.get_desc(), self.ability_handler.get_description(dungeon)])
    
    def get_effect(self, effect) -> Effect:
        return self.attackeffect
    def use(self, dungeon) -> None:
        pass

class MeleeWeapon(Weapon):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, price : int = 0, drop_chance : float = 1, attackeffect : classes.actions.Effect = None, sharpness : float = 1.0, durability : float = 0.9) -> None:
        super().__init__(name, ability_handler, price, drop_chance, attackeffect)
        self.ability_handler.add_ability(get_ability("melee"))
        self.ability_handler.add_ability(Sharpness(sharpness, durability))
    
    def dull(self, amount : float):
        self.ability_handler.get_ability("sharpness").dull(amount)
    def sharpen(self, amount : float):
        self.ability_handler.get_ability("sharpness").sharpen(amount)

class MagicWeapon(Weapon):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, price : int = 0, drop_chance : float = 1, attackeffect : classes.actions.Effect = None, mana_cost : int = 10) -> None:
        super().__init__(name, ability_handler, price, drop_chance, attackeffect)
        self.ability_handler.add_ability(get_ability("magic"))
        self.ability_handler.add_ability(ManaCost("manacost","Mana Cost", mana_cost))

class MeleeTool(MeleeWeapon, Tool):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, price : int = 0, drop_chance : float = 1, attackeffect : classes.actions.Effect = None, sharpness : float = 1.0, durability : float = 0.9, tooleffect : classes.actions.Effect = None, tool_type : str = "?", tool_strength : str = "?") -> None:
        super().__init__(name, ability_handler, price, drop_chance, attackeffect, sharpness, durability)
        Tool.__init__(self, name, ability_handler, price, drop_chance, tooleffect, tool_type, tool_strength)
    def get_effect(self, effect) -> Effect:
        return self.tooleffect if isinstance(effect.target, Destructible) else self.attackeffect
    def get_description(self, dungeon):
        return utility.combine_text([self.attackeffect.get_desc(),Tool.get_description(self,dungeon)])

class Food(Item):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, price : int = 0, drop_chance : float = 1, foodeffect : classes.actions.Effect = None) -> None:
        super().__init__(name, ability_handler, price, drop_chance)
        self.foodeffect = foodeffect or Effect()
    
    def get_description(self, dungeon) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return utility.combine_text([self.foodeffect.get_desc(), self.ability_handler.get_description(dungeon)])
    
    def get_effect(self, effect) -> Effect:
        return self.foodeffect
    def use(self, dungeon) -> None:
        pass

class Stat:
    def get_text():
        raise NotImplementedError("Subclasses must implement get_text()")

class HPContainer(Stat):
    def __init__(self, current : int, max : int = -1):
        if max == -1:
            self.max : int = current
        else:
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
        return utility.combine_text([(status_color, str(self.current)), " / ", ("healing",str(self.max))], False)
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
        else:
            self.max : int = max
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

class BoneContainer(Stat):
    def __init__(self, current : int, max : int = -1):
        self.max : int = max
        self.current : int = current
    def get_text(self):
        if self.max == -1:
            return ("bone", str(self.current) + " bones")
        else:
            return utility.combine_text([("bone", str(self.current)), " / ", ("bone", str(self.max) + " bones")], False)
    def get_current_bones(self) -> int:
        return self.current
    def spend(self, amount : int) -> bool:
        self.current -= amount
        if self.current < 0:
            self.current = 0
            return False
        return True
    def add(self, amount : int) -> int:
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
    
    def get_description(self, dungeon):
        text_list = []
        for p in self.stat_dict:
            text_list.append([p,": ", self.stat_dict[p].get_text()])
        return utility.combine_text(text_list)

class EquipmentHandler(Interactable):
    def __init__(self, equipment : dict[str:Equipment] = None):
        super().__init__("Equipment")
        self.equipment_dict : dict[str:Equipment] = equipment or {}
    
    def can_equip(self, item : Equipment):
        if hasattr(item, "equipment_slot") and item.equipment_slot in self.equipment_dict:
            return True
        else:
            return False

    def has_equipment_slots(self) -> bool:
        return len(self.equipment_dict.keys()) > 0

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
    
    def get_choices(self, dungeon) -> list[classes.actions.PlayerAction]:
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
    
    def dungeon_init(self, chain : list):
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.equipment_dict.keys():
            ele = self.equipment_dict[x]
            if isinstance(ele, RandomElement):
                self.equipment_dict[x] = ele.dungeon_init(new_chain)

    def reply(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.equipment_dict.values():
            if not x == None:
                x.reply(new_chain, effect)

    def get_items(self) -> list[Equipment]:
        equips : list[Equipment] = []
        for x in self.equipment_dict.values():
            if x != None:
                equips.append(x)
        return equips
    
    def has_ability(self, id):
        for x in self.equipment_dict.values():
            if x != None and x.has_ability(id):
                return True
        return False
    
    def has_item_equipped(self, item : Equipment):
        if self.get_item_in_slot(item.equipment_slot) == item:
            return True
        else:
            return False
    
    def remove_item(self, item : Equipment):
        if self.get_item_in_slot(item.equipment_slot) == item:
            self.equipment_dict[item.equipment_slot] = None

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
    
    def get_description(self, dungeon):
        return ["Size: ", str(self.size)]

    def get_items(self) -> list[Item]:
        return self.items_list

    def get_choices(self, dungeon) -> list[classes.actions.PlayerAction]:
        choices = []
        for x in self.items_list:
            choices.append(classes.actions.PlayerBagInteractAction(x))
        return choices
    
    def apply_statics(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.items_list:
            x.apply_statics_in_bag(new_chain, effect)

    def dungeon_init(self, chain : list):
        new_chain = chain.copy()
        new_chain.append(self)
        for x in range(len(self.items_list)):
            ele = self.items_list[x]
            if isinstance(ele, RandomElement):
                self.items_list[x] = ele.dungeon_init(new_chain)

    def reply(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.items_list:
            x.reply(new_chain, effect)

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
        if self.bag.can_add_item(item):
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

    def get_choices(self, dungeon) -> MutableSequence[classes.actions.PlayerAction]:
        return [classes.actions.PlayerInteractAction(self.equipment_handler), classes.actions.PlayerInteractAction(self.bag)]

    def get_all_items(self) -> list[Item]:
        return self.equipment_handler.get_items() + self.bag.get_items()

    def get_usable_items(self, dungeon) -> list[UsableItem]:
        opts = []
        for x in self.get_all_items():
            if hasattr(x, "can_use") and x.can_use(dungeon):
                opts.append(x)
        return opts

    def apply_statics(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        self.equipment_handler.apply_statics(new_chain, effect)
        self.bag.apply_statics(new_chain, effect)
    
    def dungeon_init(self, chain : list):
        new_chain = chain.copy()
        new_chain.append(self)
        self.equipment_handler.dungeon_init(new_chain)
        self.bag.dungeon_init(new_chain)

    def reply(self, chain : list, effect : Effect):
        new_chain = chain.copy()
        new_chain.append(self)
        self.equipment_handler.reply(new_chain, effect)
        self.bag.reply(new_chain, effect)

    def get_items_in_bag(self, condition = lambda item : True) -> list["Item"]:
        return self.bag.get_items_in_bag(condition)
    
    def has_ability(self, id):
        return self.equipment_handler.has_ability(id)
    
    def remove_item(self, item : Item):
        if isinstance(item, Equipment) and self.equipment_handler.has_item_equipped(item):
            self.equipment_handler.remove_item(item)
        else:
            self.bag.remove_item(item)

class Passage(RoomObject):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], ability_handler : AbilityHandler = None, destination_id : str = "?"):
        super().__init__(name, ability_handler)
        self.destination_id : str = destination_id
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.PlayerAction]:
        return [classes.actions.EnterPassageAction(self)]

class LockedPassage(Passage):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], ability_handler : AbilityHandler = None, destination_id : str = "?", key_id : str = "?"):
        super().__init__(name, ability_handler, destination_id)
        self.key_id : str = key_id
        self.locked : bool = True
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.PlayerAction]:
        if self.locked:
            keys = dungeon.player.get_items_in_bag(lambda item : hasattr(item, "keyeffect") and item.can_unlock(self.key_id))
            if len(keys) > 0:
                choices = []
                for x in keys:
                    choices.append(classes.actions.UnlockAction(self,x))
                return choices
            else:
                return [classes.actions.DummyAction("It's locked.")]
        else:
            return [classes.actions.EnterPassageAction(self)]
    def unlock(self):
        self.locked : bool = False
    def lock(self):
        self.locked : bool = True

class SubmergedPassage(Passage):
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.PlayerAction]:
        if not dungeon.player.has_ability("water_breathing"):
            return [classes.actions.DummyAction("You can't breathe underwater.")]
        else:
            return [classes.actions.EnterPassageAction(self)]

class Destructible(RoomObject):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], ability_handler : AbilityHandler = None, contents : list[RoomObject] = None, tool_requirement : str = "?", tool_strength : int = 0):
        super().__init__(name, ability_handler)
        self.contents : list[RoomObject] = contents or []
        self.tool_requirement : str = tool_requirement
        self.tool_strength : int = tool_strength
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.PlayerAction]:
        tools = dungeon.player.get_items_in_bag(lambda item : hasattr(item, "tooleffect") and item.can_destroy(self.tool_requirement, self.tool_strength))
        if len(tools) > 0:
            choices = []
            for x in tools:
                choices.append(classes.actions.DestroyAction(self,x))
            return choices
        else:
            return [classes.actions.DummyAction("You need a " + self.tool_requirement + " of power " + str(self.tool_strength) + " or greater to destroy this.")]
    def get_drops(self) -> list[Item]:
        all_items : list[Item] = self.contents
        drops : list[Item] = []
        for x in all_items:
            if not hasattr(x, "drop_chance") or random.random() <= x.drop_chance:
                drops.append(x)
        return drops

class Container(RoomObject):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], ability_handler : AbilityHandler = None, contents : list[RoomObject] = None):
        super().__init__(name, ability_handler)
        self.contents : list[RoomObject] = contents or []
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.PlayerAction]:
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


from data.dialogue import DialogueNode
from data.dialogue import get_dialogue

class DialogueManager(Interactable):
    def __init__(self, root_dialogue_id : str = None):
        super().__init__("Talk")
        self.set_dialogue(root_dialogue_id)
        self.speaker = None
        self.include_back = False
    
    def set_dialogue(self, dialogue_id : str | DialogueNode = None):
        self.root_dialogue : DialogueNode = None
        if dialogue_id != None:
            if isinstance(dialogue_id, str):
                self.root_dialogue : DialogueNode = get_dialogue(dialogue_id)
            else:
                self.root_dialogue : DialogueNode = dialogue_id

    def has_dialogue(self) -> bool:
        return self.root_dialogue != None

    def get_description(self, dungeon):
        return self.root_dialogue.get_text()

    def get_choices(self, dungeon):
        dialogue_options = []
        if self.root_dialogue.has_choices():
            for x in self.root_dialogue.get_choices():
                dialogue_options.append(PlayerDialogueAction(self.speaker,get_dialogue(x)))
        else:
            dialogue_options.append(EndRoundAction())
        return dialogue_options

class Entity(RoomObject):
    def __init__(self, name:str | tuple["Hashable", str] | list[str | tuple["Hashable", str]], ability_handler : AbilityHandler = None, inventory : Inventory = None, stathandler : StatHandler = None, dialogue_manager : DialogueManager = None):
        super().__init__(name, ability_handler)
        self.inventory = inventory or Inventory()
        self.stathandler = stathandler or StatHandler()
        self.dialogue_manager = dialogue_manager or DialogueManager()
        self.dialogue_manager.speaker = self
    
    def can_take_item(self, item : Item):
        return self.inventory.can_take_item(item)

    def take_item(self, item : Item):
        self.inventory.take_item(item)
    
    def equip_item(self, item : Equipment):
        self.inventory.equip_item(item)
    
    def has_stat(self, stat: str):
        return self.stathandler.has_stat(stat)
    
    def get_stat(self, stat: str):
        return self.stathandler.get_stat(stat)

    def unequip_item(self, item : Equipment):
        self.inventory.unequip_item(item)

    def can_equip(self, item : Equipment):
        return self.inventory.can_equip(item)
    
    def get_description(self, dungeon):
        return utility.combine_text([self.stathandler.get_description(dungeon), self.ability_handler.get_description(dungeon)])

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
    
    def has_item_to_use(self, dungeon) -> bool:
        item = self.inventory.get_usable_items(dungeon)
        if len(item) > 0:
            return True
        else:
            return False

    def get_item_to_use(self, dungeon) -> UsableItem:
        if len(self.inventory.get_usable_items(dungeon)) == 0:
            return None
        else:
            return self.inventory.get_usable_items(dungeon)

    def get_choices(self, dungeon) -> MutableSequence[classes.actions.PlayerAction]:
        choices : list[classes.actions.PlayerAction] = []
        if self.dialogue_manager.has_dialogue():
            choices.append(classes.actions.PlayerDialogueAction(self, self.dialogue_manager.root_dialogue))
        if dungeon.actor.has_weapon():
            choices.append(classes.actions.AttackAction(self))
        #choices.append(classes.actions.PlayerInteractAction(self.inventory.bag))
        # if self.inventory.equipment_handler.has_equipment_slots():
        #     choices.append(classes.actions.PlayerInteractAction(self.inventory.equipment_handler))
        return choices

    def apply_statics(self, chain : list, effect : Effect):
        super().apply_statics(chain, effect)
        new_chain = chain.copy()
        new_chain.append(self)
        self.inventory.apply_statics(new_chain, effect)
    
    def dungeon_init(self, chain : list):
        super().dungeon_init(chain)
        new_chain = chain.copy()
        new_chain.append(self)
        self.inventory.dungeon_init(new_chain)

    def reply(self, chain : list, effect : Effect):
        super().reply(chain, effect)
        new_chain = chain.copy()
        new_chain.append(self)
        self.inventory.reply(new_chain, effect)

    def has_ability(self, id):
        return super().has_ability(id) or self.inventory.has_ability(id)

class Player(Entity):
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.PlayerAction]:
        choices : list[classes.actions.PlayerAction] = []
        choices.append(classes.actions.PlayerInteractAction(self.inventory.equipment_handler))
        choices.append(classes.actions.PlayerInteractAction(self.inventory.bag))
        return choices
    
class StateEntity(Entity):
    def __init__(self, name, ability_handler = None, inventory = None, stathandler = None, dialogue_manager : DialogueManager = None, state : State = None):
        super().__init__(name, ability_handler, inventory, stathandler, dialogue_manager)
        self.default_state : State= state or IdleState()
        self.state : State = None
        
        self.change_to_default_state(None, False)
    
    def change_to_default_state(self, dungeon = None, act : bool = False):
        self.change_state(self.default_state, dungeon, act)

    def change_state(self, new_state : State, dungeon = None, act : bool = False):
        if self.state != None:
            self.state.unregister(self)
        self.state : State = new_state
        self.state.register(self)
        if act:
            self.state.decide(dungeon)

    def take_turn(self, dungeon) -> None:
        self.state.decide(dungeon)
        return

class ShopManager(Interactable):
    def __init__(self, items : dict[Item:int] = None):
        super().__init__("Buy")
        self.items_dict : dict[Item:int] = items or {}

    def get_description(self, dungeon):
        return dungeon.player.get_stat("Bones").get_text()

    def get_choices(self, dungeon) -> list[classes.actions.PlayerAction]:
        choices = []
        for x in self.items_dict:
            choices.append(classes.actions.PlayerBuyAction(x, self.items_dict[x]))
        return choices

class Vendor(StateEntity):
    def __init__(self, name, ability_handler=None, inventory=None, stathandler=None, dialogue_manager = None, state = None, shop_manager : ShopManager = None):
        super().__init__(name, ability_handler, inventory, stathandler, dialogue_manager, state)
        self.shop_manager = shop_manager or ShopManager()
    
    def get_choices(self, dungeon) -> MutableSequence[classes.actions.PlayerAction]:
        choices : list[classes.actions.PlayerAction] = []
        choices.append(classes.actions.PlayerInteractAction(self.shop_manager))
        choices.append(classes.actions.SellMenuAction(self.shop_manager))
        if self.dialogue_manager.has_dialogue():
            choices.append(classes.actions.PlayerDialogueAction(self, self.dialogue_manager.root_dialogue))
        if dungeon.actor.has_weapon():
            choices.append(classes.actions.AttackAction(self))
        # if self.inventory.equipment_handler.has_equipment_slots():
        #     choices.append(classes.actions.PlayerInteractAction(self.inventory.equipment_handler))
        return choices

class Room(Actor):
    def __init__(self, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], ability_handler : AbilityHandler = None, room_contents : list["RoomObject"] = None) -> None:
        self.room_contents : list[RoomObject] = room_contents or []
        self.discovered : bool = False 
        # if len(self.get_roomobjects(lambda item : isinstance(item, Campfire))) > 0:
        #    self.discovered = True# TODO: change to False
        super().__init__(name, ability_handler)
    
    def get_choices(self, dungeon) -> list[classes.actions.PlayerAction]:
        choices = []
        for x in self.get_roomobjects(lambda item : isinstance(item, Entity) and not isinstance(item, Player)):
            choices.append(classes.actions.PlayerInteractAction(x))
        for x in self.get_roomobjects(lambda item : not (isinstance(item, Entity) or isinstance(item, Passage))):
            choices.append(classes.actions.PlayerInteractAction(x))
        for x in self.get_roomobjects(lambda item : isinstance(item, Passage)):
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

    def get_roomobject_of_id(self, id : str) -> RoomObject:
        for x in self.room_contents:
            if x.is_id(id):
                return x
        return None

    def get_player(self) -> Player:
        for x in self.room_contents:
            if isinstance(x, Player):
                return x
        return None

    def add_to_action_queue(self, action_queue : list) -> None:
        action_queue.append(self)
        for x in self.get_roomobjects(lambda item : not isinstance(item, Player)):
            x.add_to_action_queue(action_queue)
    
    def dungeon_init(self, chain : list):
        super().dungeon_init(chain)
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.room_contents:
            x.dungeon_init(new_chain)

    def apply_statics(self, chain : list, effect : Effect):
        super().apply_statics(chain, effect)
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.room_contents:
            x.apply_statics(new_chain, effect)

    def reply(self, chain : list, effect : Effect):
        super().reply(chain, effect)
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.room_contents:
            x.reply(new_chain, effect)

    def end_of_round(self, chain) -> None:
        super().end_of_round(chain)
        new_chain = chain.copy()
        new_chain.append(self)
        for x in self.room_contents:
            x.end_of_round(new_chain)