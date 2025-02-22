from classes.interactable import *
from classes.actions import *
from classes.states import *
from data.abilities import *
from data.items import *
import copy

old_entities : dict[str:StateEntity] = {
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
                "Helmet":get_item("magic_helmet")
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
        utility.alternate_colors("Forest Mage",["toxic","magic"]), 
        AbilityHandler(),
        Inventory(
            EquipmentHandler({
                "Weapon":get_item("poison_tome"),
                "Boots":get_item("magic_boots")
            })
        ), 
        StatHandler({"HP":HPContainer(30),"MP":MPContainer(50)}),
        DialogueManager(),
        IdleState()
    )
}

entities : dict[str:StateEntity] = {}

entities.update(old_entities)

greedlings : dict[str:StateEntity] = {
    "greedling" : StateEntity(
        name=("meat","Greedling"), 
        ability_handler=AbilityHandler([get_ability("greedling")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("greedling_tooth")
            })
        ),
        stathandler=StatHandler({"HP":HPContainer(5), "Bones":BoneContainer(2)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "large_greedling" : StateEntity(
        name=("meat","Large Greedling"), 
        ability_handler=AbilityHandler([get_ability("greedling"), get_ability("greedling_boss")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("greedling_tooth")
            })
        ),
        stathandler=StatHandler({"HP":HPContainer(10), "Bones":BoneContainer(3)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "arcane_greedling" : StateEntity(
        name=[("magic", "Arcane"), ("meat"," Greedling")], 
        ability_handler=AbilityHandler([get_ability("greedling")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("magic_greedling_tooth")
            })
        ),
        stathandler=StatHandler({"HP":HPContainer(8), "Bones":BoneContainer(2)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "shadow_greedling" : StateEntity(
        name=[("shadow", "Shadow"), ("meat"," Greedling")], 
        ability_handler=AbilityHandler([get_ability("greedling")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("shadow_greedling_tooth")
            })
        ),
        stathandler=StatHandler({"HP":HPContainer(12), "Bones":BoneContainer(3)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "starved_greedling" : StateEntity(
        name=("meat","Starving Greedling"), 
        ability_handler=AbilityHandler([get_ability("greedling"), get_ability("starved")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("greedling_tooth")
            }),
            Bag(items=[Key(("celestial","Sunforged Key"),key_id="crumbling_entrance_key")])
        ),
        stathandler=StatHandler({"HP":HPContainer(15), "Bones":BoneContainer(1)}),
        dialogue_manager=None,
        state=IdleState()
    )
}

entities.update(greedlings)

npcs : dict[str:StateEntity] = {
    "wise_figure" : StateEntity(
        ("celestial","Wise Figure"), 
        AbilityHandler([ImmuneToAbility("wise",("celestial","Wise"), get_ability("stun"))]),
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
        ("iron","Fellow Traveller"), 
        AbilityHandler([ImmuneToAbility("tough",("iron","Tough"), get_ability("poison"))]),
        Inventory(
            EquipmentHandler({
                "Weapon":get_item("iron_axe"),
                "Offhand":get_item("iron_shield"),
                "Armor":get_item("iron_armor")
            })
        ), 
        StatHandler({"HP":HPContainer(40)}),
        DialogueManager("fellow_traveller_1"),
        PeacefulState()
    ),
    "training_dummy" : StateEntity(
        ("wood", "Training Dummy"),
        ability_handler=AbilityHandler([HiddenAbility(OnDeathEffect("dialogue_swap","Dialogue Swap",SetDialogueEffect("wise_figure_proud","id:wise_figure")))]),
        stathandler=StatHandler({"HP":HPContainer(1)}),
        state=NothingState()
    )
}

entities.update(npcs)

for x in entities:
    entities[x].id = x

def get_entity(entity_id : str) -> StateEntity:
    return copy.deepcopy(entities[entity_id])