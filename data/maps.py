from classes.interactable import *
from classes.actions import *
from classes.states import *
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
            "Weapon":None
        })
    ), 
    StatHandler({"HP":HPContainer(20,20)}),
    IdleState()
)

magi_dragon : StateEntity = StateEntity(
    ("magic","Dragon"), 
    AbilityHandler([
        Armor("Dragon Scales", 2)
    ]),
    Inventory(
        EquipmentHandler({
            "Weapon":Weapon(
                name=("fire", "Fire Breath"),
                effect=EffectSelectorTarget(DamageEvent(10)),
                drop_chance=0.0
            )
        })
    ), 
    StatHandler({"HP":HPContainer(60,60)}),
    IdleState()
)

standard_map : dict = {
    "starting_room": Room(
        "Starting room", 
        AbilityHandler(), 
        [
        copy.deepcopy(player),
        Passage(("stone", u"Stone door"),AbilityHandler(),"stone_room"),
        Passage(("iron",u"Iron door"),AbilityHandler(),"iron_room"),
        Weapon(
            name=("wood", u"Wooden Sword"),
            effect=EffectSelectorTarget(DamageEvent(5))),
        Weapon(
            name=("wood", u"Wooden Bo"),
            effect=EffectSelectorTarget(RepeatEvent(DamageEvent(7),2))),
        copy.deepcopy(goblin_with_iron_sword)
    ]),
    "stone_room": Room(("stone", u"Stone Room"),AbilityHandler(), [
        Passage(("wood", u"Wooden door"),AbilityHandler(),"starting_room"),
        Passage(("iron",u"Iron door"),AbilityHandler(),"iron_room"),
        Weapon(
            name=("magic", "Glyph-covered arm"), 
            effect=EffectSelectorTarget(DamageEvent(10))),
        Equipment(("wood", u"Wooden Shield"), ability_handler=AbilityHandler([Armor(None, 5)]),slot="Offhand")
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