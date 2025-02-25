
import sys
import typing
import utility
import copy
import math
import random
if typing.TYPE_CHECKING:
    from collections.abc import Callable, Hashable, MutableSequence
    from classes.interactable import *
    from classes.interactable import Interactable
    from classes.interactable import Equipment
    from classes.interactable import Item
    from classes.interactable import Campfire

class Effect:
    """Effects govern communication between Actors."""
    def execute_with_statics_and_reformat(self, dungeon, reformat_dict : dict, deepcopy : bool = False):
        fresh_effect : Effect = copy.deepcopy(self) if deepcopy else self
        fresh_effect.reformat(dungeon, reformat_dict)
        dungeon.apply_statics(fresh_effect)
        if not fresh_effect.cancelled:
            fresh_effect.execute(dungeon)
            dungeon.reply(fresh_effect)
    def execute_with_statics(self, dungeon, deepcopy : bool = False):
        fresh_effect : Effect = copy.deepcopy(self) if deepcopy else self
        dungeon.apply_statics(fresh_effect)
        if not fresh_effect.cancelled:
            fresh_effect.execute(dungeon)
            dungeon.reply(fresh_effect)
    def reformat(self, dungeon, reformat_dict : dict):
        for x in vars(self):
            if isinstance(vars(self)[x], str):
                reform_str : str = vars(self)[x]
                if reform_str in reformat_dict:
                    vars(self)[x] = reformat_dict[reform_str]
                elif ":" in reform_str:
                    reform_list : list[str] = reform_str.split(":")
                    if reform_list[0] == "id":
                        vars(self)[x] = dungeon.place.get_roomobject_of_id(reform_list[1])
                    elif reform_list[0] == "roomid":
                        vars(self)[x] = dungeon.map[reform_list[1]].get_roomobject_of_id(reform_list[2])
    def __init__(self):
        super().__init__()
        self.cancelled : bool = False
    def execute(self, dungeon):
        pass
    def get_desc(self):
        return None
    def cancel(self):
        self.cancelled : bool = True

class Notif:
    """Notifs are used for States that trigger off of Effects."""
    def __init__(self, effect : Effect):
        self.effect : Effect = effect

class RemoveRoomObjEffect(Effect):
    """Removes the target from the source."""
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
    def execute(self, dungeon):
        self.source.remove_roomobject(self.target)

class AddRoomObjEffect(Effect):
    """Adds the target to the source."""
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
    def execute(self, dungeon):
        self.source.add_roomobject(self.target)
        self.target.dungeon_init([dungeon])
        self.target.handle_connecting_signals(dungeon)

class EndStatusEffect(Effect):
    """Removes the target Status from the source's AbilityHandler."""
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
    def execute(self, dungeon):
        dungeon.add_to_message_queue_if_actor_visible(self.source, [self.source.get_name(), "'s ", self.target.get_name(), " expired."])
        RemoveAbilityEffect(self.source, self.target).execute(dungeon)

class RemoveAbilityEffect(Effect):
    """Removes the target Ability from the source's AbilityHandler."""
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
    def execute(self, dungeon):
        self.source.remove_ability(self.target)

class AddAbilityEffect(Effect):
    """Adds the target Ability to the source's AbilityHandler."""
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
    def get_desc(self):
        return ["Apply ", self.target.get_name()]
    def execute(self, dungeon):
        if self.source.has_ability(self.target.id):
            existing_ability = self.source.get_ability(self.target.id)
            if self.target > existing_ability:
                self.source.remove_ability(existing_ability)
            else:
                return
        dungeon.add_to_message_queue_if_actor_visible(self.source, [self.source.get_name(), " gained ", self.target.get_name(), "."])
        self.source.add_ability(self.target)

class SetDialogueEffect(Effect):
    """Sets the target's dialogue to the source."""
    def __init__(self, source , target):
        super().__init__()
        self.source = source
        self.target = target
    def execute(self, dungeon):
        self.target.dialogue_manager.set_dialogue(self.source)

