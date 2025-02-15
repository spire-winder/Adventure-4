
import sys
import typing
import utility
import copy
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
        dungeon.apply_statics(self)
        self.execute(self.dungeon, self.source, self.target)
    def execute(self, dungeon, source, target):
        raise NotImplementedError("Subclasses must implement execute()")
    def get_desc(self):
        return ""

class RemoveRoomObjEffect(Effect):
    def execute(self, dungeon, source, target):
        source.remove_roomobject(target)

class AddRoomObjEffect(Effect):
    def execute(self, dungeon, source, target):
        source.add_roomobject(target)

class EndStatusEffect(Effect):
    def execute(self, dungeon, source, target):
        dungeon.add_to_message_queue_if_actor_visible(source, [source.get_name(), "'s ", target.get_name(), " expired."])
        RemoveAbilityEffect().execute(dungeon, source, target)

class RemoveAbilityEffect(Effect):
    def execute(self, dungeon, source, target):
        source.remove_ability(target)

class AddAbilityEffect(Effect):
    def get_desc(self):
        return "Apply"
    def execute(self, dungeon, source, target):
        dungeon.add_to_message_queue_if_actor_visible(source, [source.get_name(), " gained ", target.get_name(), "."])
        source.add_ability(target)

class EffectSequence(Effect):
    def __init__(self, effects : list[Effect]):
        self.effects : list[Effect] = effects
    
    def get_desc(self):
        effect_text = []
        for x in self.effects:
            effect_text.append(x.get_desc())
        return utility.combine_text(effect_text)
    
    def execute(self, dungeon, source, target):
        for x in self.effects:
            x.execute(dungeon, source, target)

class AddtoInventoryEvent(Effect):
    def get_desc(self):
        return "Adds to inventory"
    
    def execute(self, dungeon, source, target):
        source.take_item(target)

class DeathEvent(Effect):
    def get_desc(self):
        return "Dies"
    
    def execute(self, dungeon, source, target):
        death_room = dungeon.get_location_of_actor(target)
        if death_room != None:
            dungeon.add_to_message_queue_if_actor_visible(source, [target.get_name(), " dies."])
            RemoveRoomObjEffect().execute(dungeon, death_room, target)
            if target == dungeon.player:
                dungeon.game_over = True

class DamageEvent(Effect):
    def __init__(self, damage : int):
        self.damage : int = damage
    def get_desc(self):
        return "Deal " + str(self.damage) + " damage"
    
    def execute(self, dungeon, source, target):
        if self.damage < 1:
            self.damage = 1
        dungeon.add_to_message_queue_if_actor_visible(source,["Dealt ", str(self.damage), " damage."])
        new_hp = target.stathandler.get_stat("HP").damage(self.damage)
        if new_hp <= 0:
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
        dungeon.apply_statics(self)
        for x in range(self.amount):
            if dungeon.get_location_of_actor(target) != None:
                copy.deepcopy(self.effect).execute_with_statics(dungeon, source, target)

class HealEvent(Effect):
    def __init__(self, healing : int):
        self.healing : int = healing
    def get_desc(self):
        return "Heal " + str(self.healing) + " damage"
    def execute(self, dungeon, source, target):
        dungeon.add_to_message_queue_if_actor_visible(target, ["Healed ", str(self.healing), " damage."])
        new_hp = target.stathandler.get_stat("HP").heal(self.healing)

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
        dungeon.apply_statics(self)
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
        dungeon.apply_statics(self)
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
        self.target = target
        dungeon.apply_statics(self)
        self.effect.execute_with_statics(dungeon, source, self.target)
    def get_desc(self):
        return self.effect.get_desc() + " " + self.target.get_name()

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
    def __init__(self, interactable : "Equipment"):
        super().__init__(interactable)
    
    def get_name(self):
        return [self.interactable.equipment_slot, ": ", self.interactable.get_name()]

    def get_choices(self, dungeon) -> list[InteractionAction]:
        actions = []
        if dungeon.actor.can_take_item(self.interactable):
            actions.append(UnequipItemAction(self.interactable))
        return actions

