from collections.abc import Callable, Hashable, MutableSequence
from classes.actions import *
import utility

class Ability:
    def __init__(self, id : str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]] = None, desc : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]] = None):
        self.id = id
        self.name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]= name
        self.desc : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]] = desc
    def get_name(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return self.name
    def get_desc(self):
        return self.desc
    def get_full(self):
        return utility.combine_text([self.get_name(), utility.tab_text(self.get_desc())])
    def apply(self, owner, effect : Effect):
        pass
    def end_of_round(self, dungeon, owner):
        pass
    def is_id(self, the_id : str) -> bool:
        return the_id == self.id
    def __gt__(self, a : "Ability") -> bool:
        return False

class Status(Ability):
    def get_name(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return self.ability.get_name()
    def get_desc(self):
        status_color : str
        duration_percent : float = self.current_duration / self.duration
        if duration_percent >= 0.666:
            status_color = "status_full"
        elif duration_percent >= 0.333:
            status_color = "status_depleted"
        else:
            status_color = "status_empty"
        return utility.combine_text([self.ability.get_desc(), ["(", (status_color, str(self.current_duration)), " rounds remaining)"]])
    def apply(self, owner, effect : Effect):
        self.ability.apply(owner, effect)
    def __init__(self, ability : Ability, duration : int):
        super().__init__(ability.id)
        self.ability = ability
        self.duration : int = duration
        self.current_duration : int = duration
    def end_of_round(self, dungeon, owner):
        self.ability.end_of_round(dungeon, owner)
        self.current_duration -= 1
        if self.current_duration <= 0:
            EndStatusEffect().execute_with_statics(dungeon, owner, self)
    def is_id(self, the_id : str) -> bool:
        return the_id == self.ability.id
    def __gt__(self, a : "Status") -> bool:
        return self.current_duration > a.current_duration

class Sharpness(Ability):
    def get_desc(self):
        percent : int = math.floor(self.sharpness * 100)
        return [str(percent),"%"]
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], sharpness : float = 1):
        super().__init__(id,name)
        self.sharpness = sharpness
    def apply(self, owner, effect : Effect):
        if owner.has_weapon():
            if hasattr(effect, "damage") and effect.source == owner.get_weapon():
                effect.damage *= self.sharpness
                effect.damage = math.ceil(effect.damage)
    def dull(self, amount : float):
        self.sharpness *= amount

class ManaCost(Ability):
    def get_desc(self):
        return [("magic",str(self.mpcost))," MP"]
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], mpcost : float = 1):
        super().__init__(id,name)
        self.mpcost = mpcost
    def apply(self, owner, effect : Effect):
        if isinstance(effect, AttackEffect) and effect.source == owner:
            if not owner.stathandler.get_stat("MP").spend(self.mpcost):
                effect.dungeon.add_to_message_queue_if_actor_visible(owner, [owner.get_name(), "'s mana ran out!"])
                effect.cancel()

class Armor(Ability):
    def get_desc(self):
        return ("iron", "+" + str(self.armor_value) + " Armor")
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], armor_value : int = 1):
        super().__init__(id,name)
        self.armor_value = armor_value
    def apply(self, owner, effect : Effect):
        if hasattr(effect, "damage") and effect.target == owner:
            current_armor = self.armor_value
            if effect.armor_penetrate > 0:
                current_armor -= effect.armor_penetrate
                if current_armor < 0:
                    current_armor = 0
                effect.armor_penetrate -= self.armor_value
                if effect.armor_penetrate < 0:
                    effect.armor_penetrate = 0
            effect.damage -= current_armor

class Stunned(Ability):
    def get_desc(self):
        return [["Deal ",   "-", str(self.damage_mod), " damage with ",self.tag.get_name()," attacks."],"\n", ["Recieve +", str(self.damage_mod), " damage from ",self.tag.get_name()," attacks."]]
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], tag_id : Ability, damage_mod : int = 1):
        super().__init__(id,name)
        self.tag = tag_id
        self.damage_mod = damage_mod
    def apply(self, owner, effect : Effect):
        if hasattr(effect, "damage") and effect.target == owner and effect.source.has_ability(self.tag.id):
            effect.damage += self.damage_mod
        if hasattr(effect, "damage") and effect.dungeon.actor == owner and effect.source.has_ability(self.tag.id):
            effect.damage -= self.damage_mod

class BattleCry(Ability):
    def get_desc(self):
        return utility.combine_text([self.tag.get_name(), " enemies deal ", ("damage","+" + str(self.strength) + " damage"),"."], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], tag_id : Ability, strength : int):
        super().__init__(id,name)
        self.tag = tag_id
        self.strength = strength
    def apply(self, owner, effect : Effect):
        if hasattr(effect, "damage") and effect.dungeon.actor.has_ability(self.tag.id):
            effect.damage += self.strength

class DamageTypeBuff(Ability):
    def get_desc(self):
        return utility.combine_text(["Deal ", ("damage","+" + str(self.strength) + " damage")," with ",(self.damage_type, self.damage_type)," attacks."], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], damage_type : str, strength : int):
        super().__init__(id,name)
        self.damage_type = damage_type
        self.strength = strength
    def apply(self, owner, effect : Effect):
        if hasattr(effect, "damage") and effect.dungeon.actor == owner and effect.damage_type == self.damage_type:
            effect.damage += self.strength

class SelectiveBuff(Ability):
    def get_desc(self):
        return utility.combine_text(["Deal ", ("damage","+" + str(self.strength) + " damage")," with ",self.tag.get_name()," attacks."], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], tag_id : Ability, strength : int):
        super().__init__(id,name)
        self.tag = tag_id
        self.strength = strength
    def apply(self, owner, effect : Effect):
        if hasattr(effect, "damage") and effect.dungeon.actor == owner and effect.source.has_ability(self.tag.id):
            effect.damage += self.strength