class EffectSequence(Effect):
    """Used when multiple effects must happen."""
    def __init__(self, effects : list[Effect]):
        super().__init__()
        self.effects : list[Effect] = effects
    
    def get_desc(self):
        effect_text = []
        for x in self.effects:
            effect_text.append(x.get_desc())
        return utility.combine_text(effect_text)

    def execute(self, dungeon):
        for x in self.effects:
            x.execute_with_statics(dungeon, True)
    
    def execute_with_statics_and_reformat(self, dungeon, reformat_dict, deepcopy : bool):
        dungeon.apply_statics(self)
        for x in self.effects:
            x.execute_with_statics_and_reformat(dungeon, reformat_dict, True)
        dungeon.reply(self)

class AddtoInventoryEvent(Effect):
    """Adds the target to the source's inventory. If it cannot, then adds to the room"""
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
    def get_desc(self):
        return ["Adds to inventory"]
    
    def execute(self, dungeon):
        if self.source.can_take_item(self.target):
            self.source.take_item(self.target)
        else:
            AddRoomObjEffect(dungeon.place, self.target).execute(dungeon)

class RemoveFromInventoryEvent(Effect):
    """Removes the target from the source's inventory."""
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
    def get_desc(self):
        return ["Removes from inventory"]
    
    def execute(self, dungeon):
        self.source.remove_item(self.target)

class DeathEvent(Effect):
    """The target dies. The target's drops are added to its current room."""
    def __init__(self, target):
        super().__init__()
        self.target = target
    def get_desc(self):
        return ["Dies"]
    
    def execute(self, dungeon):
        death_room = dungeon.get_location_of_actor(self.target)
        if death_room != None:
            dungeon.add_to_message_queue_if_actor_visible(self.target, [self.target.get_name(), " dies."])
            if self.target == dungeon.player:
                dungeon.game_over = True
            else:
                if dungeon.actor == dungeon.player:
                    if self.target.has_stat("Bones"):
                        dungeon.add_to_message_queue_if_actor_visible(self.target, [self.target.get_name(), " dropped ", ("bone", str(self.target.get_stat("Bones").get_current_bones()) + " Bones"),"."])
                        dungeon.player.get_stat("Bones").add(self.target.get_stat("Bones").get_current_bones())
                for x in self.target.get_drops():
                    x.drop_chance = 1
                    AddRoomObjEffect(death_room, x).execute(dungeon)
                    dungeon.add_to_message_queue_if_actor_visible(self.target, [self.target.get_name(), " dropped ", x.get_name(), "."])
            RemoveRoomObjEffect(death_room, self.target).execute(dungeon)

class DamageEvent(Effect):
    """Deals damage from the source to the target."""
    def __init__(self, source = "item", target = "target", damage : int = 1, damage_type : str = "", armor_penetrate : int = 0):
        super().__init__()
        self.source = source
        self.target = target
        self.damage : int = damage
        self.damage_type : str = damage_type
        self.armor_penetrate : int = armor_penetrate
    def get_desc(self):
        desc = []
        damage_text = str(self.damage)
        if self.damage_type != "":
            damage_text += " " + self.damage_type
        desc.append(["Deal ", (self.damage_type, damage_text), " damage"])
        if self.armor_penetrate == -1:
            desc.append([" ignoring armor"])
        elif self.armor_penetrate > 0:
            desc.append([" with ", str(self.armor_penetrate), " armor penetration"])
        return utility.combine_text(desc, False)
    
    def execute(self, dungeon):
        if self.damage < 1:
            self.damage = 1
        damage_text = str(self.damage)
        if self.damage_type != "":
            damage_text += " " + self.damage_type
        dungeon.add_to_message_queue_if_actor_visible(self.target,[self.target.get_name(), " is dealt ", (self.damage_type, damage_text + " damage"), " by ", self.source.get_name(), "."])
        self.target.get_stat("HP").damage(self.damage)
        self.target.notify(dungeon, Notif(self))
        if self.target.get_stat("HP").is_dead():
            DeathEvent(self.target).execute_with_statics(dungeon)

