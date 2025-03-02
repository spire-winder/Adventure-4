from classes.interactable import *
from classes.actions import *
from classes.states import *
from data.entities import get_entity
from data.items import get_item
from classes.ability import Spawner
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
        Bag(10,[get_item("rusty_pickaxe"),get_item("sharpening_stone")])),
    StatHandler({
        "HP":HPContainer(50),
        "MP":MPContainer(50),
        "Bones":BoneContainer(0,100)
    })
)

standard_map : dict = {
    "starting_room": Room(
        ("stone","Ruins of the Sun"), 
        AbilityHandler(), 
        [
            player,
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
            Container(("magic", "Overgrown Bookcase"), contents=[get_item("fire_staff"),get_item("magic_armor"), get_item("restoration_potion")]),
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

misc_dic : dict[str:] = {
    "arcane_entrance":LockedPassage(("stone", "Hidden Passage"),destination_id="shattered_spire"),
    "arcane_entrance_lever":Lever(("stone","Hidden Lever"),oneffect=LockEffect("item","id:arcane_entrance"),offeffect=UnlockEffect("item","id:arcane_entrance")),
    "arcane_archive_entrance":LockedPassage(("magic", "Arcane Passage"), destination_id="arcane_archive"),
    "arcane_archive_lever":Lever(("stone","Unmarked Lever"),oneffect=LockEffect("item","roomid:throne_room:arcane_entrance"),offeffect=UnlockEffect("item","roomid:throne_room:arcane_archive_entrance")),
    "hidden_stash_entrance":Passage(("water", "Behind the Waterfall"), destination_id="hidden_stash"),
}

for x in misc_dic:
    misc_dic[x].id = x

def get_misc(entity_id : str) -> StateEntity:
    return copy.deepcopy(misc_dic[entity_id])

ruins_of_the_sun : dict[str:Room] = {
    "starting_room": Room(
        name=[("celestial", "Sky"),("stone", " Chamber")],
        room_contents=[
            player,
            get_entity("wise_figure"),
            get_entity("training_dummy"),
            LockedPassage(("stone", "Chamber Exit"),destination_id="decrepit_cellar",key_id="wooden_key"),
            #Campfire(("heat", "DEBUG Campfire"))
        ]
    ),
    "decrepit_cellar": Room(
        name=("stone", "Decrepit Cellar"),
        room_contents=[
            get_entity("greedling"),
            Container(("wood", "Wooden Chest"), contents=[get_item("rusty_sword"),get_item("wooden_shield")]),
            Passage(("stone", "Chamber Entrance"),destination_id="starting_room"),
            Passage(("stone", "Cracked Steps"),destination_id="stone_rotunda")
        ]
    ),
    "stone_rotunda": Room(
        name=("stone", "Stone Rotunda"),
        ability_handler=AbilityHandler([Spawner([get_entity("large_greedling")],2,50,5)]),
        room_contents=[
            get_entity("large_greedling"),
            Campfire(("heat", "Roaring Campfire")),
            LockedPassage(("celestial", "Temple Gate"),destination_id="crumbling_entrance",key_id="crumbling_entrance_key"),
            LockedPassage(("celestial", "Vault Door"),destination_id="ransacked_vault",key_id="ransacked_vault_key"),
            Passage(("stone", "Cracked Steps"),destination_id="decrepit_cellar"),
            Passage(("stone", "Hallway"),destination_id="western_hallway"),
        ]
    ),
    "western_hallway": Room(
        name=("stone", "Western Hallway"),
        ability_handler=AbilityHandler([Spawner([get_entity("arcane_greedling")],1,25)]),
        room_contents=[
            get_entity("greedling"),
            get_entity("arcane_greedling"),
            Passage(("iron", "Armory Entrance"),destination_id="emptied_armory"),
            Passage(("stone", "Rotunda"),destination_id="stone_rotunda"),
            Passage(("sand", "Sandy Doorway"),destination_id="sandy_chapel"),
            Passage(("stone", "Crypt Door"),destination_id="crypt_of_the_sunblessed"),
        ]
    ),
    "emptied_armory": Room(
        name=("stone", "Emptied Armory"),
        room_contents=[
            get_entity("greedling"),
            Container(("iron","Weapon Rack"),contents=[get_item("rusty_axe"), get_item("rusty_staff"),]),
            Passage(("stone", "Hallway"),destination_id="western_hallway"),
        ]
    ),
    "crypt_of_the_sunblessed": Room(
        name=[("stone", "Crypt of the "), ("celestial", "Sunblessed")],
        ability_handler=AbilityHandler([Spawner([get_entity("shadow_greedling")],1,25)]),
        room_contents=[
            get_entity("shadow_greedling"),
            Container(("stone", "Defiled Grave"), contents=[get_item("wooden_shovel"),get_item("wooden_dagger")]),
            Passage(("stone", "Hallway"),destination_id="western_hallway"),
        ]
    ),
    "sandy_chapel": Room(
        name=[("sand", "Sandy "), ("stone", "Chapel")],
        room_contents=[
            Container(("wood", "Wooden Barrel"), contents=[get_item("roast_chicken")]),
            Destructible(("sand", "Pile of Sand"), contents=[Key(name=("celestial", "Vault Key"), key_id="ransacked_vault_key")], tool_requirement="Shovel", tool_strength=1),
            Passage(("stone", "Hallway"),destination_id="western_hallway"),
        ]
    ),
    "ransacked_vault": Room(
        name=("stone", "Ransacked Vault"),
        room_contents=[
            get_entity("starved_greedling"),
            get_item("lifeforce_container"),
            Passage(("stone", "Rotunda"),destination_id="stone_rotunda")
        ]
    ),
    "crumbling_entrance": Room(
        name=("stone", "Crumbling Entrance"),
        room_contents=[
            get_entity("thrifty_traveller"),
            Passage(("celestial", "Temple Gate"),destination_id="stone_rotunda"),
            Passage(("stone", "Northern Cavern"),destination_id="empty_cavern"),
        ]
    ),
}

map.update(ruins_of_the_sun)

shattered_ruins : dict[str:Room] = {
    "empty_cavern": Room(
        name=[("stone", "Empty Cavern")],
        ability_handler=AbilityHandler([Spawner([get_entity("goblin_miner")],1,25,3)]),
        room_contents=[
            Passage(("celestial", "Southern Temple"),destination_id="crumbling_entrance"),
            Passage(("stone", "Northern Trail"),destination_id="ancient_courtyard"),
            get_entity("goblin_miner"),
            Destructible(("stone", "Rubble"), contents=[get_item("wooden_ring"),get_item("spiked_shield")], tool_requirement="Pickaxe", tool_strength=2)
        ]
    ),
    "ancient_courtyard": Room(
        name=("stone", "Ancient Courtyard"),
        room_contents=[
            Passage(("stone", "Northern Road"),destination_id="cobblestone_road"),
            Passage(("stone", "Eastern Cave"),destination_id="echoing_cave"),
            Passage(("stone", "Southern Trail"),destination_id="empty_cavern"),
            Passage(("stone", "Western Gate"),destination_id="foreboding_entry"),
            Campfire(("heat", "Dying Campfire"))
        ]
    ),
    "echoing_cave": Room(
        name=("stone", "Echoing Cave"),
        ability_handler=AbilityHandler([Spawner([get_entity("demogob")],1,25,3)]),
        room_contents=[
            Passage(("stone", "Western Courtyard"),destination_id="ancient_courtyard"),
            SubmergedPassage(("water", "Underwater Passage"),destination_id="submerged_cavern"),
            get_entity("demogob"),
            get_entity("goblin_miner"),
            get_item("dynamite")
        ]
    ),
    "submerged_cavern": Room(
        name=("water", "Submerged Cavern"),
        ability_handler=AbilityHandler([get_ability("underwater_room"),Spawner([get_entity("cave_serpent")],1,25,3)]),
        room_contents=[
            get_entity("cave_serpent"),
            SubmergedPassage(("stone", "Cave"),destination_id="echoing_cave"),
            SubmergedPassage(("water", "Glowing Trail"),destination_id="oceanic_promenade"),
        ]
    ),
    "cobblestone_road": Room(
        name=("stone", "Cobblestone Road"),
        room_contents=[
            Passage(("stone", "Southern Courtyard"),destination_id="ancient_courtyard"),
            Passage(("shadow", "Shadowed Forest"),destination_id="forest_entrance"),
            get_entity("goblin_guard")
        ]
    ),
    "foreboding_entry": Room(
        name=("stone", "Foreboding Entry"),
        room_contents=[
            Passage(("stone", "Eastern Courtyard"),destination_id="ancient_courtyard"),
            Passage(("stone", "Western Hall"),destination_id="ransacked_hall"),
            get_entity("goblin_guard"),
            get_entity("goblin_commander")
        ]
    ),
    "ransacked_hall": Room(
        name=("stone", "Ransacked Hall"),
        ability_handler=AbilityHandler([Spawner([get_entity("goblin_guard_spawned")],3,20,2)]),
        room_contents=[
            get_entity("goblin_officer"),
            get_entity("goblin_basher"),
            Passage(("stone", "Eastern Entryway"),destination_id="foreboding_entry"),
            Passage(("stone", "Parlor"),destination_id="demolished_parlor"),
            Passage(("stone", "Kitchen"),destination_id="kitchen"),
            UsableRoomObj(("arcane", "Curtains"),ability_handler=AbilityHandler([get_ability("hidden_single_use")]),actions={"unveil":AddRoomObjEffect("place",get_misc("arcane_entrance"))}),
            UsableRoomObj(("arcane", "Curtains"),ability_handler=AbilityHandler([get_ability("hidden_single_use")]),actions={"unveil":AddRoomObjEffect("place",get_misc("arcane_entrance_lever"))}),
        ]
    ),
    "kitchen": Room(
        name=("stone", "Royal Kitchen"),
        ability_handler=AbilityHandler([Spawner([get_entity("goblin_chef")],1,15,2)]),
        room_contents=[
            get_entity("goblin_chef"),
            Campfire(("heat","Royal Hearth")),
            Passage(("stone", "Hall"),destination_id="ransacked_hall"),
        ]
    ),
    "shattered_spire": Room(
        name=("stone", "Shattered Spire"),
        ability_handler=AbilityHandler([Spawner([get_entity("goblin_mage")],1,15,2)]),
        room_contents=[
            get_entity("goblin_mage"),
            Passage(("stone", "Spire Exit"),destination_id="ransacked_hall"),
            get_misc("arcane_archive_lever"),
            Container(("wood","Wooden Bookshelf"), contents=[get_item("mystic_scroll"),get_item("restoration_potion")])
        ]
    ),
    "demolished_parlor": Room(
        name=("stone", "Demolished Parlor"),
        room_contents=[
            get_item("uneaten_scraps"),
            get_entity("goblin_hooligan"),
            get_entity("goblin_hooligan"),
            Passage(("stone", "Eastern Hall"),destination_id="ransacked_hall"),
            Passage(("stone", "Royal Suite"),destination_id="royal_suite"),
            Passage(("iron", "Southern Armory"),destination_id="forgotten_armory"),
            Passage(("iron", "Throne Room"),destination_id="throne_room"),
        ]
    ),
    "throne_room": Room(
        name=("stone", "Throne Room"),
        room_contents=[
            get_entity("goblin_monarch"),
            get_entity("goblin_commander"),
            get_entity("goblin_guard"),
            Passage(("stone", "Parlor"),destination_id="demolished_parlor"),
            Destructible(("iron", "Broken Throne"),contents=[get_misc("arcane_archive_entrance")],tool_requirement="Pickaxe",tool_strength=3)
        ]
    ),
    "arcane_archive": Room(
        name=("magic", "Arcane Archive"),
        room_contents=[
            get_item("mana_container"),
            Container(("wood","Staff Display"),contents=[RandomElement([get_item("fire_staff"),get_item("ice_staff"),get_item("poison_staff"),get_item("lightning_staff"),get_item("arcane_staff"),get_item("shadow_staff"),get_item("celestial_staff")]),]),
            Container(("wood","Scroll Rack"),contents=[RandomElement([get_item("wildfire_scroll"),get_item("blizzard_scroll"),get_item("venom_scroll"),get_item("storm_scroll"),get_item("mystic_scroll"),get_item("eclipse_scroll"),get_item("starfire_scroll")])]),
            Container(("wood","Alchemy Station"),contents=[get_item("empowering_potion"),get_item("regen_potion")]),
            Passage(("stone", "Archive Exit"),destination_id="throne_room"),
        ]
    ),
    "hidden_garden": Room(
        name=("stone", "Hidden Garden"),
        room_contents=[
            get_item("lifeforce_container"),
            Container(("wood","Planter Box"),contents=[get_item("torchroot_buds"),get_item("shockflower_blossom"),get_item("surface_apple")]),
            Passage(("stone", "Garden Exit"),destination_id="royal_suite"),
        ]
    ),
    "forgotten_armory": Room(
        name=("stone", "Forgotten Armory"),
        room_contents=[
            get_item("iron_shield"),
            get_item("iron_ring"),
            get_item("iron_axe"),
            get_item("sharpening_stone"),
            Passage(("stone", "Parlor"),destination_id="demolished_parlor"),
        ]
    ),
    "royal_suite": Room(
        name=("stone", "Royal Suite"),
        room_contents=[
            Container(("wood","Wooden Chest"), contents=[get_item("iron_ring"),get_item("healing_potion")]),
            Passage(("stone", "Parlor"),destination_id="demolished_parlor"),
            LockedPassage(("wood", "Wooden Door"),destination_id="hidden_garden",key_id="garden_key"),
        ]
    ),
}

map.update(shattered_ruins)

shadowed_forest : dict[str:Room] = {
    "forest_entrance": Room(
        name=("shadow", "Forest Entrance"),
        room_contents=[
            get_entity("trailblazer"),
            Passage(("stone", "Southern Road"),destination_id="cobblestone_road"),
            Passage(("shadow", "Northern Grove"),destination_id="umbral_grove"),
        ]
    ),
    "umbral_grove": Room(
        name=("shadow", "Umbral Grove"),
        ability_handler=AbilityHandler([Spawner([get_entity("mage_hater")],1,15,5)]),
        room_contents=[
            get_entity("mage_hater"),
            Passage(("shadow", "Forest Entrance"),destination_id="forest_entrance"),
            Passage(("shadow", "Northern Crossroads"),destination_id="forest_crossroads"),
        ]
    ),
    "forest_crossroads": Room(
        name=("shadow", "Forest Crossroads"),
        room_contents=[
            get_entity("old_figure"),
            Campfire(("heat", "Campfire Embers")),
            Passage(("stone", "Northern Cavern"),destination_id="cavern_maw"),
            Passage(("water", "Eastern Stream"),destination_id="shadowed_stream"),
            Passage(("shadow", "Southern Grove"),destination_id="umbral_grove"),
            Passage(("shadow", "Western Hollow"),destination_id="maneaters_hollow"),
        ]
    ),
    "cavern_maw": Room(
        name=("stone", "Cavern Maw"),
        ability_handler=AbilityHandler([Spawner([get_entity("colossal_bat")],2,10,5)]),
        room_contents=[
            get_entity("colossal_bat"),
            get_entity("colossal_bat"),
            Passage(("shadow", "Southern Crossroads"),destination_id="forest_crossroads"),
            Passage(("iron", "Iron Gateway"),destination_id="iron_gate"),
        ]
    ),
    "iron_gate": Room(
        name=("iron", "Iron Gateway"),
        room_contents=[
            Passage(("stone", "Cavern"),destination_id="cavern_maw"),
            LockedPassage(("iron", "Iron Gate"),destination_id="star_chamber",key_id="iron_key"),
        ]
    ),
    "star_chamber": Room(
        name=utility.alternate_colors("Star Chamber",["celestial","shadow"]),
        room_contents=[
            LockedPassage(("iron", "Iron Gate"),destination_id="iron_gate",key_id="iron_key"),
            get_entity("shadowed_one"),
        ]
    ),
    "shadowed_stream": Room(
        name=("water", "Shadowed Stream"),
        room_contents=[
            get_entity("mage_hater"),
            Destructible(("water","Pile of Mud"),contents=[get_item("spiked_ring"),],tool_requirement="Shovel",tool_strength=1),
            Passage(("water", "Eastern Lake"),destination_id="dark_lake"),
            Passage(("shadow", "Western Crossroads"),destination_id="forest_crossroads"),
        ]
    ),
    "dark_lake": Room(
        name=("water", "Dark Lake"),
        room_contents=[
            Passage(("wood", "Wooden Canoe"),destination_id="lumin"),
            Passage(("water", "Western Stream"),destination_id="shadowed_stream"),
            Passage(("water", "Southern Waterfall"),destination_id="waterfall"),
            SubmergedPassage(("water", "Lake Surface"),destination_id="lakeside_keep"),
        ]
    ),
    "waterfall": Room(
        name=("water", "Waterfall"),
        ability_handler=AbilityHandler([Spawner([get_entity("waterfall_serpent")],1,25,5)]),
        room_contents=[
            get_entity("waterfall_serpent"),
            UsableRoomObj(("shadow", "Darkwood Fronds"),ability_handler=AbilityHandler([get_ability("hidden_single_use")]),actions={"investigate":AddRoomObjEffect("place",get_misc("hidden_stash_entrance"))}),
            Passage(("water", "Northern Lake"),destination_id="dark_lake"),
        ]
    ),
    "hidden_stash": Room(
        name=("shadow", "Hidden Stash"),
        room_contents=[
            Destructible(("sand","Pile of Sand"),contents=[get_item("diving_gear"),get_item("magic_ring"),],tool_requirement="Shovel",tool_strength=1),
            Container(("wood","Wooden Chest"),contents=[get_item("ironhide_potion"),get_item("healing_potion_with_magic")]),
            Passage(("water", "Waterfall Clearing"),destination_id="waterfall"),
        ]
    ),
    "lumin": Room(
        name=("celestial", "Lumin"),
        room_contents=[
            Campfire(("heat","Central Bonfire")),
            get_entity("young_child"),
            get_entity("tired_parent"),
            get_entity("wise_elder"),
            Passage(("wood", "Wooden Canoe"),destination_id="dark_lake"),
            SubmergedPassage(("water", "Lake Surface"),destination_id="lakeside_keep"),
        ]
    ),
    "maneaters_hollow": Room(
        name=("shadow", "Maneaters' Hollow"),
        ability_handler=AbilityHandler([Spawner([get_entity("maneater")],1,25,5)]),
        room_contents=[
            get_entity("maneater"),
            Passage(("shadow", "Eastern Crossroads"),destination_id="forest_crossroads"),
            Passage(("magic", "Western Temple"),destination_id="mystic_temple"),
        ]
    ),
    "mystic_temple": Room(
        name=("magic", "Mystic Temple"),
        ability_handler=AbilityHandler([Spawner([get_entity("temple_guardian")],1,25,5)]),
        room_contents=[
            get_entity("temple_guardian"),
            Passage(("shadow", "Eastern Hollow"),destination_id="maneaters_hollow"),
            LockedPassage(("iron", "Armory Door"),destination_id="ancient_armory",key_id="armory_key")
        ]
    ),
    "ancient_armory": Room(
        name=("iron", "Ancient Armory"),
        room_contents=[
            get_item("guardian_chestplate"),
            get_item("guardian_crystal"),
            Passage(("magic", "Temple"),destination_id="mystic_temple"),
        ]
    ),

}

map.update(shadowed_forest)

undersea_kingdom : dict[str:Room] = {
    "oceanic_promenade": Room(
        name=("water", "Oceanic Promenade"),
        ability_handler=AbilityHandler([get_ability("underwater_room")]),
        room_contents=[
            SubmergedPassage(("water", "Submerged Cavern"),destination_id="submerged_cavern"),
            SubmergedPassage(("water", "Bright Hall"),destination_id="undersea_hall"),
            get_entity("fishy_peasant")
        ]
    ),
    "lakeside_keep": Room(
        name=("water", "Lakeside Keep"),
        ability_handler=AbilityHandler([get_ability("underwater_room")]),
        room_contents=[
            SubmergedPassage(("water", "Lake Surface"),destination_id="dark_lake"),
            SubmergedPassage(("water", "Bright Hall"),destination_id="undersea_hall"),
            get_entity("fishy_merchant")
        ]
    ),
    "undersea_hall": Room(
        name=("water", "Undersea Hall"),
        ability_handler=AbilityHandler([get_ability("underwater_room")]),
        room_contents=[
            Campfire(utility.alternate_colors("Underwater Flame",["heat","water"])),
            SubmergedPassage(("water", "Promenade"),destination_id="oceanic_promenade"),
            SubmergedPassage(("water", "Lakeside Keep"),destination_id="lakeside_keep"),
            SubmergedPassage(("water", "Waterlogged Throne"),destination_id="illuminated_throne"),
            get_entity("fishy_noble")
        ]
    ),
    "illuminated_throne": Room(
        name=("water", "Illuminated Throne"),
        ability_handler=AbilityHandler([get_ability("underwater_room")]),
        room_contents=[
            SubmergedPassage(("water", "Main Hall"),destination_id="undersea_hall"),
            get_entity("coral_king")
        ]
    ),
}

map.update(undersea_kingdom)

# systems.save_system.create_folder(systems.save_system.map_dir_name)
# systems.save_system.save_map("standard", map)