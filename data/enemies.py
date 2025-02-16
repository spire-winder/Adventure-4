from classes.interactable import *
from classes.actions import *
from classes.states import *
from data.abilities import *
from data.items import *
import copy



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