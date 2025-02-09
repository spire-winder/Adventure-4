
import sys

class InteractionAction:
    def execute(self, game_handler):
        raise NotImplementedError("Subclasses must implement execute()")

class PlayerInputAction(InteractionAction):
    def execute(self, game_handler, actor):
        game_handler.room_center()
        
class EnterPassageAction(InteractionAction):
    def __init__(self, passage):
        self.passage = passage

    def execute(self, game_handler, actor):
        game_handler.place.remove_roomobject(actor)
        game_handler.init_location(self.passage.destination_id)
        game_handler.place.add_roomobject(actor)
        game_handler.add_to_message_queue([actor.name, " entered the ", self.passage.name, "."])
        game_handler.end_current_turn()

class TakeItemAction(InteractionAction):
    def __init__(self, item):
        self.item = item
    
    def execute(self, game_handler, actor) -> None:
        if not game_handler.place.remove_roomobject(self.item):
            sys.exit('Object not found in room!')
        game_handler.add_to_message_queue([actor.name, " picked up the ", self.item.name, "."])
        game_handler.end_current_turn()