from classes.interactable import *
from classes.actions import *
from classes.states import *
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
        effect=EffectSelectorTarget(DamageEvent(10))
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

enemies : dict[str:StateEntity] = {
    "goblin_1" : StateEntity(
        ("goblin","Hairy Goblin"), 
        AbilityHandler([get_ability("goblin")]),
        Inventory(
            EquipmentHandler({
                "Weapon":get_item("wooden_bo")
            })
        ), 
        StatHandler({"HP":HPContainer(10)}),
        IdleState()
    ),
    "goblin_2" : StateEntity(
        ("goblin","Lazy Goblin"), 
        AbilityHandler([get_ability("goblin")]),
        Inventory(
            EquipmentHandler({
                "Weapon":None
            })
        ), 
        StatHandler({"HP":HPContainer(12)}),
        DialogueManager(),
        IdleState()
    ),
    "goblin_boss" : StateEntity(
        ("goblin","Goblin Boss"), 
        AbilityHandler([get_ability("goblin"),get_ability("goblin_boss")]),
        Inventory(
            EquipmentHandler({
                "Weapon":get_item("iron_axe")
            })
        ), 
        StatHandler({"HP":HPContainer(40)}),
        DialogueManager(),
        IdleState()
    ),
    "wise_figure" : StateEntity(
        ("wood","Wise Figure"), 
        AbilityHandler(),
        Inventory(
            EquipmentHandler({
                "Weapon":get_item("iron_axe")
            })
        ), 
        StatHandler({"HP":HPContainer(40)}),
        DialogueManager("wise_figure_1"),
        PeacefulState()
    ),
}

def get_enemy(enemy_id : str) -> StateEntity:
    return copy.deepcopy(enemies[enemy_id])