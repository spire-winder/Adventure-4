from classes.interactable import *
from classes.actions import *
from classes.states import *
from data.entities import get_entity
from data.items import get_item
import systems.save_system
import copy

player : Player = Player(
    "Player Name",
    AbilityHandler(),
    Inventory(
        EquipmentHandler({
            "Weapon":None,
            "Offhand":None,
            "Helmet":None,
            "Armor":None,
            "Boots":None,
            "Ring":None
        }),
        Bag(10)),
    StatHandler({
        "HP":HPContainer(50),
        "MP":MPContainer(50),
        "Bones":BoneContainer(0,25)
    })
)

standard_map : dict = {
    "starting_room": Room(
        ("stone","Ruins of the Sun"), 
        AbilityHandler(), 
        [
            copy.deepcopy(player),
            get_entity("wise_figure"),
            Container(("wood","Wooden Chest"), AbilityHandler(), [
                get_item("wooden_bo"),
                get_item("roast_chicken"),
                get_item("healing_potion"),
                get_item("iron_shovel")
            ]),
            Campfire(("heat", "Roaring Bonfire")),
            Passage(("stone","Eastern Crumbling Doorway"), destination_id="ruins_exit"),
            Destructible(("sand","Pile of Sand"), contents=[get_item("iron_ring")],tool_requirement="Shovel",tool_strength=3)
        ]
    ),
    "ruins_exit": Room(
        ("stone","Ruins Exit"), 
        AbilityHandler(), 
        [
            get_entity("goblin_1"),
            get_item("wooden_shield"),
            Passage(("stone","Western Crumbling Doorway"), destination_id="starting_room"),
            Passage(("stone", "Eastern Stone Passage"), destination_id="ruins_crossroad")
        ]
    ),
    "ruins_crossroad": Room(
        ("stone","Ruins Crossroads"), 
        AbilityHandler(), 
        [
            get_entity("goblin_2"),
            get_entity("goblin_3"),
            get_item("wooden_axe"),
            Container(("wood","Pile of Dirt"), contents=[get_item("wooden_ring"),]),
            Passage(("stone", "Western Stone Passage"), destination_id="ruins_exit"),
            Passage(("magic", "Southern Trailhead"), destination_id="magic_woods_entrance"),
            Passage(("stone", "Northern Stone Trail"), destination_id="goblin_cave_entrance"),
        ]
    ),
    "magic_woods_entrance": Room(
        ("magic", "Enchanted Woods Trail"), 
        AbilityHandler(), 
        [
            get_entity("mage_hater"),
            get_item("regen_potion"),
            Passage(("stone", "Northern Trailhead"), destination_id="ruins_crossroad"),
            Passage(("magic", "Southern Crossroad"), destination_id="forest_crossroad")
        ]
    ),
    "forest_crossroad": Room(
        ("magic", "Enchanted Woods Crossroad"), 
        AbilityHandler(), 
        [
            get_item("iron_ring"),
            get_item("bone_marrow_stew"),
            get_item("sharpening_stone"),
            Campfire(utility.alternate_colors("Magical Campfire",["magic","heat"])),
            Passage(("magic", "Northern Trail"), destination_id="magic_woods_entrance"),
            Passage(("magic", "Western Clearing"), destination_id="forest_clearing"),
            Passage(("magic", "Southern Trail"), destination_id="forest_library")
        ]
    ),
    "forest_clearing": Room(
        ("magic", "Enchanted Woods Clearing"), 
        AbilityHandler(), 
        [
            get_entity("helmet_snail"),
            get_item("magic_ring"),
            Passage(("magic", "Eastern Crossroad"), destination_id="forest_crossroad")
        ]
    ),
    "forest_library": Room(
        ("magic", "Overgrown Library"), 
        AbilityHandler(), 
        [
            Container(("magic", "Overgrown Bookcase"), contents=[get_item("fire_tome"),get_item("magic_armor"), get_item("restoration_potion")]),
            get_entity("forest_mage"),
            Passage(("magic", "Northern Trail"), destination_id="forest_crossroad")
        ]
    ),
    "goblin_cave_entrance": Room(
        ("stone", "Goblin Cave Entrance"), 
        AbilityHandler(), 
        [
            get_item("roast_beef"),
            get_entity("fellow_traveller"),
            get_item("iron_boots"),
            Campfire(("heat", "Small Campfire")),
            Passage(("stone", "Goblin Cave"), destination_id="goblin_cave"),
            Passage(("stone", "Stony Crossroads"), destination_id="ruins_crossroad")
        ]
    ),
    "goblin_cave": Room(
        ("stone", "Goblin Cave"), 
        AbilityHandler(), 
        [
            get_entity("goblin_boss"),
            get_entity("goblin_mage"),
            get_entity("goblin_3"),
            Passage(("stone", "Entrance"), destination_id="goblin_cave_entrance")
        ]
    ),
}

