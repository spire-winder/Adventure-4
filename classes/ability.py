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
    def reply(self, chain : list, effect : Effect):
        pass
    def apply_from_bag(self, chain : list, effect : Effect):
        pass
    def end_of_round(self, chain):
        pass
    def is_id(self, the_id : str) -> bool:
        return the_id == self.id
    def __gt__(self, a : "Ability") -> bool:
        return False
    def reformat_dict(self, chain) -> dict:
        return {
            "abilityhandler":chain[-1], 
            "item":chain[-2], 
            "bag":chain[-3], 
            "equipmenthandler":chain[-3], 
            "inventory":chain[3], 
            "user":chain[2], 
            "room":chain[1],
            "dungeon":chain[0],
            "self":self,
        }

class HiddenAbility(Ability):
    def get_name(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return None
    def get_desc(self):
        return None
    def apply_from_bag(self, chain : list, effect : Effect):
        self.ability.apply_from_bag(chain, effect)
    def apply(self, chain : list, effect : Effect):
        self.ability.apply(chain, effect)
    def __init__(self, ability : Ability):
        super().__init__(ability.id)
        self.ability = ability
    def end_of_round(self, chain):
        self.ability.end_of_round(chain)
    def is_id(self, the_id : str) -> bool:
        return the_id == self.ability.id

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
    def apply_from_bag(self, chain : list, effect : Effect):
        self.ability.apply_from_bag(chain, effect)
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
            EndStatusEffect(chain[2], self).execute_with_statics(chain[0])
    def is_id(self, the_id : str) -> bool:
        return the_id == self.ability.id
    def __gt__(self, a : "Status") -> bool:
        return self.current_duration > a.current_duration

class Sharpness(Ability):
    def get_desc(self):
        percent : int = math.floor(self.sharpness * 100)
        return [str(percent),"%"]
    def __init__(self, sharpness : float = 1.0, durability : float = 0.9):
        super().__init__("sharpness","Sharpness")
        self.sharpness : float = sharpness
        self.durability : float = durability
    def apply(self, chain : list, effect : Effect):
        if hasattr(effect, "damage") and effect.source == chain[-2]:
            effect.damage *= self.sharpness
            effect.damage = math.ceil(effect.damage)
        if isinstance(effect, UseEffect) and effect.item == chain[-2]:
            self.dull(random.random() * (1 - self.durability) + self.durability)
            if self.sharpness <= 0.05:
                chain[0].add_to_message_queue_if_actor_visible(chain[2], [chain[-2].get_name(), " broke!"])
                chain[3].bag.remove_item(chain[-2])
    def apply_from_bag(self, chain, effect):
        return self.apply(chain, effect)
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
        if isinstance(effect, UseEffect) and effect.item == chain[-2]:
            if not chain[2].has_stat("MP"):
                chain[0].add_to_message_queue_if_actor_visible(chain[2], [chain[2].get_name(), " can't use mana!"])
                effect.cancel()
            elif not chain[2].get_stat("MP").spend(self.mpcost):
                chain[0].add_to_message_queue_if_actor_visible(chain[2], [chain[2].get_name(), "'s mana ran out!"])
                effect.cancel()
    def apply_from_bag(self, chain, effect):
        return self.apply(chain, effect)

class SingleUse(Ability):
    def __init__(self):
        super().__init__("singleuse","Single Use",None)
    def apply(self, chain : list, effect : Effect):
        if isinstance(effect, UseEffect) and effect.item == chain[-2]:
            if hasattr(chain[3], "bag"):
                chain[3].bag.remove_item(chain[-2])
            elif effect.item == chain[2]:
                chain[1].remove_roomobject(chain[2])
    def apply_from_bag(self, chain, effect):
        return self.apply(chain, effect)

class MultiUse(Ability):
    def get_desc(self):
        if self.uses == 1:
            return ["Can only be used ", str(self.uses), " more time"]
        else:
            return ["Can only be used ", str(self.uses), " more times"]
    def __init__(self, uses : int):
        super().__init__("multiuse","Limited Uses")
        self.uses = uses
    def apply(self, chain : list, effect : Effect):
        if isinstance(effect, UseEffect) and effect.item == chain[-2]:
            self.uses -= 1
            if self.uses <= 0:
                chain[0].add_to_message_queue_if_actor_visible(chain[2], [chain[-2].get_name(), " broke!"])
                chain[3].bag.remove_item(chain[-2])
    def apply_from_bag(self, chain, effect):
        return self.apply(chain, effect)

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

class Reciprocate(Ability):
    def get_desc(self):
        return utility.combine_text(["When attacked, ", self.reciprocate_effect.get_desc()],False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], reciprocate_effect : Effect = None):
        super().__init__(id,name)
        self.reciprocate_effect = reciprocate_effect or Effect()
    def reply(self, chain : list, effect : Effect):
        if isinstance(effect, UseEffect) and effect.target == chain[2]:
            new_effect : Effect = copy.deepcopy(self.reciprocate_effect)
            new_dict = self.reformat_dict(chain).copy()
            new_dict["attacker"] = effect.source
            new_effect.execute_with_statics_and_reformat(chain[0], new_dict, True)

