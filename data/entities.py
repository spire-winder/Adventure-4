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
                "Weapon":get_item("poison_staff"),
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
                "Weapon":get_item("tooth")
            }),
            Bag(-1,[get_item("greedling_flesh")])
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
                "Weapon":get_item("tooth")
            }),
            Bag(-1,[get_item("greedling_flesh")])
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
                "Weapon":get_item("magic_tooth")
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
                "Weapon":get_item("shadow_tooth")
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
                "Weapon":get_item("tooth")
            }),
            Bag(items=[Key(("celestial","Sunforged Key"),key_id="crumbling_entrance_key")])
        ),
        stathandler=StatHandler({"HP":HPContainer(15), "Bones":BoneContainer(1)}),
        dialogue_manager=None,
        state=IdleState()
    )
}

entities.update(greedlings)


goblins : dict[str:StateEntity] = {
    "goblin_guard_spawned" : StateEntity(
        name=[("goblin","Goblin Guard")], 
        ability_handler=AbilityHandler([get_ability("goblin")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("rusty_sword"),
                "Helmet":get_item("leather_helmet"),
                "Armor":get_item("leather_armor"),
                "Boots":get_item("leather_boots"),
            }),
            Bag(-1,[get_item("uneaten_scraps")])
        ),
        stathandler=StatHandler({"HP":HPContainer(10), "Bones":BoneContainer(3)}),
        dialogue_manager=None,
        state=WanderState(2)
    ),
    "goblin_guard" : StateEntity(
        name=[("goblin","Goblin Guard")], 
        ability_handler=AbilityHandler([get_ability("goblin")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("rusty_sword"),
                "Helmet":get_item("leather_helmet"),
                "Armor":get_item("leather_armor"),
                "Boots":get_item("leather_boots"),
            }),
            Bag(-1,[get_item("uneaten_scraps")])
        ),
        stathandler=StatHandler({"HP":HPContainer(10), "Bones":BoneContainer(3)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "goblin_hooligan" : StateEntity(
        name=[("goblin","Goblin Hooligan")], 
        ability_handler=AbilityHandler([get_ability("goblin")]),
        inventory=Inventory(
            EquipmentHandler({
                "Helmet":get_item("leather_helmet"),
                "Armor":get_item("leather_armor"),
                "Boots":get_item("leather_boots"),
            }),
            Bag(-1,[get_item("uneaten_scraps"),get_item("small_rock"),get_item("small_rock")])
        ),
        stathandler=StatHandler({"HP":HPContainer(10), "Bones":BoneContainer(3)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "goblin_officer" : StateEntity(
        name=[("goblin","Goblin Officer")], 
        ability_handler=AbilityHandler([get_ability("goblin")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("rusty_axe"),
                "Helmet":get_item("leather_helmet"),
                "Armor":get_item("leather_armor"),
                "Boots":get_item("leather_boots"),
            }),
            Bag(-1,[get_item("uneaten_scraps")])
        ),
        stathandler=StatHandler({"HP":HPContainer(12), "Bones":BoneContainer(4)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "goblin_commander" : StateEntity(
        name=[("goblin","Goblin Commander")], 
        ability_handler=AbilityHandler([get_ability("goblin"),get_ability("goblin_battle_cry")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("rusty_staff"),
                "Helmet":get_item("leather_helmet"),
                "Armor":get_item("leather_armor"),
                "Boots":get_item("leather_boots"),
            }),
            Bag(-1,[get_item("uneaten_scraps")])
        ),
        stathandler=StatHandler({"HP":HPContainer(15), "Bones":BoneContainer(5)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "goblin_basher" : StateEntity(
        name=[("goblin","Goblin Basher")], 
        ability_handler=AbilityHandler([get_ability("goblin")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("rusty_sledge"),
                "Helmet":get_item("leather_helmet"),
                "Armor":get_item("leather_armor"),
                "Boots":get_item("leather_boots"),
            }),
            Bag(-1,[get_item("uneaten_scraps")])
        ),
        stathandler=StatHandler({"HP":HPContainer(15), "Bones":BoneContainer(5)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "goblin_miner" : StateEntity(
        name=[("goblin","Goblin Miner")], 
        ability_handler=AbilityHandler([get_ability("goblin")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("rusty_pickaxe"),
                "Helmet":get_item("leather_helmet"),
                "Armor":get_item("leather_armor"),
                "Boots":get_item("leather_boots"),
            }),
            Bag(-1,[get_item("uneaten_scraps")])
        ),
        stathandler=StatHandler({"HP":HPContainer(10), "Bones":BoneContainer(3)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "test_goblin" : StateEntity(
        name=[("heat","Demo"),("goblin"," Goblin")], 
        ability_handler=AbilityHandler([get_ability("goblin")]),
        inventory=Inventory(
            EquipmentHandler({
            })
        ),
        stathandler=StatHandler({"HP":HPContainer(10), "Bones":BoneContainer(3)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "demogob" : StateEntity(
        name=[("heat","Demo"),("goblin","gob")], 
        ability_handler=AbilityHandler([get_ability("goblin")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":None,
                "Helmet":get_item("leather_helmet"),
                "Armor":get_item("leather_armor"),
                "Boots":get_item("leather_boots"),
            }),
            Bag(-1,[get_item("dynamite"),get_item("dynamite")])
        ),
        stathandler=StatHandler({"HP":HPContainer(10), "Bones":BoneContainer(3)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "goblin_chef" : StateEntity(
        name=[("goblin","Goblin "), "Chef"],
        ability_handler=AbilityHandler([get_ability("goblin")]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("rusty_spatula"),
                "Helmet":get_item("chef_hat"),
                "Armor":get_item("chef_apron"),
            }),
            Bag(-1, [get_item("roast_chicken"),get_item("roast_beef"),get_item("bone_marrow_stew")])
        ),
        stathandler=StatHandler({"HP":HPContainer(25), "Bones":BoneContainer(5)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "goblin_mage" : StateEntity(
        name=[("goblin","Goblin "), ("magic", "Mage")],
        ability_handler=AbilityHandler([get_ability("goblin"),DamageTypeBuff("arcane_arts",("magic", "Arcane Arts"), "arcane", 2)]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("arcane_staff"),
                "Armor":get_item("mage_cloak"),
                "Boots":get_item("mage_boots"),
            }),
            Bag(-1, [get_item("clarity_crystal"),get_item("wooden_ring")])
        ),
        stathandler=StatHandler({"HP":HPContainer(25),"MP":MPContainer(30), "Bones":BoneContainer(5)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "goblin_monarch" : StateEntity(
        name=[("goblin","Goblin "), ("heat", "Monarch")],
        ability_handler=AbilityHandler([get_ability("goblin"),SelectiveBuff("buffed",("meat","Bulging Muscles"),get_ability("melee"),3)]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("iron_sword"),
                "Armor":get_item("iron_helmet"),
                "Armor":get_item("iron_armor"),
                "Boots":get_item("iron_boots"),
            }),
            Bag(-1, [get_item("garden_key")])
        ),
        stathandler=StatHandler({"HP":HPContainer(25), "Bones":BoneContainer(5)}),
        dialogue_manager=None,
        state=IdleState()
    )
}

entities.update(goblins)

spined : dict[str:StateEntity] = {
    "spined_rat" : StateEntity(
        name=[("iron","Spined "), ("meat", "Rat")], 
        ability_handler=AbilityHandler([get_ability("spined"),Reciprocate("spines",("iron","Spines"),DamageEvent("self","attacker",2,"slashing"))]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("tooth")
            })
        ),
        stathandler=StatHandler({"HP":HPContainer(10), "Bones":BoneContainer(3)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "spined_human_1" : StateEntity(
        name=[("iron","Spined "), "Human"],
        ability_handler=AbilityHandler([get_ability("spined"),Reciprocate("spines",("iron","Spines"),DamageEvent("self","attacker",3,"slashing"))]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("rusty_staff"),
                "Offhand":get_item("wooden_shield"),
                "Helmet":get_item("leather_helmet")
            })
        ),
        stathandler=StatHandler({"HP":HPContainer(15), "Bones":BoneContainer(5)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "spined_human_2" : StateEntity(
        name=[("iron","Spined "), "Human"],
        ability_handler=AbilityHandler([get_ability("spined"),Reciprocate("spines",("iron","Spines"),DamageEvent("self","attacker",3,"slashing"))]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("rusty_axe"),
                "Helmet":get_item("leather_helmet"),
                "Boots":get_item("leather_boots"),
            })
        ),
        stathandler=StatHandler({"HP":HPContainer(15), "Bones":BoneContainer(5)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "spined_human_spawned" : StateEntity(
        name=[("iron","Spined "), "Human"],
        ability_handler=AbilityHandler([get_ability("spined"),Reciprocate("spines",("iron","Spines"),DamageEvent("self","attacker",3,"slashing"))]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("rusty_sword")
            })
        ),
        stathandler=StatHandler({"HP":HPContainer(15), "Bones":BoneContainer(5)}),
        dialogue_manager=None,
        state=WanderState(3)
    ),
    "spined_chef" : StateEntity(
        name=[("iron","Spined "), "Chef"],
        ability_handler=AbilityHandler([get_ability("spined"),Reciprocate("spines",("iron","Spines"),DamageEvent("self","attacker",5,"slashing"))]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("rusty_spatula"),
                "Helmet":get_item("chef_hat"),
                "Armor":get_item("chef_apron"),
            }),
            Bag(-1, [get_item("roast_chicken"),get_item("bone_marrow_stew")])
        ),
        stathandler=StatHandler({"HP":HPContainer(25), "Bones":BoneContainer(5)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "spined_wizard" : StateEntity(
        name=[("iron","Spined "), ("magic", "Wizard")],
        ability_handler=AbilityHandler([get_ability("spined"),Reciprocate("spines",("iron","Spines"),DamageEvent("self","attacker",5,"slashing"))]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("arcane_staff"),
                "Armor":get_item("mage_cloak"),
                "Boots":get_item("mage_boots"),
            }),
            Bag(-1, [get_item("clarity_crystal"),get_item("wooden_ring")])
        ),
        stathandler=StatHandler({"HP":HPContainer(25),"MP":MPContainer(30), "Bones":BoneContainer(5)}),
        dialogue_manager=None,
        state=IdleState()
    )
}

entities.update(spined)

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
    ),
    "thrifty_traveller":Vendor(
        name=("iron", "Thrifty Traveller"),
        stathandler=StatHandler({"HP":HPContainer(40)}),
        dialogue_manager=DialogueManager("thrifty_traveller_1"),
        state=PeacefulState(),
        shop_manager=ShopManager({get_item("sharpening_stone"):5,get_item("healing_potion"):10,get_item("dynamite"):8,get_item("roast_chicken"):7})
    )
}

entities.update(npcs)

for x in entities:
    entities[x].id = x

def get_entity(entity_id : str) -> StateEntity:
    return copy.deepcopy(entities[entity_id])