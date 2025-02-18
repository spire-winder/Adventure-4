
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
    def execute_with_statics(self, dungeon, source, target):
        self.dungeon = dungeon
        self.source = source
        self.target = target
        self.cancelled = False
        dungeon.apply_statics(self)
        if not self.cancelled:
            self.execute(self.dungeon, self.source, self.target)
    def execute(self, dungeon, source, target):
        raise NotImplementedError("Subclasses must implement execute()")
    def get_desc(self):
        return []
    def cancel(self):
        self.cancelled = True

class Notif:
    def __init__(self, effect : Effect):
        self.effect : Effect = effect

class RemoveRoomObjEffect(Effect):
    def execute(self, dungeon, source, target):
        source.remove_roomobject(target)

class AddRoomObjEffect(Effect):
    def execute(self, dungeon, source, target):
        source.add_roomobject(target)
        target.handle_connecting_signals(dungeon)

class EndStatusEffect(Effect):
    def execute(self, dungeon, source, target):
        dungeon.add_to_message_queue_if_actor_visible(source, [source.get_name(), "'s ", target.get_name(), " expired."])
        RemoveAbilityEffect().execute(dungeon, source, target)

class RemoveAbilityEffect(Effect):
    def execute(self, dungeon, source, target):
        source.remove_ability(target)

class AddAbilityEffect(Effect):
    def get_desc(self):
        return ["Apply"]
    def execute(self, dungeon, source, target):
        if target.has_ability(source.id):
            existing_ability = target.get_ability(source.id)
            if source > existing_ability:
                target.remove_ability(existing_ability)
            else:
                return
        dungeon.add_to_message_queue_if_actor_visible(target, [target.get_name(), " gained ", source.get_name(), "."])
        target.add_ability(source)

class SetDialogueEffect(Effect):
    def execute(self, dungeon, source, target):
        source.set_dialogue(target)

class EffectSequence(Effect):
    def __init__(self, effects : list[Effect]):
        self.effects : list[Effect] = effects
    
    def get_desc(self):
        effect_text = []
        for x in self.effects:
            effect_text.append(x.get_desc())
        return utility.combine_text(effect_text)
    
    def execute_with_statics(self, dungeon, source, target):
        self.dungeon = dungeon
        self.source = source
        self.target = target
        self.cancelled = False
        dungeon.apply_statics(self)
        if not self.cancelled:
            for x in self.effects:
                x.execute_with_statics(dungeon, source, target)

    def execute(self, dungeon, source, target):
        for x in self.effects:
            x.execute(dungeon, source, target)

class AddtoInventoryEvent(Effect):
    def get_desc(self):
        return ["Adds to inventory"]
    
    def execute(self, dungeon, source, target):
        source.take_item(target)

class DeathEvent(Effect):
    def get_desc(self):
        return ["Dies"]
    
    def execute(self, dungeon, source, target):
        death_room = dungeon.get_location_of_actor(target)
        if death_room != None:
            dungeon.add_to_message_queue_if_actor_visible(target, [target.get_name(), " dies."])
            if target == dungeon.player:
                dungeon.game_over = True
            else:
                for x in target.get_drops():
                    x.drop_chance = 1
                    AddRoomObjEffect().execute(dungeon, death_room, x)
                    dungeon.add_to_message_queue_if_actor_visible(target, [target.get_name(), " dropped the ", x.get_name(), "."])
                if target.has_ability("goblin_boss"):
                    dungeon.add_to_message_queue(["You've completed the demo! Feel free to continue to explore, or try to fight the travellers as well for more items."])
            RemoveRoomObjEffect().execute(dungeon, death_room, target)

class DamageEvent(Effect):
    def __init__(self, damage : int, damage_type : str = "", armor_penetrate : int = 0):
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
    
    def execute(self, dungeon, source, target):
        if self.damage < 1:
            self.damage = 1
        damage_text = str(self.damage)
        if self.damage_type != "":
            damage_text += " " + self.damage_type
        dungeon.add_to_message_queue_if_actor_visible(target,["Dealt ", (self.damage_type, damage_text), " damage."])
        target.stathandler.get_stat("HP").damage(self.damage)
        target.notify(dungeon, Notif(self))
        if target.stathandler.get_stat("HP").is_dead():
            DeathEvent().execute(dungeon, source, target)