class RepeatEvent(Effect):
    """Repeats the effect an amount of times."""
    def __init__(self, effect : Effect, amount : int):
        super().__init__()
        self.effect : Effect = effect
        self.amount : int = amount
    def get_desc(self):
        return utility.combine_text([["(x",str(self.amount),") "], self.effect.get_desc()], False)
    def reformat(self, dungeon, reformat_dict : dict):
        super().reformat(dungeon, reformat_dict)
        self.effect.reformat(dungeon, reformat_dict)
    def execute(self, dungeon):
        for x in range(self.amount):
            self.effect.execute_with_statics(dungeon, True)
    def execute_with_statics_and_reformat(self, dungeon, reformat_dict, deepcopy : bool):
        dungeon.apply_statics(self)
        for x in range(self.amount):
            self.effect.execute_with_statics_and_reformat(dungeon, reformat_dict, True)
        dungeon.reply(self)

class ProbabilityEvent(Effect):
    """Repeats the effect an amount of times."""
    def __init__(self, effect : Effect, chance : float):
        super().__init__()
        self.effect : Effect = effect
        self.chance : int = chance
    def get_desc(self):
        percent : int = math.floor(self.chance * 100)
        return utility.combine_text([["(",str(percent),"%) "], self.effect.get_desc()], False)
    def reformat(self, dungeon, reformat_dict : dict):
        super().reformat(dungeon, reformat_dict)
        self.effect.reformat(dungeon, reformat_dict)
    def execute(self, dungeon):
        if random.random() <= self.chance:
            copy.deepcopy(self.effect).execute_with_statics(dungeon, True)
    def execute_with_statics_and_reformat(self, dungeon, reformat_dict, deepcopy : bool):
        dungeon.apply_statics(self)
        if random.random() <= self.chance:
            self.effect.execute_with_statics_and_reformat(dungeon, reformat_dict, True)
        dungeon.reply(self)

class HealEvent(Effect):
    """Heals the target by an amount."""
    def __init__(self, source, target, healing : int):
        super().__init__()
        self.source = source
        self.target = target
        self.healing : int = healing
    def get_desc(self):
        return ["Heal ",("healing",str(self.healing)+ " HP")]
    def execute(self, dungeon):
        dungeon.add_to_message_queue_if_actor_visible(self.target, [self.target.get_name(), " is healed ", ("healing",str(self.healing)+ " HP"), " by ", self.source.get_name(), "."])
        new_hp = self.target.get_stat("HP").heal(self.healing)

class DullWeaponEvent(Effect):
    """Dulls the target by an amount."""
    def __init__(self, source, target, dulling : float):
        super().__init__()
        self.source = source
        self.target = target
        self.dulling : float = dulling
    def execute(self, dungeon):
        self.target.dull(self.dulling)

class SharpenEvent(Effect):
    """Sharpens the target by an amount."""
    def __init__(self, source, target, sharpening : float):
        super().__init__()
        self.source = source
        self.target = target
        self.sharpening : float= sharpening
    def get_desc(self):
        percent : int = math.floor(self.sharpening * 100)
        return ["Sharpen an item ", ("iron",str(percent) + "%")]
    def execute(self, dungeon):
        percent : int = math.floor(self.sharpening * 100)
        dungeon.add_to_message_queue_if_visible([self.target.get_name(), " is sharpened ", ("iron",str(percent) + "%"), " by ", self.source.get_name(), "."])
        self.target.sharpen(self.sharpening)

class SpendMPEvent(Effect):
    """The target spends MP."""
    def __init__(self, source, target, spending : int):
        super().__init__()
        self.source = source
        self.target = target
        self.spending : int = spending
    def get_desc(self):
        return ["Spend ",("magic", str(self.spending) + " MP")]
    def execute(self, dungeon):
        dungeon.add_to_message_queue_if_actor_visible(self.target, [self.target.get_name(), " spent ", ("magic", str(self.spending) + " MP"), "."])
        self.target.get_stat("MP").spend(self.spending)

class RestoreMPEvent(Effect):
    """The target restores MP."""
    def __init__(self, source, target, restoring : int):
        super().__init__()
        self.source = source
        self.target = target
        self.restoring : int = restoring
    def get_desc(self):
        return ["Restore ",("magic", str(self.restoring) + " MP")]
    def execute(self, dungeon):
        dungeon.add_to_message_queue_if_actor_visible(self.target, [self.target.get_name(), " restored ", ("magic", str(self.restoring) + " MP"), "."])
        self.target.get_stat("MP").restore(self.restoring)

