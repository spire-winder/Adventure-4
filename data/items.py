from classes.interactable import *
from classes.actions import *
from data.abilities import *
import copy

items : dict[str:Item] = {
    "wooden_sword":MeleeWeapon(
        name=("wood","Wooden Sword"),
        effect=EffectSelectorTarget(DamageEvent(5))
    ),
    "wooden_bo":MeleeWeapon(
        name=("wood","Wooden Bo"),
        effect=EffectSelectorTarget(RepeatEvent(DamageEvent(3),2))
    ),
    "iron_axe":MeleeWeapon(
        name=("iron","Iron Axe"),
        effect=
            EffectSelectorTarget(
                EffectSequence([
                    DamageEvent(10),
                    ProbabilityEvent(EffectSelectorPredefinedSource(AddAbilityEffect(), Status(get_ability("stun"),3)),0.75)
                ]),
            )
    ),
    "shiv":Equipment(
        name=("iron","Shiv"),
        ability_handler=AbilityHandler([SelectiveBuff("meleebuff",None,get_ability("melee"),2)]),
        slot="Offhand"
    ),
    "wooden_shield":Equipment(
        name=("wood","Wooden Shield"),
        ability_handler=AbilityHandler([Armor("armor",None,1)]),
        slot="Offhand"
    ),
    "iron_ring":Equipment(
        name=("iron","Iron Ring"),
        ability_handler=AbilityHandler([Armor("armor",None,2)]),
        slot="Ring"
    ),
}

def get_item(item_id : str) -> Item:
    return copy.deepcopy(items[item_id])