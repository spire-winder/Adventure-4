import random
import classes.actions

class State:
    def decide(self, dungeon, actor):
        raise NotImplementedError("Subclasses must implement decide()")

class IdleState(State):
    def decide(self, dungeon, actor ):
        current_room = dungeon.get_location_of_actor(actor)
        if dungeon.player in current_room.room_contents:
            dungeon.add_to_message_queue_if_actor_visible(actor, [actor.get_name(), " notices ", dungeon.player.get_name(), "."])
            actor.state = AttackingState()
            actor.state.decide(dungeon, actor)
        actor.event.emit(action=None)

class AttackingState(State):
    def find_weapon(self, dungeon, actor) -> bool:
        current_room = dungeon.get_location_of_actor(actor)
        weapons = current_room.get_roomobjects(lambda item : hasattr(item, "attack"))
        if weapons != []:
            weapon = random.choice(weapons)
            actor.event.emit(action=classes.actions.TakeItemAction(weapon))
            return True
        return False
    
    def decide(self, dungeon, actor ):
        current_room = dungeon.get_location_of_actor(actor)
        if dungeon.player in current_room.room_contents:
            if not actor.has_weapon():
                if self.find_weapon(dungeon, actor):
                    return
            actor.event.emit(action=classes.actions.AttackAction(dungeon.player))
        else:
            actor.state = WanderState(3)
            actor.state.decide(dungeon, actor)

class WanderState(State):
    def __init__(self, time : int):
        self.time : int = time

    def decide(self, dungeon, actor ):
        current_room = dungeon.get_location_of_actor(actor)
        if dungeon.player in current_room.room_contents:
            actor.state = AttackingState()
            actor.state.decide(dungeon, actor)
        else:
            if self.time > 0:
                self.time -= 1
                passages = current_room.get_roomobjects(lambda item : hasattr(item, "destination_id"))
                passage = random.choice(passages)
                actor.event.emit(action=classes.actions.EnterPassageAction(passage))
            else:
                actor.state = IdleState()
                actor.state.decide(dungeon, actor)