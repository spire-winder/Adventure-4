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
    "goblin_mage_og" : StateEntity(
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
                "Weapon":RandomElement([get_item("wooden_sword"),get_item("wooden_bo"),get_item("wooden_axe")]),
                "Helmet":RandomElement([get_item("leather_helmet"),None]),
                "Armor":RandomElement([get_item("leather_armor"),None]),
                "Boots":RandomElement([get_item("leather_boots"),None]),
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
                "Weapon":RandomElement([get_item("wooden_sword"),get_item("wooden_bo"),get_item("wooden_axe")]),
                "Helmet":RandomElement([get_item("leather_helmet"),None]),
                "Armor":RandomElement([get_item("leather_armor"),None]),
                "Boots":RandomElement([get_item("leather_boots"),None]),
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
                "Helmet":RandomElement([get_item("leather_helmet"),None]),
                "Armor":RandomElement([get_item("leather_armor"),None]),
                "Boots":RandomElement([get_item("leather_boots"),None]),
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
                "Weapon":RandomElement([get_item("wooden_sword"),get_item("wooden_bo"),get_item("wooden_axe")]),
                "Helmet":RandomElement([get_item("leather_helmet"),None]),
                "Armor":RandomElement([get_item("leather_armor"),None]),
                "Boots":RandomElement([get_item("leather_boots"),None]),
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
                "Weapon":RandomElement([get_item("wooden_sword"),get_item("wooden_bo"),get_item("wooden_axe")]),
                "Helmet":RandomElement([get_item("leather_helmet"),None]),
                "Armor":RandomElement([get_item("leather_armor"),None]),
                "Boots":RandomElement([get_item("leather_boots"),None]),
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
                "Weapon":get_item("wooden_sledge"),
                "Helmet":RandomElement([get_item("leather_helmet"),None]),
                "Armor":RandomElement([get_item("leather_armor"),None]),
                "Boots":RandomElement([get_item("leather_boots"),None]),
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
                "Helmet":RandomElement([get_item("leather_helmet"),None]),
                "Armor":RandomElement([get_item("leather_armor"),None]),
                "Boots":RandomElement([get_item("leather_boots"),None]),
            }),
            Bag(-1,[get_item("uneaten_scraps")])
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
                "Helmet":RandomElement([get_item("leather_helmet"),None]),
                "Armor":RandomElement([get_item("leather_armor"),None]),
                "Boots":RandomElement([get_item("leather_boots"),None]),
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
        stathandler=StatHandler({"HP":HPContainer(20), "Bones":BoneContainer(5)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "goblin_mage" : StateEntity(
        name=[("goblin","Goblin "), ("magic", "Mage")],
        ability_handler=AbilityHandler([get_ability("goblin"),DamageTypeBuff("arcane_arts",("magic", "Arcane Arts"), "arcane", 2)]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":RandomElement([get_item("fire_staff"),get_item("ice_staff"),get_item("poison_staff"),get_item("lightning_staff"),get_item("arcane_staff"),get_item("shadow_staff"),get_item("celestial_staff")]),
                "Armor":get_item("mage_cloak"),
                "Boots":get_item("mage_boots"),
            }),
            Bag(-1, [get_item("clarity_crystal"),get_item("wooden_ring")])
        ),
        stathandler=StatHandler({"HP":HPContainer(20),"MP":MPContainer(30), "Bones":BoneContainer(5)}),
        dialogue_manager=None,
        state=IdleState()
    ),
    "goblin_monarch" : StateEntity(
        name=[("goblin","Goblin "), ("heat", "Monarch")],
        ability_handler=AbilityHandler([get_ability("goblin"),SelectiveBuff("buffed",("meat","Bulging Muscles"),get_ability("melee"),3)]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":RandomElement([get_item("rusty_sword"),get_item("rusty_staff"),get_item("rusty_axe"),get_item("rusty_sledge")]),
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

forest_beasts : dict[str:StateEntity] = {
    "mage_hater" : StateEntity(
        name=("magic","Mage Hater"), 
        ability_handler=AbilityHandler([WeakTo("celestial_weakness",("shadow", "Celestial Weakness"),"celestial",5),SelectiveArmor("magebane", ("arcane","Mage Bane"), "arcane", 5)]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("magic_barbs")
            }),
            Bag(-1, [get_item("roast_pork")])
        ), 
        stathandler=StatHandler({"HP":HPContainer(25)}),
        state=IdleState()
    ),
    "maneater" : StateEntity(
        name=("shadow","Maneater"), 
        ability_handler=AbilityHandler([WeakTo("celestial_weakness",("shadow", "Celestial Weakness"),"celestial",5),WeakTo("plant",("healing", "Vines"),"slashing",5)]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("maneater_bite")
            }),
            Bag(-1, [])
        ), 
        stathandler=StatHandler({"HP":HPContainer(25)}),
        state=IdleCannotLeaveState()
    ),
    "waterfall_serpent" : StateEntity(
        name=("water","Waterfall Serpent"), 
        ability_handler=AbilityHandler([WeakTo("celestial_weakness",("shadow", "Celestial Weakness"),"celestial",5),SelectiveArmor("temperature_modulation_heat", ("water","Temperature Modulation"), "heat", 5),SelectiveArmor("temperature_modulation_cold", None, "cold", 5)]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("wave_crash")
            }),
            Bag(-1, [get_item("gillberry"),get_item("frozen_helm"),get_item("serpent_flesh"),get_item("lifeforce_container"),RandomElement([get_item("ice_staff"),get_item("blizzard_scroll")])])
        ), 
        stathandler=StatHandler({"HP":HPContainer(30)}),
        state=IdleCannotLeaveState()
    ),
    "cave_serpent" : StateEntity(
        name=("water","Cave Serpent"), 
        ability_handler=AbilityHandler([SelectiveArmor("temperature_modulation_heat", ("water","Temperature Modulation"), "heat", 3),SelectiveArmor("temperature_modulation_cold", None, "cold", 3)]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("wave_crash")
            }),
            Bag(-1, [get_item("serpent_flesh")])
        ), 
        stathandler=StatHandler({"HP":HPContainer(15)}),
        state=IdleCannotLeaveState()
    ),
    "colossal_bat" : StateEntity(
        name=("meat","Colossal Bat"), 
        ability_handler=AbilityHandler([WeakTo("celestial_weakness",("shadow", "Celestial Weakness"),"celestial",5)]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("bat_bite")
            }),
            Bag(-1, [get_item("bat_flesh")])
        ), 
        stathandler=StatHandler({"HP":HPContainer(10)}),
        state=IdleCannotLeaveState()
    ),
    "temple_guardian" : StateEntity(
        name=utility.alternate_colors("Temple Guardian", ["heat","magic","stone"]), 
        ability_handler=AbilityHandler([WeakTo("arcane_weakness",("arcane", "Arcane Vulnerability"),"arcane",5),SelectiveArmor("heatproof", ("heat","Heatproof"), "heat", 3), Armor("armor",("stone","Ancient Stone"),5)]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("flame_crash")
            }),
            Bag(-1, [get_item("mana_container"),get_item("armory_key"),RandomElement([get_item("fire_staff"),get_item("wildfire_scroll")])])
        ), 
        stathandler=StatHandler({"HP":HPContainer(20)}),
        state=IdleCannotLeaveState()
    ),
    "shadowed_one" : StateEntity(
        name=("shadow","Shadowed One"), 
        ability_handler=AbilityHandler([WeakTo("celestial_weakness",("shadow", "Celestial Weakness"),"celestial",5),Armor("shadow_armor",("shadow","Shade Armor"),3),DamageTypeBuff("shadow_aura",("shadow","Shade Aura"),"shadow",3)]),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("shadow_blade")
            }),
            Bag(-1, [get_item("iron_key"),get_item("gloom_helm"),get_item("umbra_cloak"),get_item("blight_treads"),get_item("twilight_ring"),get_item("dusk_shield")])
        ), 
        stathandler=StatHandler({"HP":HPContainer(40)}),
        state=IdleCannotLeaveState()
    ),
}