class RepeatEvent(Effect):
    def __init__(self, effect : Effect, amount : int):
        self.effect : Effect = effect
        self.amount : int = amount
    def get_desc(self):
        return utility.combine_text([["(x",str(self.amount),") "], self.effect.get_desc()], False)
    
    def execute(self, dungeon, source, target):
        for x in range(self.amount):
            copy.deepcopy(self.effect).execute(dungeon, source, target)
    def execute_with_statics(self, dungeon, source, target):
        self.dungeon = dungeon
        self.source = source
        self.target = target
        self.cancelled = False
        dungeon.apply_statics(self)
        if not self.cancelled:
            for x in range(self.amount):
                if dungeon.get_location_of_actor(target) != None:
                    copy.deepcopy(self.effect).execute_with_statics(dungeon, source, target)

class ProbabilityEvent(Effect):
    def __init__(self, effect : Effect, chance : float):
        self.effect : Effect = effect
        self.chance : int = chance
    def get_desc(self):
        percent : int = math.floor(self.chance * 100)
        return utility.combine_text([["(",str(percent),"%) "], self.effect.get_desc()], False)
    
    def execute(self, dungeon, source, target):
        if random.random() <= self.chance:
            copy.deepcopy(self.effect).execute(dungeon, source, target)
    def execute_with_statics(self, dungeon, source, target):
        self.dungeon = dungeon
        self.source = source
        self.target = target
        self.cancelled = False
        dungeon.apply_statics(self)
        if not self.cancelled:
            if random.random() <= self.chance:
                copy.deepcopy(self.effect).execute_with_statics(dungeon, source, target)

class HealEvent(Effect):
    def __init__(self, healing : int):
        self.healing : int = healing
    def get_desc(self):
        return ["Heal ",("healing",str(self.healing)), " HP"]
    def execute(self, dungeon, source, target):
        dungeon.add_to_message_queue_if_actor_visible(target, ["Healed ", ("healing",str(self.healing)), " HP."])
        new_hp = target.stathandler.get_stat("HP").heal(self.healing)

class DullWeaponEvent(Effect):
    def execute(self, dungeon, source, target):
        target.dull(random.random() * 0.1 + 0.9)

class SharpenEvent(Effect):
    def get_desc(self):
        percent : int = math.floor(self.sharpening * 100)
        return ["Sharpen an item ",("iron",str(percent) + "%")]
    def __init__(self, sharp : float):
        self.sharpening : float= sharp
    def execute(self, dungeon, source, target):
        target.sharpen(self.sharpening)

class SpendMPEvent(Effect):
    def __init__(self, spending : int):
        self.spending : int = spending
    def get_desc(self):
        return ["Spend ",str(self.spending), " MP"]
    def execute(self, dungeon, source, target):
        dungeon.add_to_message_queue_if_actor_visible(target, ["Spent ", str(self.spending), " MP."])
        target.stathandler.get_stat("MP").spend(self.spending)

class RestoreMPEvent(Effect):
    def __init__(self, healing : int):
        self.healing : int = healing
    def get_desc(self):
        return ["Restore ",str(self.healing), " MP"]
    def execute(self, dungeon, source, target):
        dungeon.add_to_message_queue_if_actor_visible(target, ["Restored ", str(self.healing), " MP."])
        target.stathandler.get_stat("MP").restore(self.healing)

class AttackEffect(Effect):
    def execute(self, dungeon, source, target) -> None:
        dungeon.add_to_message_queue_if_visible([
            source.get_name(), " attacked ", 
            target.get_name(), " with the ", 
            source.get_weapon().get_name(), "."])
        source.get_weapon().attack(dungeon, target)

class UseEffect(Effect):
    def execute(self, dungeon, source, target) -> None:
        dungeon.add_to_message_queue_if_visible([
            dungeon.actor.get_name(), " used the ", 
            source.get_name(), " on ", 
            target.get_name(), "."])
        source.use(dungeon, target)

class EffectSelector(Effect):
    def __init__(self, effect:Effect):
        self.effect : Effect = effect

class EffectSelectorTarget(EffectSelector):
    def execute(self, dungeon, source, target):
        self.effect.execute(dungeon, source, target)
    def execute_with_statics(self, dungeon, source, target):
        self.dungeon = dungeon
        self.source = source
        self.target = target
        self.cancelled = False
        dungeon.apply_statics(self)
        if not self.cancelled:
            self.effect.execute_with_statics(dungeon, source, target)
    def get_desc(self):
        return utility.combine_text(["Target:",utility.tab_text(self.effect.get_desc())])

class EffectSelectorSelf(EffectSelector):
    def execute(self, dungeon, source, target):
        self.effect.execute(dungeon, source, source)
    def execute_with_statics(self, dungeon, source, target):
        self.dungeon = dungeon
        self.source = source
        self.target = target
        self.cancelled = False
        dungeon.apply_statics(self)
        if not self.cancelled:
            self.effect.execute_with_statics(dungeon, source, source)
    def get_desc(self):
        return utility.combine_text(["User:",utility.tab_text(self.effect.get_desc())])

