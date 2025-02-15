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
    StatHandler({"HP":HPContainer(50,50)})
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
    StatHandler({"HP":HPContainer(20,20)})
)

magi_dragon : StateEntity = StateEntity(
    ("magic","Dragon"), 
    AbilityHandler([
        Armor("Dragon Scales", 2)
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
    StatHandler({"HP":HPContainer(60,60)})
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
        Weapon(("wood", u"Wooden Bo"), AbilityHandler(),EffectSelectorTarget(RepeatEvent(DamageEvent(7),2))),
        copy.deepcopy(goblin_with_iron_sword)
    ]),
    "stone_room": Room(("stone", u"Stone Room"),AbilityHandler(), [
        Passage(("wood", u"Wooden door"),AbilityHandler(),"starting_room"),
        Passage(("iron",u"Iron door"),AbilityHandler(),"iron_room"),
        Weapon(("magic", "Glyph-covered arm"), AbilityHandler(), EffectSelectorTarget(DamageEvent(10))),
        Equipment(("wood", u"Wooden Shield"), AbilityHandler([Armor(None, 5)]),"Offhand")
    ]),
    "iron_room": Room(("iron", u"Iron Room"), AbilityHandler(),[
        Passage(("stone", u"Stone door"),AbilityHandler(),"stone_room"), 
        Passage(("wood", u"Wooden door"),AbilityHandler(),"starting_room"), 
        Item(("magic", u"Dragon Dreams"),AbilityHandler(),), 
        Food("Roast chicken", AbilityHandler(), EffectSelectorSelf(EffectSequence([HealEvent(20), EffectSelectorPredefinedTarget(AddAbilityEffect(),Status(Armor("Well Fed",2),12))]))),
        Campfire(("fire","Campfire")),
        copy.deepcopy(magi_dragon)
    ]),
}

systems.save_system.create_folder(systems.save_system.map_dir_name)
systems.save_system.save_map("standard", standard_map)