class UseEffect(Effect):
    """The source uses the item against the target. Verb determines the context of usage."""
    def __init__(self, source, target, item, verb : str):
        super().__init__()
        self.source = source
        self.target = target
        self.item = item
        self.verb : str = verb
    def execute(self, dungeon) -> None:
        message = []
        message.append(self.source.get_name())
        message.append(" ")
        message.append(self.verb)
        message.append("s ")
        if self.target != None:
            message.append(self.target.get_name())
            message.append(" with ")
        message.append(self.item.get_name())
        message.append(".")
        dungeon.add_to_message_queue_if_visible(message)
        reformat_dict = {
            "place":dungeon.place, 
            "user":self.source, 
            "target":self.target, 
            "item":self.item
        }
        new_effect : Effect = copy.deepcopy(self.item.get_effect(self))
        new_effect.execute_with_statics_and_reformat(dungeon, reformat_dict, True)
        self.item.use(dungeon)

class EnterPassageEffect(Effect):
    """The source enters the target."""
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target

    def execute(self, dungeon):
        source_room = dungeon.place
        target_room = dungeon.map[self.target.destination_id]
        if not self.source == dungeon.player:
            dungeon.add_to_message_queue_if_actor_visible(self.source, [self.source.get_name(), " exits ", source_room.get_name(),"."])
        RemoveRoomObjEffect(source_room, self.source).execute(dungeon)
        AddRoomObjEffect(target_room, self.source).execute(dungeon)
        dungeon.update_location()
        dungeon.add_to_message_queue_if_actor_visible(self.source, [self.source.get_name(), " enters ", target_room.get_name(),"."])
        
class UnlockEffect(Effect):
    """The source unlocks the target."""
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target

    def execute(self, dungeon):
        if self.target != None:
            self.target.unlock()
    def get_desc(self):
        return "Unlocks something..."

class LockEffect(Effect):
    """The source unlocks the target."""
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target

    def execute(self, dungeon):
        if self.target != None:
            self.target.lock()
    def get_desc(self):
        return "Locks something..."

class DestroyEffect(Effect):
    """The source destroys the target."""
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target

    def execute(self, dungeon):
        death_room = dungeon.get_location_of_actor(self.target)
        if death_room != None:
            dungeon.add_to_message_queue_if_actor_visible(self.target, [self.target.get_name(), " was destroyed."])
            for x in self.target.get_drops():
                x.drop_chance = 1
                AddRoomObjEffect(death_room, x).execute(dungeon)
                dungeon.add_to_message_queue_if_actor_visible(self.target, [self.target.get_name(), " dropped ", x.get_name(), "."])
            RemoveRoomObjEffect(death_room, self.target).execute(dungeon)
    def get_desc(self):
        return "Can destroy objects"

class TakeItemEffect(Effect):
    """The target takes the item from the source."""
    def __init__(self, source, target, item):
        super().__init__()
        self.source = source
        self.target = target
        self.item = item
    
    def execute(self, dungeon) -> None:
        if not self.target.can_take_item(self.item):
            return
        RemoveRoomObjEffect(self.source, self.item).execute(dungeon)
        AddtoInventoryEvent(self.target, self.item).execute(dungeon)
        dungeon.add_to_message_queue_if_actor_visible(self.source, [self.target.get_name(), " takes ", self.item.get_name(), "."])

class EquipItemEffect(Effect):
    """The target equips the item from the source."""
    def __init__(self, source, target, item):
        super().__init__()
        self.source = source
        self.target = target
        self.item = item
    
    def execute(self, dungeon) -> None:
        if self.source != None:
            RemoveRoomObjEffect(self.source, self.item).execute(dungeon)
        self.target.equip_item(self.item)
        dungeon.add_to_message_queue_if_visible([dungeon.actor.get_name(), " equipped the ", self.item.get_name(), "."])

class GiveItemEffect(Effect):
    """The source gives the target an item."""
    def __init__(self, source, target, item):
        super().__init__()
        self.source = source
        self.target = target
        self.item = item
    
    def execute(self, dungeon) -> None:
        if not self.target.can_take_item(self.item):
            return
        if hasattr(self.item,"equipment_slot") and self.target.inventory.equipment_handler.can_equip_without_swap(self.item):
            self.target.equip_item(self.item)
        else:
            AddtoInventoryEvent(self.target, self.item).execute(dungeon)
        dungeon.add_to_message_queue_if_actor_visible(self.source, [self.source.get_name(), " gives ",self.target.get_name()," ", self.item.get_name(), "."])

