from classes.interactable import *
import systems.save_system

standard_map : dict = {
    "starting_room": Room("Starting room", [Player("Player Name", Inventory(EquipmentHandler({"Weapon":None, "Offhand":None}))), Passage(("stone", u"Stone door"),"stone_room"), Passage(("iron",u"Iron door"),"iron_room"), Equipment(("wood", u"Wooden Sword"), "Weapon"), Entity(("goblin","Goblin"))]),
    "stone_room": Room(("stone", u"Stone Room"), [Passage(("wood", u"Wooden door"),"starting_room"), Passage(("iron",u"Iron door"),"iron_room"), Equipment(("magic", "Glyph-covered arm"), "Weapon"), Equipment(("wood", u"Wooden Shield"), "Offhand")]),
    "iron_room": Room(("iron", u"Iron Room"), [Passage(("stone", u"Stone door"),"stone_room"), Passage(("wood", u"Wooden door"),"starting_room"), Item(("magic", u"Dragon Dreams")), Entity(("magic","Dragon"))]),
}

systems.save_system.create_folder(systems.save_system.map_dir_name)
systems.save_system.save_map("standard", standard_map)