from classes.rooms import Room
from classes.roomobjects import Passage
from classes.roomobjects import Item
from classes.roomobjects import Player
import systems.save_system

standard_map : dict = {
    "starting_room": Room("Starting room", [Player("Player Name"), Passage(("stone", u"Stone door"),"stone_room"), Passage(("iron",u"Iron door"),"iron_room"), Item(("wood", u"Wooden Sword"))]),
    "stone_room": Room(("stone", u"Stone Room"), [Passage(("wood", u"Wooden door"),"starting_room"), Passage(("iron",u"Iron door"),"iron_room"), Item(("magic", "Glyph-covered arm")), Item(("wood", u"Wooden Shield"))]),
    "iron_room": Room(("iron", u"Iron Room"), [Passage(("stone", u"Stone door"),"stone_room"), Passage(("wood", u"Wooden door"),"starting_room"), Item(("magic", u"Dragon Dreams"))]),
}

systems.save_system.save_file_path = "starting_map.pkl"
systems.save_system.save_game(standard_map)