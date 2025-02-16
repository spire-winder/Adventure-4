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
        super().__init__()
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

class Armor(Ability):
    def get_desc(self):
        return ("iron", "+" + str(self.armor_value) + " Armor")
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], armor_value : int = 1):
        super().__init__(id,name)
        self.armor_value = armor_value
    def apply(self, owner, effect : Effect):
        if hasattr(effect, "damage") and effect.target == owner:
            effect.damage -= self.armor_value

class BattleCry(Ability):
    def get_desc(self):
        return utility.combine_text([self.tag.get_name(), " enemies deal ", ("damage","+" + str(self.strength) + " damage"),"."], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], tag_id : Ability, strength : int):
        super().__init__(id,name)
        self.tag = tag_id
        self.strength = strength
    def apply(self, owner, effect : Effect):
        if hasattr(effect, "damage") and effect.source.has_ability(self.tag):
            effect.damage += self.strength

class SelectiveBuff(Ability):
    def get_desc(self):
        return utility.combine_text(["Your ",self.tag.get_name()," attacks deal ", ("damage","+" + str(self.strength) + " damage"),"."], False)
    def __init__(self, id:str, name : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], tag_id : Ability, strength : int):
        super().__init__(id,name)
        self.tag = tag_id
        self.strength = strength
    def apply(self, owner, effect : Effect):
        if hasattr(effect, "damage") and effect.dungeon.actor == owner and effect.source.has_ability(self.tag):
            effect.damage += self.strength