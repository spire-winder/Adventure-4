from classes.interactable import *
from classes.actions import *
from data.abilities import *
import copy

items : dict[str:Item] = {
    
}

wooden_items : dict[str:Item] = {
    "wooden_sword":MeleeWeapon(
        name=("wood","Wooden Sword"),
        attackeffect=DamageEvent(damage=6, damage_type="slashing"),
        price=2,
        durability=0.7
    ),
    "wooden_bo":MeleeWeapon(
        name=("wood","Wooden Bo"),
        attackeffect=RepeatEvent(DamageEvent(damage=4, damage_type="bashing"),2),
        price=2
    ),
    "wooden_axe":MeleeWeapon(
        name=("wood","Wooden Axe"),
        attackeffect=
            EffectSequence([
                DamageEvent(damage=5, damage_type="slashing"),
                ProbabilityEvent(AddAbilityEffect("target", Status(get_ability("stun"),3)),0.25)
            ]),
        price=2
    ),
    "wooden_shield":Equipment(
        name=("wood","Wooden Shield"),
        ability_handler=AbilityHandler([Armor("armor",None,1)]),
        slot="Offhand",
        price=2
    ),
    "wooden_dagger":Equipment(
        name=("wood","Wooden Dagger"),
        ability_handler=AbilityHandler([SelectiveBuff("meleebuff",None,get_ability("melee"),1)]),
        slot="Offhand",
        price=2
    ),
    "leather_helmet":Equipment(
        name=("wood","Leather Helmet"),
        ability_handler=AbilityHandler([Armor("armor",None,1)]),
        slot="Helmet",
        price=2
    ),
    "leather_armor":Equipment(
        name=("wood","Leather Armor"),
        ability_handler=AbilityHandler([Armor("armor",None,1)]),
        slot="Armor",
        price=2
    ),
    "leather_boots":Equipment(
        name=("wood","Leather Boots"),
        ability_handler=AbilityHandler([Armor("armor",None,1)]),
        slot="Boots",
        price=2
    ),
    "wooden_ring":Equipment(
        name=("wood","Wooden Ring"),
        ability_handler=AbilityHandler([SelectiveArmor("magicarmor", "Magic Armor", "arcane", 2)]),
        slot="Ring",
        price=2
    ),
}

items.update(wooden_items)

rusty_items : dict[str:Item] = {
    "rusty_sword":MeleeWeapon(
        name=[("rust","Rusty"),("iron"," Sword")],
        attackeffect=DamageEvent(damage=8, damage_type="slashing"),
        durability=0.75,
        price=4
    ),
    "rusty_staff":MeleeWeapon(
        name=[("rust","Rusty"),("iron"," Staff")],
        attackeffect=RepeatEvent(DamageEvent(damage=5, damage_type="bashing"),2),
        durability=0.75,
        price=4
    ),
    "rusty_axe":MeleeWeapon(
        name=[("rust","Rusty"),("iron"," Axe")],
        attackeffect=
            EffectSequence([
                DamageEvent(damage=7, damage_type="slashing"),
                ProbabilityEvent(AddAbilityEffect("target", Status(get_ability("stun"),3)),0.25)
            ]),
        durability=0.75,
        price=4
    ),
    "iron_shield":Equipment(
        name=("iron","Iron Shield"),
        ability_handler=AbilityHandler([SelectiveArmor("magicarmor", "Magic Armor", "bashing", 4)]),
        slot="Offhand",
        price=4
    ),
    "iron_shiv":Equipment(
        name=("iron","Iron Shiv"),
        ability_handler=AbilityHandler([SelectiveBuff("meleebuff",None,get_ability("melee"),2)]),
        slot="Offhand",
        price=4
    ),
    "iron_helmet":Equipment(
        name=("iron","Iron Helmet"),
        ability_handler=AbilityHandler([Armor("armor",None,2)]),
        slot="Helmet",
        price=4
    ),
    "iron_armor":Equipment(
        name=("iron","Iron Armor"),
        ability_handler=AbilityHandler([Armor("armor",None,2)]),
        slot="Armor",
        price=4
    ),
    "iron_boots":Equipment(
        name=("iron","Iron Boots"),
        ability_handler=AbilityHandler([Armor("armor",None,2)]),
        slot="Boots",
        price=4
    ),
    "iron_ring":Equipment(
        name=("iron","Iron Ring"),
        ability_handler=AbilityHandler([SelectiveArmor("magicarmor", "Magic Armor", "slashing", 4)]),
        slot="Ring",
        price=4
    ),
}

