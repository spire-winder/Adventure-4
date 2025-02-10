from classes.interactable import Room
from classes.interactable import Passage
from classes.interactable import Item
from classes.interactable import Player
import systems.save_system

standard_map : dict = {
    "starting_room": Room("Starting room", [Player("Player Name"), Passage(("stone", u"Stone door"),"stone_room"), Passage(("iron",u"Iron door"),"iron_room"), Item(("wood", u"Wooden Sword"))]),
    "stone_room": Room(("stone", u"Stone Room"), [Passage(("wood", u"Wooden door"),"starting_room"), Passage(("iron",u"Iron door"),"iron_room"), Item(("magic", "Glyph-covered arm")), Item(("wood", u"Wooden Shield"))]),
    "iron_room": Room(("iron", u"Iron Room"), [Passage(("stone", u"Stone door"),"stone_room"), Passage(("wood", u"Wooden door"),"starting_room"), Item(("magic", u"Dragon Dreams"))]),
}

systems.save_system.create_folder(systems.save_system.map_dir_name)
systems.save_system.save_map("standard", standard_map)