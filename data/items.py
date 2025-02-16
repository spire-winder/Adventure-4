from classes.interactable import *
from classes.actions import *
from data.abilities import *
import copy

items : dict[str:Item] = {
    
}

wooden_items : dict[str:Item] = {
    "wooden_sword":MeleeWeapon(
        name=("wood","Wooden Sword"),
        effect=DamageEvent(6, "slashing")
    ),
    "wooden_bo":MeleeWeapon(
        name=("wood","Wooden Bo"),
        effect=RepeatEvent(DamageEvent(4, "bashing"),2)
    ),
    "wooden_axe":MeleeWeapon(
        name=("wood","Wooden Axe"),
        effect=
            EffectSequence([
                DamageEvent(5, "slashing"),
                ProbabilityEvent(EffectSelectorPredefinedSource(AddAbilityEffect(), Status(get_ability("stun"),3)),0.25)
            ]),
    ),
    "wooden_shield":Equipment(
        name=("wood","Wooden Shield"),
        ability_handler=AbilityHandler([Armor("armor",None,1)]),
        slot="Offhand"
    ),
    "wooden_dagger":Equipment(
        name=("wood","Wooden Dagger"),
        ability_handler=AbilityHandler([SelectiveBuff("meleebuff",None,get_ability("melee"),1)]),
        slot="Offhand"
    ),
    "leather_helmet":Equipment(
        name=("wood","Leather Helmet"),
        ability_handler=AbilityHandler([Armor("armor",None,1)]),
        slot="Helmet"
    ),
    "leather_armor":Equipment(
        name=("wood","Leather Armor"),
        ability_handler=AbilityHandler([Armor("armor",None,1)]),
        slot="Armor"
    ),
    "leather_boots":Equipment(
        name=("wood","Leather Boots"),
        ability_handler=AbilityHandler([Armor("armor",None,1)]),
        slot="Boots"
    ),
    "wooden_ring":Equipment(
        name=("wood","Wooden Ring"),
        ability_handler=AbilityHandler([SelectiveArmor("magicarmor", "Magic Armor", "arcane", 2)]),
        slot="Ring"
    ),
}

items.update(wooden_items)

iron_items : dict[str:Item] = {
    "iron_sword":MeleeWeapon(
        name=("iron","Iron Sword"),
        effect=DamageEvent(10, "slashing")
    ),
    "iron_bo":MeleeWeapon(
        name=("iron","Iron Staff"),
        effect=RepeatEvent(DamageEvent(7, "bashing"),2)
    ),
    "iron_axe":MeleeWeapon(
        name=("iron","Iron Axe"),
        effect=
            EffectSequence([
                DamageEvent(8, "slashing"),
                ProbabilityEvent(EffectSelectorPredefinedSource(AddAbilityEffect(), Status(get_ability("stun"),5)),0.5)
            ]),
    ),
    "iron_shield":Equipment(
        name=("iron","Iron Shield"),
        ability_handler=AbilityHandler([SelectiveArmor("magicarmor", "Magic Armor", "bashing", 4)]),
        slot="Offhand"
    ),
    "iron_shiv":Equipment(
        name=("iron","Iron Shiv"),
        ability_handler=AbilityHandler([SelectiveBuff("meleebuff",None,get_ability("melee"),2)]),
        slot="Offhand"
    ),
    "iron_helmet":Equipment(
        name=("iron","Iron Helmet"),
        ability_handler=AbilityHandler([Armor("armor",None,2)]),
        slot="Helmet"
    ),
    "iron_armor":Equipment(
        name=("iron","Iron Armor"),
        ability_handler=AbilityHandler([Armor("armor",None,2)]),
        slot="Armor"
    ),
    "iron_boots":Equipment(
        name=("iron","Iron Boots"),
        ability_handler=AbilityHandler([Armor("armor",None,2)]),
        slot="Boots"
    ),
    "iron_ring":Equipment(
        name=("iron","Iron Ring"),
        ability_handler=AbilityHandler([SelectiveArmor("magicarmor", "Magic Armor", "slashing", 4)]),
        slot="Ring"
    ),
}

items.update(iron_items)