entities.update(forest_beasts)

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
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("iron_sword"),
                "Offhand":get_item("wooden_shield"),
                "Helmet":get_item("iron_helmet")
            })
        ), 
        state=PeacefulState(),
        shop_manager=ShopManager({get_item("sharpening_stone"):5,get_item("healing_potion"):10,get_item("dynamite"):8,get_item("roast_chicken"):7})
    ),
    "trailblazer":StateEntity(
        name=("sand", "Trailblazer"),
        stathandler=StatHandler({"HP":HPContainer(40)}),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("iron_staff"),
                "Offhand":get_item("wooden_dagger"),
                "Boots":get_item("iron_boots")
            })
        ), 
        dialogue_manager=DialogueManager("trailblazer_1"),
        state=PeacefulState()
    ),
    "old_figure":StateEntity(
        name=("shadow", "Old Figure"),
        stathandler=StatHandler({"HP":HPContainer(10)}),
        dialogue_manager=DialogueManager("old_figure_1"),
        state=NothingState()
    ),
    "old_figure":StateEntity(
        name=("shadow", "Old Figure"),
        stathandler=StatHandler({"HP":HPContainer(10)}),
        dialogue_manager=DialogueManager("old_figure_1"),
        state=NothingState()
    ),
    "young_child":StateEntity(
        name="Young Child",
        stathandler=StatHandler({"HP":HPContainer(10)}),
        dialogue_manager=DialogueManager("young_child_1"),
        state=NothingState()
    ),
    "tired_parent":Vendor(
        name="Tired Parent",
        stathandler=StatHandler({"HP":HPContainer(10)}),
        dialogue_manager=DialogueManager("tired_parent_1"),
        state=NothingState(),
        shop_manager=ShopManager({get_item("greedling_flesh"):5,get_item("small_rock"):3,get_item("raw_fish"):6,get_item("wooden_shovel"):5})
    ),
    "wise_elder":StateEntity(
        name=("arcane", "Town Elder"),
        stathandler=StatHandler({"HP":HPContainer(10)}),
        dialogue_manager=DialogueManager("wise_elder_1"),
        state=NothingState()
    ),
    "fishy_peasant":StateEntity(
        name=("water", "Fishy Peasant"),
        stathandler=StatHandler({"HP":HPContainer(10)}),
        dialogue_manager=DialogueManager("fishy_peasant_1"),
        state=NothingState()
    ),
    "fishy_merchant":Vendor(
        name=("water","Fishy merchant"),
        stathandler=StatHandler({"HP":HPContainer(10)}),
        dialogue_manager=DialogueManager("fishy_merchant_1"),
        state=NothingState(),
        shop_manager=ShopManager({get_item("serpent_flesh"):20,get_item("empowering_potion"):10,get_item("healing_potion_with_magic"):10})
    ),
    "fishy_noble":StateEntity(
        name=("water", "Fishy Noble"),
        stathandler=StatHandler({"HP":HPContainer(10)}),
        dialogue_manager=DialogueManager("fishy_noble_1"),
        state=NothingState()
    ),
    "coral_king":StateEntity(
        name=("water", "Coral King"),
        stathandler=StatHandler({"HP":HPContainer(30)}),
        dialogue_manager=DialogueManager("coral_king_1"),
        inventory=Inventory(
            EquipmentHandler({
                "Weapon":get_item("iron_staff"),
                "Offhand":get_item("wooden_dagger"),
                "Boots":get_item("waterforged_boots")
            })
        ), 
        state=PeacefulState()
    ),
}

entities.update(npcs)

for x in entities:
    entities[x].id = x

def get_entity(entity_id : str) -> StateEntity:
    return copy.deepcopy(entities[entity_id])