import random
import classes.actions
import utility

class State:
    def register(self, state_entity):
        self.state_entity = state_entity
        self.state_entity.notif.subscribe(self.state_entity_event)
    def unregister(self, state_entity):
        self.state_entity.notif.unsubscribe(self.state_entity_event)
    def state_entity_event(self, dungeon, notif ):
        pass
    def decide(self, dungeon):
        raise NotImplementedError("Subclasses must implement decide()")

class PeacefulState(State):
    def state_entity_event(self, dungeon, notif ):
        if hasattr(notif.effect, "damage"):
            dungeon.add_to_message_queue_if_actor_visible(self.state_entity, [self.state_entity.get_name(), " moves to attack."])
            self.state_entity.change_state(AttackingState(), dungeon, False)

    def decide(self, dungeon):
        pass

class IdleState(State):
    def decide(self, dungeon ):
        current_room = dungeon.get_location_of_actor(self.state_entity)
        if dungeon.player in current_room.room_contents:
            dungeon.add_to_message_queue_if_actor_visible(self.state_entity, [self.state_entity.get_name(), " notices ", dungeon.player.get_name(), "."])
            self.state_entity.change_state(AttackingState(), dungeon)

class AttackingState(State):
    def find_weapon(self, dungeon) -> bool:
        current_room = dungeon.get_location_of_actor(self.state_entity)
        weapons = current_room.get_roomobjects(lambda item : hasattr(item, "attackeffect"))
        if weapons != []:
            weapon = random.choice(weapons)
            classes.actions.TakeItemEffect(current_room, self.state_entity, weapon).execute_with_statics(dungeon)
    
    def decide(self, dungeon ):
        current_room = dungeon.get_location_of_actor(self.state_entity)
        if dungeon.player in current_room.room_contents:
            if not self.state_entity.has_weapon():
                self.find_weapon(dungeon)
            else:
                classes.actions.UseEffect(self.state_entity, dungeon.player, self.state_entity.get_weapon(), "attacks").execute_with_statics(dungeon)
        else:
            self.state_entity.change_state(WanderState(3), dungeon, True)

class WanderState(State):
    def __init__(self,time : int):
        self.time : int = time

    def decide(self, dungeon ):
        current_room = dungeon.get_location_of_actor(self.state_entity)
        if dungeon.player in current_room.room_contents:
            self.state_entity.change_state(AttackingState(), dungeon)
        else:
            if self.time > 0:
                self.time -= 1
                passages = current_room.get_roomobjects(lambda item : hasattr(item, "destination_id"))
                if len(passages) >= 1:
                    passage = random.choice(passages)
                    classes.actions.EnterPassageEffect(self.state_entity, passage).execute_with_statics(dungeon)
                else:
                    self.state_entity.change_to_default_state()
            else:
                self.state_entity.change_to_default_state()