class PlayerInventoryInteractAction(PlayerInteractAction):
    def __init__(self, interactable : "Item"):
        super().__init__(interactable)
    
    def get_name(self):
        return self.interactable.get_name()

    def get_choices(self, dungeon) -> list[InteractionAction]:
        actions = []
        if hasattr(self.interactable, "equipment_slot") and dungeon.actor.can_equip(self.interactable):
            actions.append(EquipItemAction(self.interactable))
        return actions

class EnterPassageAction(InteractionAction):
    def __init__(self, passage):
        self.passage = passage

    def execute(self, dungeon):
        if not dungeon.actor == dungeon.player:
            dungeon.add_to_message_queue_if_actor_visible(dungeon.actor, [dungeon.actor.get_name(), " entered the ", self.passage.get_name(), "."])
        source_room = dungeon.place
        target_room = dungeon.map[self.passage.destination_id]
        RemoveRoomObjEffect().execute(dungeon, source_room, dungeon.actor)
        AddRoomObjEffect().execute(dungeon, target_room, dungeon.actor)
        dungeon.update_location()
        if not dungeon.actor == dungeon.player:
            dungeon.add_to_message_queue_if_actor_visible(dungeon.actor, [dungeon.actor.get_name(), " exited the ", self.passage.get_name(), "."])
        if dungeon.actor == dungeon.player:
            dungeon.add_to_message_queue([dungeon.actor.get_name(), " passes through the ", self.passage.get_name(), "."])
        dungeon.end_current_turn()
    def get_name(self):
        return "Enter"

class PlayerCampfireInteractAction(PlayerInteractAction):
    def __init__(self, interactable : "Campfire"):
        super().__init__(interactable)
    
    def get_name(self):
        return "Rest"

    def get_choices(self, dungeon) -> list[InteractionAction]:
        actions = []
        for x in dungeon.actor.get_items_in_bag(lambda item : hasattr(item,"eat")):
            actions.append(EatAction(x))
        return actions

class TakeItemAction(InteractionAction):
    def __init__(self, item):
        self.item = item
    
    def execute(self, dungeon) -> None:
        if not dungeon.actor.can_take_item(self.item):
            return
        RemoveRoomObjEffect().execute(dungeon, dungeon.place, self.item)
        AddtoInventoryEvent().execute(dungeon, dungeon.actor, self.item)
        dungeon.add_to_message_queue_if_visible([dungeon.actor.get_name(), " picked up the ", self.item.get_name(), "."])
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

class EquipItemAction(InteractionAction):
    def __init__(self, item : "Equipment"):
        self.item = item
    
    def execute(self, dungeon) -> None:
        dungeon.actor.equip_item(self.item)
        dungeon.add_to_message_queue_if_visible([dungeon.actor.get_name(), " equipped the ", self.item.get_name(), "."])
        dungeon.end_current_turn()
    
    def get_name(self):
        return "Equip"

class EatAction(InteractionAction):
    def __init__(self, food):
        self.food = food
    
    def execute(self, dungeon) -> None:
        dungeon.add_to_message_queue_if_visible([
            dungeon.actor.get_name(), " ate the ", 
            self.food.get_name(), "."])
        self.food.eat(dungeon, dungeon.actor)
        dungeon.end_current_turn()
    
    def get_name(self):
        return ["Eat the ", self.food.get_name()]

class AttackAction(InteractionAction):
    def __init__(self, entity):
        self.entity = entity
    
    def execute(self, dungeon) -> None:
        dungeon.add_to_message_queue_if_visible([
            dungeon.actor.get_name(), " attacked ", 
            self.entity.get_name(), " with the ", 
            dungeon.actor.get_weapon().get_name(), "."])
        dungeon.actor.get_weapon().attack(dungeon, self.entity)
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

