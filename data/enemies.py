from classes.interactable import *
from classes.actions import *
from classes.states import *
from data.abilities import *
from data.items import *
import copy

enemies : dict[str:StateEntity] = {
    "goblin_1" : StateEntity(
        name=("goblin","Hairy Goblin"), 
        ability_handler=AbilityHandler([get_ability("goblin")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("wooden_sword"),
                "Helmet":get_item("leather_helmet")
            })
        ), 
        stathandler=StatHandler({"HP":HPContainer(8)}),
        state=IdleState()
    ),
    "goblin_2" : StateEntity(
        name=("goblin","Lazy Goblin"), 
        ability_handler=AbilityHandler([get_ability("goblin")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":None,
                "Offhand":get_item("wooden_dagger"),
                "Armor":get_item("leather_armor")
            })
        ), 
        stathandler=StatHandler({"HP":HPContainer(10)}),
        state=IdleState()
    ),
    "goblin_3" : StateEntity(
        name=("goblin","Goblin Captain"), 
        ability_handler=AbilityHandler([get_ability("goblin")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("iron_sword"),
                "Boots":get_item("leather_boots")
            })
        ), 
        stathandler=StatHandler({"HP":HPContainer(10)}),
        state=IdleState()
    ),
    "mage_hater" : StateEntity(
        name=("magic","Mage Hater"), 
        ability_handler=AbilityHandler([SelectiveArmor("magebane", "Mage Bane", "arcane", 5)]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("magic_barbs")
            }),
            Bag(-1, [get_item("roast_pork")])
        ), 
        stathandler=StatHandler({"HP":HPContainer(15)}),
        state=IdleState()
    ),
    "helmet_snail" : StateEntity(
        name=("iron","Helmet Snail"), 
        ability_handler=AbilityHandler([]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("eye_whip"),
                "Helmet":get_item("iron_helmet")
            })
        ), 
        stathandler=StatHandler({"HP":HPContainer(25)}),
        state=IdleState()
    ),
    "goblin_mage" : StateEntity(
        utility.alternate_colors("Goblin Mage",["goblin","magic"]), 
        AbilityHandler([get_ability("goblin")]),
        Inventory(
            EquipmentHandler({
                "Weapon":get_item("magic_staff"),
                "Offhand":get_item("clarity_crystal"),
                "Armor":get_item("magic_armor")
            })
        ), 
        StatHandler({"HP":HPContainer(20),"MP":MPContainer(20)}),
        DialogueManager(),
        IdleState()
    ),
    "goblin_boss" : StateEntity(
        ("goblin","Goblin Boss"), 
        AbilityHandler([get_ability("goblin"),get_ability("goblin_boss")]),
        Inventory(
            EquipmentHandler({
                "Weapon":get_item("magic_sword"),
                "Offhand":get_item("iron_shiv"),
            }),
            Bag(-1,[get_item("roast_beef")])
        ), 
        StatHandler({"HP":HPContainer(30)}),
        DialogueManager(),
        IdleState()
    ),
    "forest_mage" : StateEntity(
        utility.alternate_colors("Forest Mage",["poison","magic"]), 
        AbilityHandler(),
        Inventory(
            EquipmentHandler({
                "Weapon":get_item("poison_tome"),
                "Armor":get_item("magic_helmet"),
                "Boots":get_item("iron_boots")
            })
        ), 
        StatHandler({"HP":HPContainer(30),"MP":MPContainer(50)}),
        DialogueManager(),
        IdleState()
    ),
    "wise_figure" : StateEntity(
        ("wood","Wise Figure"), 
        AbilityHandler([ImmuneToAbility("wise","Wise", get_ability("stun"))]),
        Inventory(
            EquipmentHandler({
                "Weapon":get_item("magic_axe"),
                "Offhand":get_item("magic_shield")
            })
        ), 
        StatHandler({"HP":HPContainer(40)}),
        DialogueManager("wise_figure_1"),
        PeacefulState()
    ),
    "fellow_traveller" : StateEntity(
        ("wood","Fellow Traveller"), 
        AbilityHandler([ImmuneToAbility("tough","Tough", get_ability("poison"))]),
        Inventory(
            EquipmentHandler({
                "Weapon":get_item("iron_axe"),
                "Offhand":get_item("iron_shield")
            })
        ), 
        StatHandler({"HP":HPContainer(40)}),
        DialogueManager("fellow_traveller_1"),
        PeacefulState()
    ),
}

def get_enemy(enemy_id : str) -> StateEntity:
    return copy.deepcopy(enemies[enemy_id])