from classes.interactable import *
from classes.actions import *
from classes.states import *
from data.enemies import *
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
            "Ring":None,
        }),
        Bag(10)),
    StatHandler({
        "HP":HPContainer(50),
        "MP":MPContainer(50),
    })
)

standard_map : dict = {
    "starting_room": Room(
        ("stone","Ruins of the Sun"), 
        AbilityHandler(), 
        [
            copy.deepcopy(player),
            get_enemy("wise_figure"),
            Container(("wood","Wooden Chest"), AbilityHandler(), [
                get_item("wooden_bo"),
                get_item("roast_chicken"),
                get_item("healing_potion")
            ]),
            Campfire(("fire", "Roaring Bonfire")),
            Passage(("stone","Eastern Crumbling Doorway"), destination_id="ruins_exit")
        ]
    ),
    "ruins_exit": Room(
        ("stone","Ruins Exit"), 
        AbilityHandler(), 
        [
            get_enemy("goblin_1"),
            get_item("wooden_shield"),
            Passage(("stone","Western Crumbling Doorway"), destination_id="starting_room"),
            Passage(("stone", "Eastern Stone Passage"), destination_id="ruins_crossroad")
        ]
    ),
    "ruins_crossroad": Room(
        ("stone","Ruins Crossroads"), 
        AbilityHandler(), 
        [
            get_enemy("goblin_2"),
            get_enemy("goblin_3"),
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
            get_enemy("mage_hater"),
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
            Campfire(utility.alternate_colors("Magical Campfire",["magic","fire"])),
            Passage(("magic", "Northern Trail"), destination_id="magic_woods_entrance"),
            Passage(("magic", "Western Clearing"), destination_id="forest_clearing"),
            Passage(("magic", "Southern Trail"), destination_id="forest_library")
        ]
    ),
    "forest_clearing": Room(
        ("magic", "Enchanted Woods Clearing"), 
        AbilityHandler(), 
        [
            get_enemy("helmet_snail"),
            get_item("magic_ring"),
            Passage(("magic", "Eastern Crossroad"), destination_id="forest_crossroad")
        ]
    ),
    "forest_library": Room(
        ("magic", "Overgrown Library"), 
        AbilityHandler(), 
        [
            Container(("magic", "Overgrown Bookcase"), contents=[get_item("fire_tome"),get_item("magic_armor"), get_item("restoration_potion")]),
            get_enemy("forest_mage"),
            Passage(("magic", "Northern Trail"), destination_id="forest_crossroad")
        ]
    ),
    "goblin_cave_entrance": Room(
        ("stone", "Goblin Cave Entrance"), 
        AbilityHandler(), 
        [
            get_item("roast_beef"),
            get_enemy("fellow_traveller"),
            get_item("iron_boots"),
            Campfire(("fire", "Small Campfire")),
            Passage(("stone", "Goblin Cave"), destination_id="goblin_cave"),
            Passage(("stone", "Stony Crossroads"), destination_id="ruins_crossroad")
        ]
    ),
    "goblin_cave": Room(
        ("stone", "Goblin Cave"), 
        AbilityHandler(), 
        [
            get_enemy("goblin_boss"),
            get_enemy("goblin_mage"),
            get_enemy("goblin_3"),
            Passage(("stone", "Entrance"), destination_id="goblin_cave_entrance")
        ]
    ),
}

map : dict[str:Room] = {}

ruins_of_the_sun : dict[str:Room] = {
    "starting_room": Room(
        name=("stone", "Sky Chamber")
    )
}

map.update(ruins_of_the_sun)

systems.save_system.create_folder(systems.save_system.map_dir_name)
systems.save_system.save_map("standard", standard_map)