class SelectiveArmor(Ability):
    def get_desc(self):
        return utility.combine_text([("iron","+" + str(self.armor_value) + " Armor")," against ",(self.damage_type, self.damage_type)," attacks"], False)
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
        return [["Deal ",   "-", str(self.damage_mod), " damage with ",self.tag.get_name()," attacks"],"\n", ["Recieve +", str(self.damage_mod), " damage from ",self.tag.get_name()," attacks"]]
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], tag_id : Ability, damage_mod : int = 1):
        super().__init__(id,name)
        self.tag = tag_id
        self.damage_mod = damage_mod
    def apply(self, chain : list, effect : Effect):
        if hasattr(effect, "damage") and effect.target == chain[2] and effect.source.has_ability(self.tag.id):
            effect.damage += self.damage_mod
        if hasattr(effect, "damage") and chain[0].actor == chain[2] and effect.source.has_ability(self.tag.id):
            effect.damage -= self.damage_mod

class BattleCry(Ability):
    def get_desc(self):
        return utility.combine_text([self.tag.get_name(), " enemies deal ", ("damage","+" + str(self.strength) + " damage")], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], tag_id : Ability, strength : int):
        super().__init__(id,name)
        self.tag = tag_id
        self.strength = strength
    def apply(self, chain : list, effect : Effect):
        if hasattr(effect, "damage") and chain[0].actor.has_ability(self.tag.id):
            effect.damage += self.strength

class DamageTypeBuff(Ability):
    def get_desc(self):
        return utility.combine_text(["Deal ", ("damage","+" + str(self.strength) + " damage")," with ",(self.damage_type, self.damage_type)," attacks"], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], damage_type : str, strength : int):
        super().__init__(id,name)
        self.damage_type = damage_type
        self.strength = strength
    def apply(self, chain : list, effect : Effect):
        if hasattr(effect, "damage") and chain[0].actor == chain[2] and effect.damage_type == self.damage_type:
            effect.damage += self.strength

class SelectiveBuff(Ability):
    def get_desc(self):
        return utility.combine_text(["Deal ", ("damage","+" + str(self.strength) + " damage")," with ",self.tag.get_name()," attacks"], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], tag_id : Ability, strength : int):
        super().__init__(id,name)
        self.tag = tag_id
        self.strength = strength
    def apply(self, chain : list, effect : Effect):
        if hasattr(effect, "damage") and chain[0].actor == chain[2] and effect.source.has_ability(self.tag.id):
            effect.damage += self.strength

class EndOfTurnEffect(Ability):
    def get_desc(self):
        return utility.combine_text([self.effect.get_desc(), " each round"], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], effect : Effect):
        super().__init__(id,name)
        self.effect = effect
    def end_of_round(self, chain):
        new_effect : Effect = copy.deepcopy(self.effect)
        new_effect.execute_with_statics_and_reformat(chain[0], self.reformat_dict(chain), True)

class OnDeathEffect(Ability):
    def get_desc(self):
        return utility.combine_text([self.effect.get_desc(), " on death"], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], effect : Effect):
        super().__init__(id,name)
        self.effect = effect
    def apply(self, chain, effect):
        if isinstance(effect, DeathEvent) and effect.target == chain[2]:
            new_effect : Effect = copy.deepcopy(self.effect)
            new_effect.execute_with_statics_and_reformat(chain[0], self.reformat_dict(chain), True)

class ImmuneToAbility(Ability):
    def get_desc(self):
        return utility.combine_text(["Immune to ", self.abil.get_name()], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], abil : Ability):
        super().__init__(id,name)
        self.abil = abil
    def apply(self, chain : list, effect : Effect):
        if isinstance(effect, AddAbilityEffect) and effect.target == chain[2] and effect.source.is_id(self.abil.id):
            chain[0].add_to_message_queue_if_actor_visible(chain[2], [chain[2].get_name(), " is immune to ", effect.source.get_name(), "!"])
            effect.cancel()