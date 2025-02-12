
import sys
import typing
if typing.TYPE_CHECKING:
    from classes.interactable import Interactable
    from classes.interactable import Item

class InteractionAction:
    def execute(self, dungeon):
        raise NotImplementedError("Subclasses must implement execute()")

    def get_name(self):
        raise NotImplementedError("Subclasses must implement get_name()")

class PlayerInteractAction(InteractionAction):
    def __init__(self, interactable : "Interactable"):
        self.interactable : "Interactable" = interactable
        self.prev = None
    
    def execute(self, dungeon):
        dungeon.player_interact(self)

    def get_name(self):
        return self.interactable.get_name()

class EnterPassageAction(InteractionAction):
    def __init__(self, passage):
        self.passage = passage

    def execute(self, dungeon):
        dungeon.place.remove_roomobject(dungeon.actor)
        dungeon.init_location(self.passage.destination_id)
        dungeon.place.add_roomobject(dungeon.actor)
        dungeon.add_to_message_queue([dungeon.actor.get_name(), " entered the ", self.passage.get_name(), "."])
        dungeon.end_current_turn()
    def get_name(self):
        return "Enter"

class TakeItemAction(InteractionAction):
    def __init__(self, item):
        self.item = item
    
    def execute(self, dungeon) -> None:
        if not dungeon.actor.can_take_item(self.item):
            return
        if not dungeon.place.remove_roomobject(self.item):
            sys.exit('Object not found in room!')
        dungeon.actor.take_item(self.item)
        self.item.is_in_inventory = True
        dungeon.add_to_message_queue([dungeon.actor.get_name(), " picked up the ", self.item.get_name(), "."])
        dungeon.end_current_turn()
    
    def get_name(self):
        return "Take"

class AttackAction(InteractionAction):
    def __init__(self, entity):
        self.entity = entity
    
    def execute(self, dungeon) -> None:
        dungeon.add_to_message_queue([dungeon.actor.get_name(), " attacked ", self.entity.get_name(), " with the ", dungeon.actor.get_weapon().get_name()])
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