items.update(rusty_items)


iron_items : dict[str:Item] = {
    "iron_sword":MeleeWeapon(
        name=("iron","Iron Sword"),
        attackeffect=DamageEvent(damage=10, damage_type="slashing"),
        price=5
    ),
    "iron_bo":MeleeWeapon(
        name=("iron","Iron Staff"),
        attackeffect=RepeatEvent(DamageEvent(damage=7, damage_type="bashing"),2),
        price=5
    ),
    "iron_axe":MeleeWeapon(
        name=("iron","Iron Axe"),
        attackeffect=
            EffectSequence([
                DamageEvent(damage=8, damage_type="slashing"),
                ProbabilityEvent(AddAbilityEffect("target", Status(get_ability("stun"),5)),0.5)
            ]),
        price=5
    ),
    "iron_shield":Equipment(
        name=("iron","Iron Shield"),
        ability_handler=AbilityHandler([SelectiveArmor("magicarmor", "Magic Armor", "bashing", 4)]),
        slot="Offhand",
        price=5
    ),
    "iron_shiv":Equipment(
        name=("iron","Iron Shiv"),
        ability_handler=AbilityHandler([SelectiveBuff("meleebuff",None,get_ability("melee"),2)]),
        slot="Offhand",
        price=5
    ),
    "iron_helmet":Equipment(
        name=("iron","Iron Helmet"),
        ability_handler=AbilityHandler([Armor("armor",None,2)]),
        slot="Helmet",
        price=5
    ),
    "iron_armor":Equipment(
        name=("iron","Iron Armor"),
        ability_handler=AbilityHandler([Armor("armor",None,2)]),
        slot="Armor",
        price=5
    ),
    "iron_boots":Equipment(
        name=("iron","Iron Boots"),
        ability_handler=AbilityHandler([Armor("armor",None,2)]),
        slot="Boots",
        price=5
    ),
    "iron_ring":Equipment(
        name=("iron","Iron Ring"),
        ability_handler=AbilityHandler([SelectiveArmor("magicarmor", "Magic Armor", "slashing", 4)]),
        slot="Ring",
        price=5
    ),
}

items.update(iron_items)

magic_items : dict[str:Item] = {
    "magic_sword":MeleeWeapon(
        name=("magic","Magic Sword"),
        attackeffect=EffectSequence([DamageEvent(damage=8,damage_type="slashing"),DamageEvent(damage=8,damage_type="arcane")]),
        price=8
    ),
    "magic_staff":MagicWeapon(
        name=("magic","Magic Staff"),
        attackeffect=RepeatEvent(DamageEvent(damage=8,damage_type="arcane",armor_penetrate=2),2),
        mana_cost=5,
        price=8
    ),
    "magic_axe":MeleeWeapon(
        name=("magic","Magic Axe"),
        attackeffect=
            EffectSequence([
                DamageEvent(damage=10,damage_type="arcane"),
                ProbabilityEvent(AddAbilityEffect("target", Status(get_ability("stun"),5)),0.75)
            ]),
        price=8
    ),
    "magic_shield":Equipment(
        name=("magic","Magic Shield"),
        ability_handler=AbilityHandler([SelectiveArmor("magedefense", "Mage Defense", "arcane", 6)]),
        slot="Offhand",
        price=8
    ),
    "clarity_crystal":Equipment(
        name=("magic","Clarity Crystal"),
        ability_handler=AbilityHandler([SelectiveBuff("magicbuff","Magical Focus",get_ability("magic"),2),Armor("armor",None,2)]),
        slot="Offhand",
        price=8
    ),
    "magic_helmet":Equipment(
        name=("magic","Magic Helmet"),
        ability_handler=AbilityHandler([Armor("armor",None,5)]),
        slot="Helmet",
        price=8
    ),
    "magic_armor":Equipment(
        name=("magic","Magic Armor"),
        ability_handler=AbilityHandler([Armor("armor",None,5)]),
        slot="Armor",
        price=8
    ),
    "magic_boots":Equipment(
        name=("magic","Magic Boots"),
        ability_handler=AbilityHandler([Armor("armor",None,5)]),
        slot="Boots",
        price=8
    ),
    "magic_ring":Equipment(
        name=("magic","Magic Ring"),
        ability_handler=AbilityHandler([DamageTypeBuff("magic_aura","Aura","arcane",3)]),
        slot="Ring",
        price=8
    ),
}

