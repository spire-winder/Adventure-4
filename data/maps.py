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
            "Offhand":None
        })),
    StatHandler({"HP":HPContainer(50,50)})
)

standard_map : dict = {
    "starting_room": Room(
        "Starting room", 
        AbilityHandler(), 
        [
            copy.deepcopy(player),
            get_enemy("goblin_1"),
            get_enemy("goblin_2"),
            get_enemy("goblin_boss"),
            get_item("wooden_sword"),
            get_item("wooden_sword")
        ]
    ),
}

systems.save_system.create_folder(systems.save_system.map_dir_name)
systems.save_system.save_map("standard", standard_map)