map : dict[str:Room] = {}

ruins_of_the_sun : dict[str:Room] = {
    "starting_room": Room(
        name=[("celestial", "Sky"),("stone", " Chamber")],
        room_contents=[
            player,
            get_entity("wise_figure"),
            get_entity("training_dummy"),
            LockedPassage(("stone", "Chamber Exit (north)"),destination_id="decrepit_cellar",key_id="wooden_key")
        ]
    ),
    "decrepit_cellar": Room(
        name=("stone", "Decrepit Cellar"),
        room_contents=[
            get_entity("greedling"),
            Passage(("stone", "Chamber Entrance (south)"),destination_id="starting_room"),
            Passage(("stone", "Cracked Steps (north)"),destination_id="stone_rotunda")
        ]
    ),
    "stone_rotunda": Room(
        name=("stone", "Stone Rotunda"),
        room_contents=[
            get_entity("large_greedling"),
            LockedPassage(("celestial", "Gate (north)"),destination_id="crumbling_entrance",key_id="crumbling_entrance_key"),
            LockedPassage(("celestial", "Vault Door (east)"),destination_id="ransacked_vault",key_id="ransacked_vault_key"),
            Passage(("stone", "Cracked Steps (south)"),destination_id="decrepit_cellar"),
            Passage(("stone", "Hallway (west)"),destination_id="western_hallway"),
        ]
    ),
    "western_hallway": Room(
        name=("stone", "Western Hallway"),
        room_contents=[
            get_entity("greedling"),
            get_entity("arcane_greedling"),
            Passage(("iron", "Armory Entrance (north)"),destination_id="emptied_armory"),
            Passage(("stone", "Rotunda (east)"),destination_id="stone_rotunda"),
            Passage(("sand", "Sandy Doorway (south)"),destination_id="sandy_chapel"),
            Passage(("stone", "Crypt Door (west)"),destination_id="crypt_of_the_sunblessed"),
        ]
    ),
    "emptied_armory": Room(
        name=("stone", "Emptied Armory"),
        room_contents=[
            get_entity("greedling"),
            Passage(("stone", "Hallway (south)"),destination_id="western_hallway"),
        ]
    ),
    "crypt_of_the_sunblessed": Room(
        name=[("stone", "Crypt of the "), ("celestial", "Sunblessed")],
        room_contents=[
            get_entity("shadow_greedling"),
            Passage(("stone", "Hallway (east)"),destination_id="western_hallway"),
        ]
    ),
    "sandy_chapel": Room(
        name=[("sand", "Sandy "), ("stone", "Chapel")],
        room_contents=[
            Passage(("stone", "Hallway (north)"),destination_id="western_hallway"),
        ]
    ),
    "ransacked_vault": Room(
        name=("stone", "Ransacked Vault"),
        room_contents=[
            get_entity("starved_greedling"),
            Passage(("stone", "Rotunda (west)"),destination_id="stone_rotunda"),
        ]
    ),
    "crumbling_entrance": Room(
        name=("stone", "Crumbling Entrance"),
        room_contents=[
            Passage(("celestial", "Ruins of the Sun Entrance (south)"),destination_id="stone_rotunda"),
        ]
    ),
}

map.update(ruins_of_the_sun)

systems.save_system.create_folder(systems.save_system.map_dir_name)
systems.save_system.save_map("standard", map)