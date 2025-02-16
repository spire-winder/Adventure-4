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
    def apply(self, chain : list, effect : Effect):
        pass
    def end_of_round(self, chain):
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
    def apply(self, chain : list, effect : Effect):
        self.ability.apply(chain, effect)
    def __init__(self, ability : Ability, duration : int):
        super().__init__(ability.id)
        self.ability = ability
        self.duration : int = duration
        self.current_duration : int = duration
    def end_of_round(self, chain):
        self.ability.end_of_round(chain)
        self.current_duration -= 1
        if self.current_duration <= 0:
            EndStatusEffect().execute_with_statics(chain[0], chain[2], self)
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
        self.sharpness : float = sharpness
    def apply(self, chain : list, effect : Effect):
        if hasattr(effect, "damage") and len(chain)>=6 and effect.source == chain[5]:
            effect.damage *= self.sharpness
            effect.damage = math.ceil(effect.damage)
    def dull(self, amount : float):
        self.sharpness *= amount
    def sharpen(self, amount : float):
        self.sharpness += amount
        if self.sharpness > 1.0:
            self.sharpness : float = 1.0

class ManaCost(Ability):
    def get_desc(self):
        return [("magic",str(self.mpcost))," MP"]
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], mpcost : float = 1):
        super().__init__(id,name)
        self.mpcost = mpcost
    def apply(self, chain : list, effect : Effect):
        if ((isinstance(effect, AttackEffect) and effect.source.get_weapon() == chain[5]) or
            effect.source == chain[5] and isinstance(effect, UseEffect)):
            if not chain[2].stathandler.get_stat("MP").spend(self.mpcost):
                effect.dungeon.add_to_message_queue_if_actor_visible(chain[2], [chain[2].get_name(), "'s mana ran out!"])
                effect.cancel()

class SingleUse(Ability):
    def __init__(self):
        super().__init__("singleuse","Single Use",None)
    def apply(self, chain : list, effect : Effect):
        if len(chain) >= 6 and ((isinstance(effect, AttackEffect) and effect.source.get_weapon() == chain[5]) or
            effect.source == chain[5] and isinstance(effect, UseEffect)):
            chain[3].bag.remove_item(chain[5])

class MultiUse(Ability):
    def get_desc(self):
        return ["Can only be used ", str(self.uses), " more times"]
    def __init__(self, uses : int):
        super().__init__("multiuse","Multi Use")
        self.uses = uses
    def apply(self, chain : list, effect : Effect):
        if ((isinstance(effect, AttackEffect) and effect.source.get_weapon() == chain[5]) or
            effect.source == chain[5] and isinstance(effect, UseEffect)):
            self.uses -= 1
            if self.uses <= 0:
                chain[3].bag.remove_item(chain[5])

class Armor(Ability):
    def get_desc(self):
        return [("iron", "+" + str(self.armor_value) + " Armor")]
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], armor_value : int = 1):
        super().__init__(id,name)
        self.armor_value = armor_value
    def apply(self, chain : list, effect : Effect):
        if hasattr(effect, "damage") and effect.target == chain[2]:
            current_armor = self.armor_value
            if effect.armor_penetrate == -1:
                return
            if effect.armor_penetrate > 0:
                current_armor -= effect.armor_penetrate
                if current_armor < 0:
                    current_armor = 0
                effect.armor_penetrate -= self.armor_value
                if effect.armor_penetrate < 0:
                    effect.armor_penetrate = 0
            effect.damage -= current_armor

class SelectiveArmor(Ability):
    def get_desc(self):
        return utility.combine_text([("iron","+" + str(self.armor_value) + " Armor")," against ",(self.damage_type, self.damage_type)," attacks."], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], damage_type : str, armor_value : int):
        super().__init__(id,name)
        self.damage_type = damage_type
        self.armor_value = armor_value
    def apply(self, chain : list, effect : Effect):
        if hasattr(effect, "damage") and effect.target == chain[2] and effect.damage_type == self.damage_type:
            current_armor = self.armor_value
            if effect.armor_penetrate == -1:
                return
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
    def apply(self, chain : list, effect : Effect):
        if hasattr(effect, "damage") and effect.target == chain[2] and effect.source.has_ability(self.tag.id):
            effect.damage += self.damage_mod
        if hasattr(effect, "damage") and effect.dungeon.actor == chain[2] and effect.source.has_ability(self.tag.id):
            effect.damage -= self.damage_mod

class BattleCry(Ability):
    def get_desc(self):
        return utility.combine_text([self.tag.get_name(), " enemies deal ", ("damage","+" + str(self.strength) + " damage"),"."], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], tag_id : Ability, strength : int):
        super().__init__(id,name)
        self.tag = tag_id
        self.strength = strength
    def apply(self, chain : list, effect : Effect):
        utility.log(effect.dungeon.actor.has_ability(self.tag.id))
        if hasattr(effect, "damage") and effect.dungeon.actor.has_ability(self.tag.id):
            effect.damage += self.strength

class DamageTypeBuff(Ability):
    def get_desc(self):
        return utility.combine_text(["Deal ", ("damage","+" + str(self.strength) + " damage")," with ",(self.damage_type, self.damage_type)," attacks."], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], damage_type : str, strength : int):
        super().__init__(id,name)
        self.damage_type = damage_type
        self.strength = strength
    def apply(self, chain : list, effect : Effect):
        if hasattr(effect, "damage") and effect.dungeon.actor == chain[2] and effect.damage_type == self.damage_type:
            effect.damage += self.strength

class SelectiveBuff(Ability):
    def get_desc(self):
        return utility.combine_text(["Deal ", ("damage","+" + str(self.strength) + " damage")," with ",self.tag.get_name()," attacks."], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], tag_id : Ability, strength : int):
        super().__init__(id,name)
        self.tag = tag_id
        self.strength = strength
    def apply(self, chain : list, effect : Effect):
        if hasattr(effect, "damage") and effect.dungeon.actor == chain[2] and effect.source.has_ability(self.tag.id):
            effect.damage += self.strength

class EndOfTurnEffect(Ability):
    def get_desc(self):
        return utility.combine_text([self.effect.get_desc(), " each round."], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], effect : Effect):
        super().__init__(id,name)
        self.effect = effect
    def end_of_round(self, chain):
        copy.deepcopy(self.effect).execute_with_statics(chain[0], self, chain[2])

class ImmuneToAbility(Ability):
    def get_desc(self):
        return utility.combine_text(["Immune to ", self.abil.get_name()], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], abil : Ability):
        super().__init__(id,name)
        self.abil = abil
    def apply(self, chain : list, effect : Effect):
        if isinstance(effect, AddAbilityEffect) and effect.target == chain[2] and effect.source.is_id(self.abil.id):
            effect.dungeon.add_to_message_queue_if_actor_visible(chain[2], [chain[2].get_name(), " is immune to ", effect.source.get_name(), "!"])
            effect.cancel()