class PlayerAction:
    """Effects which the player can call."""
    def __init__(self):
        self.prev = None
    def get_name(self):
        pass

    def get_description(self, dungeon):
        return None

    def execute(self, dungeon):
        pass

class DummyAction(PlayerAction):
    """Used for effects that don't do anything."""
    def __init__(self, name : str | tuple["Hashable", str] | list[str | tuple["Hashable", str]]):
        super().__init__()
        self.name : str | tuple["Hashable", str] | list[str | tuple["Hashable", str]] = name
    def execute(self, dungeon):
        pass
    def get_name(self):
        return self.name

class EndRoundAction(PlayerAction):
    """Used for ending the round."""
    def execute(self, dungeon):
        dungeon.end_current_turn()
    def get_name(self):
        return "Continue"

class PlayerInteractAction(PlayerAction):
    """Interacting with the interactable."""
    def __init__(self, interactable : "Interactable"):
        super().__init__()
        self.interactable : "Interactable" = interactable
    
    def execute(self, dungeon):
        dungeon.player_interact(self)

    def get_name(self):
        return self.interactable.get_name()

    def get_description(self, dungeon):
        return self.interactable.get_description(dungeon)

    def get_choices(self, dungeon) -> list[PlayerAction]:
        return self.interactable.get_choices(dungeon)

class PlayerEquippedInteractAction(PlayerInteractAction):
    """Interacting with an equipped item."""
    def __init__(self, interactable : "Equipment", player_inv : bool):
        super().__init__(interactable)
        self.player_inv = player_inv
    
    def get_name(self):
        return [self.interactable.equipment_slot, ": ", self.interactable.get_name()]

    def get_choices(self, dungeon) -> list[PlayerAction]:
        actions = []
        if self.player_inv:
            if dungeon.actor.can_take_item(self.interactable):
                actions.append(UnequipItemAction(self.interactable))
            for x in dungeon.player.get_items_in_bag(lambda item : hasattr(item, "equipment_slot") and item.equipment_slot == self.interactable.equipment_slot):
                actions.append(EquipItemAction(x))
        return actions

class PlayerBagInteractAction(PlayerInteractAction):
    """Interacting with an item in the bag."""
    def __init__(self, interactable : "Item"):
        super().__init__(interactable)
    
    def get_choices(self, dungeon) -> list[PlayerAction]:
        actions = []
        if hasattr(self.interactable, "equipment_slot") and dungeon.actor.can_equip(self.interactable):
            actions.append(EquipItemAction(self.interactable))
        if hasattr(self.interactable, "useeffect") and self.interactable.can_use(dungeon) :
            actions.append(UseItemAction(self.interactable))
        actions.append(DiscardItemAction(self.interactable))
        return actions

class PlayerDialogueAction(PlayerAction):
    """Talking to an entity with dialogue."""
    def __init__(self, speaker , dialogue):
        super().__init__()
        self.speaker = speaker
        self.dialogue = dialogue
    
    def get_name(self):
        return self.dialogue.get_response_text()

    def execute(self, dungeon):
        SetDialogueEffect(self.dialogue, self.speaker).execute_with_statics(dungeon)
        dungeon.player_interact(PlayerInteractAction(self.speaker.dialogue_manager))
        if self.dialogue.get_effect() != None:
            reformat_dict = {
                "player":dungeon.player, 
                "speaker":self.speaker
            }
            new_effect : Effect = copy.deepcopy(self.dialogue).get_effect()
            new_effect.execute_with_statics_and_reformat(dungeon, reformat_dict, True)

class EnterPassageAction(PlayerAction):
    """Entering a passage."""
    def __init__(self, target):
        super().__init__()
        self.target = target
    def execute(self, dungeon):
        EnterPassageEffect(dungeon.player, self.target).execute(dungeon)
        dungeon.end_current_turn()
    def get_name(self):
        return "Enter"