magic_items : dict[str:Item] = {
    "magic_sword":MeleeWeapon(
        name=("magic","Magic Sword"),
        effect=EffectSequence([DamageEvent(8,"slashing"),DamageEvent(8,"arcane")])
    ),
    "magic_staff":MagicWeapon(
        name=("magic","Magic Staff"),
        effect=RepeatEvent(DamageEvent(5,"arcane",3),3),
        mana_cost=5
    ),
    "magic_axe":MeleeWeapon(
        name=("magic","Magic Axe"),
        effect=
            EffectSequence([
                DamageEvent(10,"arcane"),
                ProbabilityEvent(EffectSelectorPredefinedSource(AddAbilityEffect(), Status(get_ability("stun"),5)),0.75)
            ]),
    ),
    "magic_shield":Equipment(
        name=("magic","Magic Shield"),
        ability_handler=AbilityHandler([SelectiveArmor("magedefense", "Mage Defense", "arcane", 6)]),
        slot="Offhand"
    ),
    "clarity_crystal":Equipment(
        name=("magic","Clarity Crystal"),
        ability_handler=AbilityHandler([SelectiveBuff("magicbuff","Magical Focus",get_ability("magic"),2),Armor("armor",None,2)]),
        slot="Offhand"
    ),
    "magic_helmet":Equipment(
        name=("magic","Magic Helmet"),
        ability_handler=AbilityHandler([Armor("armor",None,5)]),
        slot="Helmet"
    ),
    "magic_armor":Equipment(
        name=("magic","Magic Armor"),
        ability_handler=AbilityHandler([Armor("armor",None,5)]),
        slot="Armor"
    ),
    "magic_boots":Equipment(
        name=("magic","Magic Boots"),
        ability_handler=AbilityHandler([Armor("armor",None,5)]),
        slot="Boots"
    ),
    "magic_ring":Equipment(
        name=("magic","Magic Ring"),
        ability_handler=AbilityHandler([DamageTypeBuff("magic_aura","Aura","arcane",3)]),
        slot="Ring"
    ),
}

items.update(magic_items)

magic_weapon_items : dict[str:Item] = {
    "fire_tome":MagicWeapon(
        name=("fire","Fire Tome"),
        effect=DamageEvent(15,"fire"),
        mana_cost=10
    ),
    "poison_tome":MagicWeapon(
        name=("poison","Poison Tome"),
        effect=EffectSequence([DamageEvent(5,"poison"),EffectSelectorPredefinedSource(AddAbilityEffect(), Status(get_ability("poison"),3))]),
        mana_cost=10
    ),
    "lightning_tome":MagicWeapon(
        name=("lightning","Lightning Tome"),
        effect=EffectSequence([DamageEvent(10,"lightning"),EffectSelectorPredefinedSource(AddAbilityEffect(), Status(get_ability("stun"),5))]),
        mana_cost=10
    ),
    "ultra_death":MeleeWeapon(
        name=("lightning","Lightning Tome"),
        effect=DamageEvent(110,"lightning"),
    ),
}

items.update(magic_weapon_items)

consumeable_items : dict[str:Item] = {
    "sharpening_stone":Sharpener(
        name="Sharpening Stone",
        ability_handler=AbilityHandler([MultiUse(3)]),
        effect=SharpenEvent(0.5)
    ),
    "healing_potion":Potion(
        name=("healing","Healing Potion"),
        ability_handler=AbilityHandler([SingleUse()]),
        effect=HealEvent(20)
    ),
    "healing_potion_with_magic":Potion(
        name=utility.alternate_colors("Infused Healing Potion",["healing"*2,"magic"*2]),
        ability_handler=AbilityHandler([ManaCost("manacost","Mana Cost", 5),SingleUse()]),
        effect=HealEvent(50)
    ),
    "regen_potion":Potion(
        name=("healing","Regeneration Potion"),
        ability_handler=AbilityHandler([SingleUse()]),
        effect=EffectSelectorPredefinedSource(AddAbilityEffect(), Status(get_ability("regen"),10))
    ),
    "ironhide_potion":Potion(
        name=("iron","Ironhide Potion"),
        ability_handler=AbilityHandler([SingleUse()]),
        effect=EffectSelectorPredefinedSource(AddAbilityEffect(), Status(Armor("iron_hide", ("iron", "Ironhide"),8),10))
    )
}

items.update(consumeable_items)

food_items : dict[str:Item] = {
    "roast_chicken":Food(
        name=("meat", "Roast Chicken"),
        effect=HealEvent(15)
    ),
    "roast_pork":Food(
        name=("meat", "Roast Pork"),
        effect=HealEvent(20)
    ),
    "roast_beef":Food(
        name=("meat", "Roast Beef"),
        effect=HealEvent(25)
    ),
    "bone_marrow_stew":Food(
        name=("food", "Bone Marrow Stew"),
        effect=EffectSequence([
            HealEvent(20),
            EffectSelectorPredefinedSource(AddAbilityEffect(), Status(Armor("strong_bones", ("iron", "Strong Bones"),2),20))
        ])
    )
}

items.update(food_items)

enemy_items : dict[str:Item] = {
    "magic_barbs":MeleeWeapon(
        name=("magic","Magic Barbs"),
        drop_chance=0,
        effect=DamageEvent(7,"arcane",2)
    ),
    "eye_whip":MeleeWeapon(
        name=("meat","Eye Whip"),
        drop_chance=0,
        effect=DamageEvent(5,"bashing",3)
    )
}

items.update(enemy_items)

def get_item(item_id : str) -> Item:
    return copy.deepcopy(items[item_id])