class EffectSelectorPredefinedTarget(EffectSelector):
    def __init__(self, effect, target):
        super().__init__(effect)
        self.target = target
    def execute(self, dungeon, source, target):
        self.effect.execute(dungeon, source, self.target)
    def execute_with_statics(self, dungeon, source, target):
        self.dungeon = dungeon
        self.source = source
        self.cancelled = False
        dungeon.apply_statics(self)
        if not self.cancelled:
            self.effect.execute_with_statics(dungeon, source, self.target)
    def get_desc(self):
        return [self.effect.get_desc(), " " ,self.target.get_name()]

class EffectSelectorPredefinedSource(EffectSelector):
    def __init__(self, effect, source):
        super().__init__(effect)
        self.source = source
    def execute(self, dungeon, source, target):
        self.effect.execute(dungeon, self.source, target)
    def execute_with_statics(self, dungeon, source, target):
        self.dungeon = dungeon
        self.target = target
        self.cancelled = False
        dungeon.apply_statics(self)
        if not self.cancelled:
            self.effect.execute_with_statics(dungeon, self.source, target)
    def get_desc(self):
        return [self.effect.get_desc(), " " ,self.source.get_name()]

class InteractionAction:
    def execute(self, dungeon):
        raise NotImplementedError("Subclasses must implement execute()")

    def get_name(self):
        raise NotImplementedError("Subclasses must implement get_name()")

    def get_description(self):
        return ""

class DummyAction(InteractionAction):
    def __init__(self, name : str | tuple["Hashable", str] | list[str | tuple["Hashable", str]]):
        self.name : str | tuple["Hashable", str] | list[str | tuple["Hashable", str]] = name
    def execute(self, dungeon):
        pass

    def get_name(self):
        return self.name

class PlayerInteractAction(InteractionAction):
    def __init__(self, interactable : "Interactable"):
        self.interactable : "Interactable" = interactable
        self.prev = None
    
    def execute(self, dungeon):
        dungeon.player_interact(self)

    def get_name(self):
        return self.interactable.get_name()

    def get_description(self):
        return self.interactable.get_description()

    def get_choices(self, dungeon) -> list[InteractionAction]:
        return self.interactable.get_choices(dungeon)


class PlayerEquippedInteractAction(PlayerInteractAction):
    def __init__(self, interactable : "Equipment", player_inv : bool):
        super().__init__(interactable)
        self.player_inv = player_inv
    
    def get_name(self):
        return [self.interactable.equipment_slot, ": ", self.interactable.get_name()]

    def get_choices(self, dungeon) -> list[InteractionAction]:
        actions = []
        if self.player_inv:
            if dungeon.actor.can_take_item(self.interactable):
                actions.append(UnequipItemAction(self.interactable))
        return actions

class PlayerBagInteractAction(PlayerInteractAction):
    def __init__(self, interactable : "Item"):
        super().__init__(interactable)
    
    def get_choices(self, dungeon) -> list[InteractionAction]:
        actions = []
        if hasattr(self.interactable, "equipment_slot") and dungeon.actor.can_equip(self.interactable):
            actions.append(EquipItemAction(self.interactable))
        if hasattr(self.interactable, "use") and self.interactable.can_use(dungeon) :
            actions.append(UseItemAction(self.interactable))
        actions.append(DiscardItemAction(self.interactable))
        return actions

class DialogueAction(InteractionAction):
    def __init__(self, manager , dialogue):
        self.manager = manager
        self.dialogue = dialogue
    
    def get_name(self):
        return self.dialogue.get_response_text()

    def execute(self, dungeon):
        self.manager.root_dialogue = self.dialogue
        dungeon.player_interact(PlayerInteractAction(self.manager))
        if self.dialogue.get_effect() != None:
            self.dialogue.get_effect().execute(dungeon, self.manager, self.dialogue)
    
class EnterPassageAction(InteractionAction):
    def __init__(self, passage):
        self.passage = passage

    def execute(self, dungeon):
        actor = dungeon.actor
        if not actor == dungeon.player:
            dungeon.add_to_message_queue_if_actor_visible(actor, [actor.get_name(), " entered the ", self.passage.get_name(), "."])
        source_room = dungeon.place
        target_room = dungeon.map[self.passage.destination_id]
        RemoveRoomObjEffect().execute(dungeon, source_room, actor)
        AddRoomObjEffect().execute(dungeon, target_room, actor)
        dungeon.update_location()
        if not actor == dungeon.player:
            dungeon.add_to_message_queue_if_actor_visible(actor, [actor.get_name(), " exited the ", self.passage.get_name(), "."])
        if actor == dungeon.player:
            dungeon.add_to_message_queue([actor.get_name(), " passes through the ", self.passage.get_name(), "."])
        dungeon.end_current_turn()
    def get_name(self):
        return "Enter"