class UnlockAction(PlayerAction):
    """Interacting with the interactable."""
    def __init__(self, target, key):
        super().__init__()
        self.target = target
        self.key = key
    def execute(self, dungeon):
        UseEffect(dungeon.player, self.target, self.key, "unlock").execute_with_statics(dungeon)
        dungeon.end_current_turn()
    def get_name(self):
        return utility.combine_text(["Unlock using ",self.key.get_name()], False)

class DestroyAction(PlayerAction):
    """Destroying something."""
    def __init__(self, target, tool):
        super().__init__()
        self.target = target
        self.tool = tool
    def execute(self, dungeon):
        UseEffect(dungeon.player, self.target, self.tool, "destroy").execute_with_statics(dungeon)
        dungeon.end_current_turn()
    def get_name(self):
        return utility.combine_text(["Use ",self.tool.get_name()], False)

class CampfireAction(PlayerInteractAction):
    def get_name(self):
        return "Rest"

    def get_choices(self, dungeon) -> list[PlayerAction]:
        actions = []
        for x in dungeon.actor.get_items_in_bag(lambda item : hasattr(item,"foodeffect")):
            actions.append(EatAction(x, self.interactable))
        return actions

class SellMenuAction(PlayerInteractAction):
    def get_name(self):
        return "Sell"
    
    def get_description(self, dungeon):
        return dungeon.player.get_stat("Bones").get_text()

    def get_choices(self, dungeon) -> list[PlayerAction]:
        actions = []
        for x in dungeon.actor.get_items_in_bag(lambda item : item.price > 0):
            actions.append(SellItemAction(x))
        return actions

class DreamAction(PlayerInteractAction):
    def get_name(self):
        return "Dream"

    def get_choices(self, dungeon) -> list[PlayerAction]:
        actions = []
        for x in dungeon.get_discovered_campfire_rooms():
            if x != dungeon.place:
                actions.append(TeleportAction(x, self.interactable))
        return actions

class PlayerBuyAction(PlayerAction):
    def __init__(self, item, price):
        super().__init__()
        self.item = item
        self.price = price
    
    def execute(self, dungeon) -> None:
        if dungeon.player.can_take_item(self.item) and dungeon.actor.get_stat("Bones").get_current_bones() >= self.price:
            dungeon.add_to_message_queue([dungeon.player.get_name(), " bought ", self.item.get_name(), "."])
            AddtoInventoryEvent(dungeon.player, self.item).execute_with_statics(dungeon)
            dungeon.actor.get_stat("Bones").spend(self.price)
            dungeon.end_current_turn()
    
    def get_name(self):
        return ["Buy ", self.item.get_name(), ": ", ("bone", str(self.price) + " bones")]

class TakeItemAction(PlayerAction):
    def __init__(self, item, source):
        super().__init__()
        self.item = item
        self.source = source
    
    def execute(self, dungeon) -> None:
        if not dungeon.player.can_take_item(self.item):
            dungeon.end_current_turn()
            return
        TakeItemEffect(self.source, dungeon.player, self.item).execute_with_statics(dungeon)
        dungeon.end_current_turn()
    
    def get_name(self):
        return ["Take ", self.item.get_name()]

class UnequipItemAction(PlayerAction):
    def __init__(self, item : "Equipment"):
        super().__init__()
        self.item = item
    
    def execute(self, dungeon) -> None:
        if not dungeon.actor.can_take_item(self.item):
            return
        dungeon.actor.unequip_item(self.item)
        self.prev.prev.execute(dungeon)
    
    def get_name(self):
        return ["Unequip ", self.item.get_name()]

class UseItemAction(PlayerInteractAction):
    def execute(self, dungeon):
        if len(self.interactable.get_targets(dungeon)) <= 1:
            choices = self.interactable.get_targets(dungeon)
            if len(choices) == 0:
                choices = [None]
            UseAction(self.interactable, choices[0]).execute(dungeon)
        else:
            dungeon.player_interact(self)

    def get_choices(self, dungeon) -> list[PlayerAction]:
        actions = []
        targets = self.interactable.get_targets(dungeon)
        for x in targets:
            actions.append(UseAction(self.interactable, x))
        return actions

    def get_name(self):
        return "Use"