items.update(magic_items)

magic_weapon_items : dict[str:Item] = {
    "fire_tome":MagicWeapon(
        name=("heat","Fire Tome"),
        attackeffect=DamageEvent(damage=15,damage_type="heat"),
        mana_cost=10,
        price=10
    ),
    "poison_tome":MagicWeapon(
        name=("toxic","Poison Tome"),
        attackeffect=EffectSequence([
            DamageEvent(damage=5,damage_type="toxic"),
            AddAbilityEffect("target", Status(get_ability("poison"),3))
        ]),
        mana_cost=10,
        price=10
    ),
    "lightning_tome":MagicWeapon(
        name=("lightning","Lightning Tome"),
        attackeffect=EffectSequence([
            DamageEvent(damage=10,damage_type="lightning"),
            AddAbilityEffect("target", Status(get_ability("stun"),5))
        ]),
        mana_cost=10,
        price=10
    ),
    "mega_death":MagicWeapon(
        name=("shadow","Mega Death"),
        attackeffect=EffectSequence([
            DamageEvent(damage=110,damage_type="shadow"),
            AddAbilityEffect("target", Status(get_ability("stun"),5))
        ]),
        mana_cost=1,
        price=10
    )
}

items.update(magic_weapon_items)

consumeable_items : dict[str:Item] = {
    "sharpening_stone":Sharpener(
        name=("iron","Sharpening Stone"),
        ability_handler=AbilityHandler([MultiUse(3)]),
        useeffect=SharpenEvent("item", "target", 0.5),
        price=2
    ),
    "healing_potion":Potion(
        name=("healing","Healing Potion"),
        ability_handler=AbilityHandler([SingleUse()]),
        useeffect=HealEvent("item","user",10),
        price=2
    ),
    "restoration_potion":Potion(
        name=("magic","Restoration Potion"),
        ability_handler=AbilityHandler([SingleUse()]),
        useeffect=RestoreMPEvent("item","user",20),
        price=4
    ),
    "healing_potion_with_magic":Potion(
        name=utility.alternate_colors("Infused Healing Potion",["healing"*2,"magic"*2]),
        ability_handler=AbilityHandler([ManaCost("manacost","Mana Cost", 5),SingleUse()]),
        useeffect=HealEvent("item","user",15),
        price=4
    ),
    "regen_potion":Potion(
        name=("healing","Regeneration Potion"),
        ability_handler=AbilityHandler([SingleUse()]),
        useeffect=AddAbilityEffect("user",Status(get_ability("regen"),5)),
        price=4
    ),
    "ironhide_potion":Potion(
        name=("iron","Ironhide Potion"),
        ability_handler=AbilityHandler([SingleUse()]),
        useeffect=AddAbilityEffect("user",Status(Armor("iron_hide", ("iron", "Ironhide"),3),5)),
        price=4
    )
}

items.update(consumeable_items)

