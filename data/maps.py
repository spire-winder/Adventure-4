from classes.interactable import *
from classes.actions import *
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
    StatHandler({"HP":50})
)

goblin_with_iron_sword : StateEntity = StateEntity(
    ("goblin","Goblin"), 
    AbilityHandler(),
    Inventory(
        EquipmentHandler({
            "Weapon":Weapon(
                ("iron", "Iron Sword"), 
                AbilityHandler(),
                EffectSelectorTarget(DamageEvent(5))
            )
        })
    ), 
    StatHandler({"HP":20})
)

magi_dragon : StateEntity = StateEntity(
    ("magic","Dragon"), 
    AbilityHandler([
        AbilityName("Dragon Scales", Armor(2))
    ]),
    Inventory(
        EquipmentHandler({
            "Weapon":Weapon(
                ("fire", "Fire Breath"), 
                AbilityHandler(),
                EffectSelectorTarget(DamageEvent(10))
            )
        })
    ), 
    StatHandler({"HP":60})
)

standard_map : dict = {
    "starting_room": Room(
        "Starting room", 
        AbilityHandler(), 
        [
        copy.deepcopy(player),
        Passage(("stone", u"Stone door"),AbilityHandler(),"stone_room"),
        Passage(("iron",u"Iron door"),AbilityHandler(),"iron_room"),
        Weapon(("wood", u"Wooden Sword"), AbilityHandler(),EffectSelectorTarget(DamageEvent(5))),
        copy.deepcopy(goblin_with_iron_sword)
    ]),
    "stone_room": Room(("stone", u"Stone Room"),AbilityHandler(), [
        Passage(("wood", u"Wooden door"),AbilityHandler(),"starting_room"),
        Passage(("iron",u"Iron door"),AbilityHandler(),"iron_room"),
        Weapon(("magic", "Glyph-covered arm"), AbilityHandler(), EffectSelectorTarget(DamageEvent(10))),
        Equipment(("wood", u"Wooden Shield"), AbilityHandler([Armor(5)]),"Offhand")
    ]),
    "iron_room": Room(("iron", u"Iron Room"), AbilityHandler(),[
        Passage(("stone", u"Stone door"),AbilityHandler(),"stone_room"), 
        Passage(("wood", u"Wooden door"),AbilityHandler(),"starting_room"), 
        Item(("magic", u"Dragon Dreams"),AbilityHandler(),), 
        copy.deepcopy(magi_dragon)
    ]),
}

systems.save_system.create_folder(systems.save_system.map_dir_name)
systems.save_system.save_map("standard", standard_map)