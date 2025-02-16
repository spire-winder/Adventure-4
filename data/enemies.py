from classes.interactable import *
from classes.actions import *
from classes.ability import *
from classes.states import *
import utility
import copy

items : dict[str:Item] = {
    "wooden_sword":Weapon(
        name=("wood","Wooden Sword"),
        effect=EffectSelectorTarget(DamageEvent(5))
    ),
    "wooden_bo":Weapon(
        name=("wood","Wooden Bo"),
        effect=EffectSelectorTarget(RepeatEvent(DamageEvent(3),2))
    ),
    "iron_axe":Weapon(
        name=("iron","Iron Axe"),
        effect=EffectSelectorTarget(DamageEvent(10))
    ),
}

def get_item(item_id : str) -> Item:
    return copy.deepcopy(items[item_id])

abilities : dict[str:Ability] = {
    "Goblin":Ability(
        id="Goblin",
        name=("goblin","Goblin"),
        desc="Goblins are creatures with a knack for cooperation and collateral damage."
    ),
    "goblin_boss":BattleCry(
        id="goblin_boss",
        name=utility.alternate_colors("Big Goblin",["goblin","fire"]),
        tag_id="Goblin",
        strength=5
    ),
}

def get_ability(ability_id : str) -> Ability:
    return copy.deepcopy(abilities[ability_id])

enemies : dict[str:StateEntity] = {
    "goblin_1" : StateEntity(
        ("goblin","Hairy Goblin"), 
        AbilityHandler([get_ability("Goblin")]),
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
        AbilityHandler([get_ability("Goblin")]),
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
        AbilityHandler([get_ability("Goblin"),get_ability("goblin_boss")]),
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