class EquipItemAction(PlayerAction):
    def __init__(self, item : "Equipment", source = None):
        self.item = item
        self.source = source
    
    def execute(self, dungeon) -> None:
        EquipItemEffect(self.source, dungeon.actor, self.item).execute_with_statics(dungeon)
        dungeon.end_current_turn()
    
    def get_name(self):
        return ["Equip ", self.item.get_name()]

class DiscardItemAction(PlayerAction):
    def __init__(self, item : "Item"):
        super().__init__()
        self.item = item
    
    def execute(self, dungeon) -> None:
        dungeon.actor.remove_item(self.item)
        AddRoomObjEffect(dungeon.place, self.item).execute(dungeon)
        #dungeon.add_to_message_queue_if_visible([dungeon.actor.get_name(), " discarded the ", self.item.get_name(), "."])
        #dungeon.end_current_turn()
        self.prev.prev.execute(dungeon)
    
    def get_name(self):
        return ["Discard ", self.item.get_name()]

class SellItemAction(PlayerAction):
    def __init__(self, item : "Item"):
        super().__init__()
        self.item = item
    
    def execute(self, dungeon) -> None:
        dungeon.actor.remove_item(self.item)
        dungeon.actor.get_stat("Bones").add(self.item.price)
        #dungeon.add_to_message_queue_if_visible([dungeon.actor.get_name(), " discarded the ", self.item.get_name(), "."])
        #dungeon.end_current_turn()
        self.prev.execute(dungeon)
    
    def get_name(self):
        return ["Sell ", self.item.get_name(), ": ", ("bone", str(self.item.price) + " bones")]

class EatAction(PlayerAction):
    def __init__(self, food, campfire):
        super().__init__()
        self.food = food
        self.campfire = campfire
    
    def execute(self, dungeon) -> None:
        dungeon.add_to_message_queue_if_visible([dungeon.actor.get_name(), " rests at ", self.campfire.get_name(), "."])
        UseEffect(dungeon.player, None, self.food, "eat").execute_with_statics(dungeon)
        RestoreMPEvent(self.food, dungeon.player, 10).execute_with_statics(dungeon)
        dungeon.end_current_turn()
    
    def get_name(self):
        return ["Eat ", self.food.get_name()]

class TeleportAction(PlayerAction):
    def __init__(self, room, campfire):
        super().__init__()
        self.room = room
        self.campfire = campfire
    
    def execute(self, dungeon) -> None:
        dungeon.add_to_message_queue_if_visible([dungeon.actor.get_name(), " rests at ", self.campfire.get_name(), "."])
        dungeon.add_to_message_queue_if_visible([dungeon.actor.get_name(), " dreams of ", self.room.get_name(), "."])
        source_room = dungeon.place
        RemoveRoomObjEffect(source_room, dungeon.player).execute(dungeon)
        AddRoomObjEffect(self.room, dungeon.player).execute(dungeon)
        dungeon.end_current_turn()
    
    def get_name(self):
        return ["Dream of ", self.room.get_name()]

class UseAction(PlayerAction):
    def __init__(self, item, target, verb : str = "use"):
        super().__init__()
        self.item = item
        self.target = target
        self.verb = verb
    
    def execute(self, dungeon) -> None:
        UseEffect(dungeon.player, self.target, self.item, self.verb).execute_with_statics(dungeon)
        dungeon.end_current_turn()
    
    def get_name(self):
        if self.target != None:
            return self.target.get_name()
        else:
            return self.verb.capitalize()

class AttackAction(PlayerAction):
    def __init__(self, entity):
        super().__init__()
        self.entity = entity
    
    def execute(self, dungeon) -> None:
        UseEffect(dungeon.player, self.entity, dungeon.player.get_weapon(), "attack").execute_with_statics(dungeon)
        dungeon.end_current_turn()
    
    def get_name(self):
        return "Attack"

class UIAction:
    def execute(self, game_handler):
        raise NotImplementedError("Subclasses must implement execute()")

class InteractAction(UIAction):
    def __init__(self, inter : PlayerInteractAction):
        self.inter : PlayerInteractAction = inter

    def execute(self, game_handler) -> None:
        game_handler.player_interact(self.inter)

class MessageQueueAction(UIAction):
    def __init__(self, queue):
        self.queue = queue
    
    def execute(self, game_handler) -> None:
        game_handler.show_message_queue(self.queue)

