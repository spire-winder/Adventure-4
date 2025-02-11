
import sys
import typing
if typing.TYPE_CHECKING:
    from classes.interactable import Interactable

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
        return self.interactable.name
        
class EnterPassageAction(InteractionAction):
    def __init__(self, passage):
        self.passage = passage

    def execute(self, dungeon):
        dungeon.place.remove_roomobject(dungeon.actor)
        dungeon.init_location(self.passage.destination_id)
        dungeon.place.add_roomobject(dungeon.actor)
        dungeon.add_to_message_queue([dungeon.actor.name, " entered the ", self.passage.name, "."])
        dungeon.end_current_turn()
    def get_name(self):
        return "Enter"

class TakeItemAction(InteractionAction):
    def __init__(self, item):
        self.item = item
    
    def execute(self, dungeon) -> None:
        if not dungeon.place.remove_roomobject(self.item):
            sys.exit('Object not found in room!')
        dungeon.add_to_message_queue([dungeon.actor.name, " picked up the ", self.item.name, "."])
        dungeon.end_current_turn()
    
    def get_name(self):
        return "Take"

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