food_items : dict[str:Item] = {
    "roast_chicken":Food(
        name=("meat", "Roast Chicken"),
        ability_handler=AbilityHandler([SingleUse()]),
        foodeffect=HealEvent("item","user",15),
        price=2
    ),
    "roast_pork":Food(
        name=("meat", "Roast Pork"),
        ability_handler=AbilityHandler([SingleUse()]),
        foodeffect=HealEvent("item","user",20),
        price=3
    ),
    "roast_beef":Food(
        name=("meat", "Roast Beef"),
        ability_handler=AbilityHandler([SingleUse()]),
        foodeffect=HealEvent("item","user",25),
        price=4
    ),
    "bone_marrow_stew":Food(
        name=("food", "Bone Marrow Stew"),
        ability_handler=AbilityHandler([SingleUse()]),
        foodeffect=EffectSequence([
            HealEvent("item","user",20),
            AddAbilityEffect("user",Status(Armor("strong_bones", ("iron", "Strong Bones"),2),20))
        ]),
        price=5
    )
}

items.update(food_items)

enemy_items : dict[str:Item] = {
    "magic_barbs":MeleeWeapon(
        name=("magic","Magic Barbs"),
        drop_chance=0,
        attackeffect=DamageEvent(damage=7,damage_type="arcane",armor_penetrate=2)
    ),
    "eye_whip":MeleeWeapon(
        name=("meat","Eye Whip"),
        drop_chance=0,
        attackeffect=DamageEvent(damage=5,damage_type="bashing",armor_penetrate=3)
    ),
    "tooth":MeleeWeapon(
        name=("meat","Tooth"),
        drop_chance=0.2,
        attackeffect=DamageEvent(damage=2,damage_type="slashing",armor_penetrate=1)
    ),
    "magic_tooth":MeleeWeapon(
        name=("magic","Arcane Tooth"),
        drop_chance=0.1,
        attackeffect=DamageEvent(damage=4,damage_type="arcane",armor_penetrate=2)
    ),
    "shadow_tooth":MeleeWeapon(
        name=("shadow","Shadow Tooth"),
        drop_chance=0.1,
        attackeffect=DamageEvent(damage=6,damage_type="shadow")
    ),
    "rusty_spatula":MeleeWeapon(
        name=[("rust","Rusty"),("iron"," Spatula")],
        attackeffect=DamageEvent(damage=10, damage_type="bashing"),
        durability=0.8,
        drop_chance=0.3,
        price=6
    ),
    "chef_hat":Equipment(
        name="Chef's Hat",
        ability_handler=AbilityHandler([Armor("armor",None,2),OnEatEffect("eat_mp","Home Cooking",RestoreMPEvent("item","user",5))]),
        slot="Helmet",
        drop_chance=0.3,
        price=8
    ),
    "chef_apron":Equipment(
        name="Chef's Apron",
        ability_handler=AbilityHandler([Armor("armor",None,2),OnEatEffect("eat_hp","Ancestral Recipe",HealEvent("item","user",5))]),
        slot="Armor",
        drop_chance=0.3,
        price=8
    ),
}

items.update(enemy_items)

tools : dict[str:Item] = {
    "wooden_key":Key(("wood", "Wooden Key"),key_id="wooden_key"),
    "wooden_shovel":Tool(
        ("wood", "Wooden Shovel"),
        ability_handler=AbilityHandler([Sharpness(1,0.6)]),
        tool_type="Shovel",
        tool_strength=1,
        price=2
    ),
    "iron_shovel":Tool(
        ("iron", "Iron Shovel"),
        ability_handler=AbilityHandler([Sharpness()]),
        tool_type="Shovel",
        tool_strength=5,
        price=4
    ),
    "diving_gear":Equipment(
        ("water","Diving Gear"),
        ability_handler=AbilityHandler([Ability("water_breathing",("water", "Water Breathing"),"Allows you to breathe underwater.")]),
        slot="Helmet",
        price=12
    )
}

items.update(tools)

for x in items:
    items[x].id = x

def get_item(item_id : str) -> Item:
    return copy.deepcopy(items[item_id])