class PlayerCampfireInteractAction(PlayerInteractAction):
    def __init__(self, interactable : "Campfire"):
        super().__init__(interactable)
    
    def get_name(self):
        return "Rest"

    def execute(self, dungeon):
        RestoreMPEvent(10).execute(dungeon,self.interactable,dungeon.actor)
        super().execute(dungeon)

    def get_choices(self, dungeon) -> list[InteractionAction]:
        actions = []
        for x in dungeon.actor.get_items_in_bag(lambda item : hasattr(item,"eat")):
            actions.append(EatAction(x))
        return actions

class TakeItemAction(InteractionAction):
    def __init__(self, item, source = None):
        self.item = item
        self.source = source
    
    def execute(self, dungeon) -> None:
        if not dungeon.actor.can_take_item(self.item):
            dungeon.end_current_turn()
            return
        if hasattr(self, "prev"):
            source = self.prev.interactable
        else:
            source = self.source
        RemoveRoomObjEffect().execute(dungeon, source, self.item)
        AddtoInventoryEvent().execute(dungeon, dungeon.actor, self.item)
        dungeon.add_to_message_queue_if_visible([dungeon.actor.get_name(), " picks up the ", self.item.get_name(), "."])
        dungeon.end_current_turn()
    
    def get_name(self):
        return "Take"

class UnequipItemAction(InteractionAction):
    def __init__(self, item : "Equipment"):
        self.item = item
    
    def execute(self, dungeon) -> None:
        if not dungeon.actor.can_take_item(self.item):
            return
        dungeon.actor.unequip_item(self.item)
        dungeon.add_to_message_queue_if_visible([dungeon.actor.get_name(), " unequipped the ", self.item.get_name(), "."])
        dungeon.end_current_turn()
    
    def get_name(self):
        return "Unequip"

class UseItemAction(PlayerInteractAction):
    def execute(self, dungeon):
        if len(self.interactable.get_targets(dungeon)) == 1:
            choices = self.interactable.get_targets(dungeon)
            UseAction(self.interactable, choices[0]).execute(dungeon)
        else:
            dungeon.player_interact(self)

    def get_choices(self, dungeon) -> list[InteractionAction]:
        actions = []
        targets = self.interactable.get_targets(dungeon)
        for x in targets:
            actions.append(UseAction(self.interactable, x))
        return actions

    def get_name(self):
        return "Use"

class EquipItemAction(InteractionAction):
    def __init__(self, item : "Equipment"):
        self.item = item
    
    def execute(self, dungeon) -> None:
        dungeon.actor.equip_item(self.item)
        dungeon.add_to_message_queue_if_visible([dungeon.actor.get_name(), " equipped the ", self.item.get_name(), "."])
        dungeon.end_current_turn()
    
    def get_name(self):
        return "Equip"

class DiscardItemAction(InteractionAction):
    def __init__(self, item : "Equipment"):
        self.item = item
    
    def execute(self, dungeon) -> None:
        dungeon.actor.remove_item(self.item)
        AddRoomObjEffect().execute(dungeon, dungeon.place, self.item)
        dungeon.add_to_message_queue_if_visible([dungeon.actor.get_name(), " discarded the ", self.item.get_name(), "."])
        dungeon.end_current_turn()
    
    def get_name(self):
        return "Discard"

class EatAction(InteractionAction):
    def __init__(self, food):
        self.food = food
    
    def execute(self, dungeon) -> None:
        dungeon.add_to_message_queue_if_visible([
            dungeon.actor.get_name(), " ate the ", 
            self.food.get_name(), "."])
        self.food.eat(dungeon, dungeon.actor)
        dungeon.actor.remove_item(self.food)
        dungeon.end_current_turn()
    
    def get_name(self):
        return ["Eat the ", self.food.get_name()]

class UseAction(InteractionAction):
    def __init__(self, item, target):
        self.item = item
        self.target = target
    
    def execute(self, dungeon) -> None:
        UseEffect().execute_with_statics(dungeon, self.item, self.target)
        dungeon.end_current_turn()
    
    def get_name(self):
        return self.target.get_name()

class AttackAction(InteractionAction):
    def __init__(self, entity):
        self.entity = entity
    
    def execute(self, dungeon) -> None:
        AttackEffect().execute_with_statics(dungeon, dungeon.actor, self.entity)
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

