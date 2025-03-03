from classes.interactable import *
from classes.actions import *
from data.abilities import *
import copy

items : dict[str:Item] = {
    
}

ruins_of_the_sun_items : dict[str:Item] = {
    "wooden_sword":MeleeWeapon(
        name=("wood","Wooden Sword"),
        attackeffect=DamageEvent(damage=6, damage_type="slashing"),
        drop_chance=0.3,
        price=2,
        durability=0.9,
    ),
    "wooden_bo":MeleeWeapon(
        name=("wood","Wooden Bo"),
        attackeffect=RepeatEvent(DamageEvent(damage=4, damage_type="bashing"),2),
        drop_chance=0.3,
        durability=0.9,
        price=2
    ),
    "wooden_axe":MeleeWeapon(
        name=("wood","Wooden Axe"),
        attackeffect=
            EffectSequence([
                DamageEvent(damage=5, damage_type="slashing"),
                ProbabilityEvent(AddAbilityEffect("target", Status(get_ability("stun"),3)),0.25)
            ]),
        drop_chance=0.3,
        price=2,
        durability=0.9,
    ),
    "wooden_sledge":MeleeWeapon(
        name=("wood","Wooden Sledge"),
        attackeffect=DamageEvent(damage=5, damage_type="bashing",armor_penetrate=2),
        drop_chance=0.3,
        price=2,
        durability=0.9,
    ),
    "wooden_key":Key(("wood", "Wooden Key"),key_id="wooden_key"),
    "wooden_shield":Equipment(
        name=("wood","Wooden Shield"),
        ability_handler=AbilityHandler([Armor("armor",None,1)]),
        drop_chance=0.3,
        slot="Offhand",
        price=2
    ),
    "rusty_sword":MeleeWeapon(
        name=[("rust","Rusty"),("iron"," Sword")],
        attackeffect=DamageEvent(damage=8, damage_type="slashing"),
        drop_chance=0.3,
        durability=0.9,
        price=4
    ),
    "rusty_staff":MeleeWeapon(
        name=[("rust","Rusty"),("iron"," Staff")],
        attackeffect=RepeatEvent(DamageEvent(damage=5, damage_type="bashing"),2),
        drop_chance=0.3,
        durability=0.9,
        price=4
    ),
    "rusty_axe":MeleeWeapon(
        name=[("rust","Rusty"),("iron"," Axe")],
        attackeffect=
            EffectSequence([
                DamageEvent(damage=7, damage_type="slashing"),
                ProbabilityEvent(AddAbilityEffect("target", Status(get_ability("stun"),3)),0.5)
            ]),
        drop_chance=0.3,
        durability=0.9,
        price=4
    ),
    "wooden_shovel":Tool(
        ("wood", "Wooden Shovel"),
        ability_handler=AbilityHandler([Sharpness(1,0.7)]),
        drop_chance=0.3,
        tool_type="Shovel",
        tool_strength=1,
        price=2
    ),
    "wooden_dagger":Equipment(
        name=("wood","Wooden Dagger"),
        ability_handler=AbilityHandler([SelectiveBuff("meleebuff",None,get_ability("melee"),1)]),
        drop_chance=0.3,
        slot="Offhand",
        price=2
    ),
    "greedling_flesh":Food(
        name=("meat", "Greedling Flesh"),
        ability_handler=AbilityHandler([SingleUse()]),
        foodeffect=EffectSequence([
            HealEvent("item","user",8)
        ]),
        drop_chance=0.6,
        price=2
    ),
    "raw_fish":Food(
        name=("water", "Raw Fish"),
        ability_handler=AbilityHandler([SingleUse()]),
        foodeffect=EffectSequence([
            HealEvent("item","user",10)
        ]),
        drop_chance=0.6,
        price=2
    )
}

items.update(ruins_of_the_sun_items)

shattered_ruins_items : dict[str:Item] = {
    "leather_helmet":Equipment(
        name=("wood","Leather Helmet"),
        ability_handler=AbilityHandler([Armor("armor",None,1)]),
        drop_chance=0.3,
        slot="Helmet",
        price=2
    ),
    "leather_armor":Equipment(
        name=("wood","Leather Armor"),
        ability_handler=AbilityHandler([Armor("armor",None,1)]),
        drop_chance=0.3,
        slot="Armor",
        price=2
    ),
    "leather_boots":Equipment(
        name=("wood","Leather Boots"),
        ability_handler=AbilityHandler([Armor("armor",None,1)]),
        drop_chance=0.3,
        slot="Boots",
        price=2
    ),
    "rusty_sledge":MeleeWeapon(
        name=[("rust","Rusty"),("iron"," Sledge")],
        attackeffect=DamageEvent(damage=6, damage_type="bashing",armor_penetrate=4),
        drop_chance=0.3,
        durability=0.9,
        price=4
    ),
    "rusty_pickaxe":MeleeTool(
        name=[("rust","Rusty"),("iron"," Pickaxe")],
        attackeffect=DamageEvent(damage=4, damage_type="slashing",armor_penetrate=-1),
        drop_chance=0.5,
        durability=0.9,
        price=4,
        tool_type="Pickaxe",
        tool_strength=2,
    ),
    "dynamite":Explosive(
        name=("heat","Dynamite"),
        ability_handler=AbilityHandler([SingleUse()]),
        drop_chance=0.5,
        price=4,
        tool_type="Pickaxe",
        tool_strength=3,
        attackeffect=AOEEffect(DamageEvent(damage=10, damage_type="heat",armor_penetrate=-1))
    ),
    "rusty_spatula":MeleeWeapon(
        name=[("rust","Rusty"),("iron"," Spatula")],
        attackeffect=DamageEvent(damage=12, damage_type="bashing"),
        durability=0.95,
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
    "mage_cloak":Equipment(
        name=("magic", "Mage Cloak"),
        ability_handler=AbilityHandler([Armor("armor",None,2),SelectiveBuff("manapower",("magic", "Manapower"),get_ability("magic"),2)]),
        slot="Armor",
        drop_chance=0.3,
        price=8
    ),
    "mage_boots":Equipment(
        name=("magic", "Mage Boots"),
        ability_handler=AbilityHandler([Armor("armor",None,2),ManaReduction("manabond",("magic", "Manabond"),2)]),
        slot="Boots",
        drop_chance=0.3,
        price=8
    ),
    "wooden_ring":Equipment(
        name=("wood","Wooden Ring"),
        ability_handler=AbilityHandler([SelectiveArmor("magicarmor", "Magic Armor", "arcane", 2)]),
        drop_chance=0.3,
        slot="Ring",
        price=2
    ),
    "clarity_crystal":Equipment(
        name=("magic","Clarity Crystal"),
        ability_handler=AbilityHandler([SelectiveBuff("magicbuff","Magical Focus",get_ability("magic"),2),Armor("armor",None,2)]),
        drop_chance=0.2,
        slot="Offhand",
        price=8
    ),
    "iron_helmet":Equipment(
        name=("iron","Iron Helmet"),
        ability_handler=AbilityHandler([Armor("armor",None,3)]),
        drop_chance=0.2,
        slot="Helmet",
        price=10
    ),
    "iron_armor":Equipment(
        name=("iron","Iron Armor"),
        ability_handler=AbilityHandler([Armor("armor",None,3)]),
        drop_chance=0.2,
        slot="Armor",
        price=10
    ),
    "iron_boots":Equipment(
        name=("iron","Iron Boots"),
        ability_handler=AbilityHandler([Armor("armor",None,3)]),
        drop_chance=0.2,
        slot="Boots",
        price=10
    ),
    "garden_key":Key(("wood", "Garden Key"),key_id="garden_key"),
    "small_rock":UsableWeapon(
        name=("stone","Small Rock"),
        ability_handler=AbilityHandler([SingleUse()]),
        drop_chance=0.9,
        useeffect=DamageEvent(damage=7,damage_type="bashing")
    ),
    "spiked_shield":Equipment(
        name=("iron","Spiked Shield"),
        ability_handler=AbilityHandler([SelectiveArmor("sturdy", ("iron", "Sturdy"), "slashing", 2),Reciprocate("spikes",("iron","Spikes"),DamageEvent("item","attacker",2,"slashing"))]),
        slot="Offhand",
        price=5
    ),
    "spiked_ring":Equipment(
        name=("iron","Spiked Ring"),
        ability_handler=AbilityHandler([SelectiveBuff("bloodsoaked", ("meat", "Bloodsoaked"), get_ability("melee"), 2),Reciprocate("spikes",("iron","Spikes"),DamageEvent("item","attacker",2,"slashing"))]),
        slot="Ring",
        price=5
    ),
}

items.update(shattered_ruins_items)

shadowed_forest_items : dict[str:Item] = {
    "frozen_helm":Equipment(
        name=("cold","Frozen Helm"),
        ability_handler=AbilityHandler([Armor("armor",None,5),DamageTypeBuff("freeze_aura1",("cold","Frozen Aura"),"cold",5),SelectiveArmor("freeze_aura2",None,"cold",5)]),
        slot="Helmet",
        price=12
    ),
    "guardian_chestplate":Equipment(
        name=utility.alternate_colors("Guardian Chestplate", ["magic","stone"]),
        ability_handler=AbilityHandler([Armor("armor",None,5),SelectiveArmor("ancient_armor1","Ancient Armor","arcane",3),SelectiveArmor("ancient_armor2",None,"heat",3)]),
        slot="Armor",
        price=12
    ),
    "waterforged_boots":Equipment(
        name=utility.alternate_colors("Waterforged Boots", ["water","magic"]),
        ability_handler=AbilityHandler([Armor("armor",None,5),EndOfTurnEffect("mp_restore",("magic", "Magic Restoration"),RestoreMPEvent("self","user",3))]),
        slot="Boots",
        price=12
    ),
    "waterforged_sledge":MeleeWeapon(
        name=[("water","Waterforged"),("iron"," Sledge")],
        attackeffect=EffectSequence([DamageEvent(damage=6, damage_type="bashing",armor_penetrate=4),DamageEvent(damage=6, damage_type="cold",armor_penetrate=4)]),
        durability=0.9,
        price=15
    ),
    "guardian_crystal":Equipment(
        name=utility.alternate_colors("Guardian Crystal", ["magic","stone"]),
        ability_handler=AbilityHandler([DamageTypeBuff("ancient_power1","Ancient Power","arcane",3),DamageTypeBuff("ancient_power2",None,"heat",3)]),
        slot="Offhand",
        price=12
    ),
    "gillberry":Food(
        name=("water", "Gillberry"),
        ability_handler=AbilityHandler([SingleUse()]),
        foodeffect=EffectSequence([
            HealEvent("item","user",10),
            AddAbilityEffect("user",get_ability("water_breathing"))
        ]),
        price=20,
        drop_chance=1
    ),
    "serpent_flesh":Food(
        name=("water", "Serpent Flesh"),
        ability_handler=AbilityHandler([SingleUse()]),
        drop_chance=1,
        foodeffect=HealEvent("item","user",45),
        price=15
    ),
    "bat_flesh":Food(
        name=("water", "Bat Flesh"),
        ability_handler=AbilityHandler([SingleUse()]),
        drop_chance=0.5,
        foodeffect=HealEvent("item","user",20),
        price=15
    ),
    "armory_key":Key(("iron", "Armory Key"),key_id="armory_key"),
    "iron_key":Key(("iron", "Iron Key"),key_id="iron_key"),
}

items.update(shadowed_forest_items)

iron_items : dict[str:Item] = {
    "iron_sword":MeleeWeapon(
        name=("iron","Iron Sword"),
        attackeffect=DamageEvent(damage=10, damage_type="slashing"),
        price=5
    ),
    "iron_staff":MeleeWeapon(
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
        ability_handler=AbilityHandler([SelectiveArmor("sturdy", ("iron", "Sturdy"), "slashing", 4)]),
        slot="Offhand",
        price=5
    ),
    "iron_shiv":Equipment(
        name=("iron","Iron Shiv"),
        ability_handler=AbilityHandler([SelectiveBuff("meleebuff",None,get_ability("melee"),2)]),
        slot="Offhand",
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
    "fire_staff":MagicWeapon(
        name=("heat","Fire Staff"),
        attackeffect=EffectSequence([
            RepeatEvent(DamageEvent(damage=7,damage_type="heat"),2)
        ]),
        mana_cost=5,
        price=15
    ),
    "ice_staff":MagicWeapon(
        name=("cold","Ice Staff"),
        attackeffect=EffectSequence([
            DamageEvent(damage=10,damage_type="cold"),
            ProbabilityEvent(AddAbilityEffect("target", Status(get_ability("freeze"),3)),0.5)
        ]),
        mana_cost=5,
        price=15
    ),
    "poison_staff":MagicWeapon(
        name=("toxic","Poison Staff"),
        attackeffect=EffectSequence([
            DamageEvent(damage=5,damage_type="toxic"),
            ProbabilityEvent(AddAbilityEffect("target", Status(get_ability("poison"),3)),0.5)
        ]),
        mana_cost=5,
        price=15
    ),
    "lightning_staff":MagicWeapon(
        name=("lightning","Lightning Staff"),
        attackeffect=EffectSequence([
            DamageEvent(damage=10,damage_type="lightning"),
            ProbabilityEvent(AddAbilityEffect("target", Status(get_ability("stun"),3)),0.25)
        ]),
        mana_cost=5,
        price=15
    ),
    "arcane_staff":MagicWeapon(
        name=("arcane","Arcane Staff"),
        attackeffect=EffectSequence([
            DamageEvent(damage=10,damage_type="arcane",armor_penetrate=-1)
        ]),
        mana_cost=5,
        price=15
    ),
    "shadow_staff":MagicWeapon(
        name=("shadow","Shadow Staff"),
        attackeffect=EffectSequence([
            DamageEvent(damage=10,damage_type="shadow"),
            ProbabilityEvent(AddAbilityEffect("target", Status(get_ability("doomed"),3)),0.5)
        ]),
        mana_cost=5,
        price=15
    ),
    "celestial_staff":MagicWeapon(
        name=("celestial","Celestial Staff"),
        attackeffect=EffectSequence([
            DamageEvent(damage=10,damage_type="celestial"),
            ProbabilityEvent(AddAbilityEffect("user", Status(get_ability("empowered"),3)),0.5)
        ]),
        mana_cost=5,
        price=15
    ),
    "wildfire_scroll":Scroll(
        name=("heat","Wildfire Scroll"),
        ability_handler=AbilityHandler([MultiUse(3)]),
        useeffect=EffectSequence([
            RepeatEvent(DamageEvent(damage=15,damage_type="heat"),3)
        ]),
        mana_cost=5,
        price=15
    ),
    "blizzard_scroll":Scroll(
        name=("cold","Blizzard Scroll"),
        ability_handler=AbilityHandler([MultiUse(3)]),
        useeffect=EffectSequence([
            DamageEvent(damage=20,damage_type="cold"),
            AddAbilityEffect("target", Status(get_ability("freeze"),10))
        ]),
        mana_cost=5,
        price=15
    ),
    "venom_scroll":Scroll(
        name=("toxic","Venom Scroll"),
        ability_handler=AbilityHandler([MultiUse(3)]),
        useeffect=EffectSequence([
            DamageEvent(damage=10,damage_type="toxic"),
            AddAbilityEffect("target", Status(get_ability("poison"),10))
        ]),
        mana_cost=5,
        price=15
    ),
    "storm_scroll":Scroll(
        name=("lightning","Storm Scroll"),
        ability_handler=AbilityHandler([MultiUse(3)]),
        useeffect=EffectSequence([
            DamageEvent(damage=20,damage_type="lightning"),
            AddAbilityEffect("target", Status(get_ability("stun"),10))
        ]),
        mana_cost=5,
        price=15
    ),
    "mystic_scroll":Scroll(
        name=("arcane","Mystic Scroll"),
        ability_handler=AbilityHandler([MultiUse(3)]),
        useeffect=EffectSequence([
            DamageEvent(damage=30,damage_type="arcane",armor_penetrate=-1)
        ]),
        mana_cost=5,
        price=15
    ),
    "eclipse_scroll":Scroll(
        name=("shadow","Eclipse Scroll"),
        ability_handler=AbilityHandler([MultiUse(3)]),
        useeffect=EffectSequence([
            DamageEvent(damage=20,damage_type="shadow"),
            AddAbilityEffect("target", Status(get_ability("doomed"),10))
        ]),
        mana_cost=5,
        price=15
    ),
    "starfire_scroll":Scroll(
        name=("celestial","Starfire Scroll"),
        ability_handler=AbilityHandler([MultiUse(3)]),
        useeffect=EffectSequence([
            DamageEvent(damage=20,damage_type="celestial"),
            AddAbilityEffect("user", Status(get_ability("empowered"),10))
        ]),
        mana_cost=5,
        price=15
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

consumable_items : dict[str:Item] = {
    "sharpening_stone":Sharpener(
        name=("iron","Sharpening Stone"),
        ability_handler=AbilityHandler([MultiUse(3)]),
        useeffect=SharpenEvent("item", "target", 0.25),
        price=2
    ),
    "healing_potion":Potion(
        name=("healing","Healing Potion"),
        ability_handler=AbilityHandler([SingleUse()]),
        useeffect=HealEvent("item","user",20),
        price=2
    ),
    "restoration_potion":Potion(
        name=("magic","Restoration Potion"),
        ability_handler=AbilityHandler([SingleUse()]),
        useeffect=RestoreMPEvent("item","user",20),
        price=4
    ),
    "healing_potion_with_magic":Potion(
        name=utility.alternate_colors("Infused Healing Potion",["healing","magic"]),
        ability_handler=AbilityHandler([ManaCost("manacost","Mana Cost", 5),SingleUse()]),
        useeffect=HealEvent("item","user",30),
        price=4
    ),
    "regen_potion":Potion(
        name=("healing","Regeneration Potion"),
        ability_handler=AbilityHandler([SingleUse()]),
        useeffect=AddAbilityEffect("user",Status(get_ability("regen"),10)),
        price=10
    ),
    "empowering_potion":Potion(
        name=("celestial","Empowering Potion"),
        ability_handler=AbilityHandler([SingleUse()]),
        useeffect=AddAbilityEffect("user",Status(get_ability("empowered"),8)),
        price=10
    ),
    "ironhide_potion":Potion(
        name=("iron","Ironhide Potion"),
        ability_handler=AbilityHandler([SingleUse()]),
        useeffect=AddAbilityEffect("user",Status(Armor("iron_hide", ("iron", "Ironhide"),3),5)),
        price=4
    ),
    "lifeforce_container":Potion(
        name=("healing","Lifeforce Container"),
        ability_handler=AbilityHandler([SingleUse()]),
        useeffect=IncreaseMaxHPEffect("item","user",10),
        drop_chance=1,
        price=10
    ),
    "mana_container":Potion(
        name=("magic","Mana Container"),
        ability_handler=AbilityHandler([SingleUse()]),
        useeffect=IncreaseMaxMPEffect("item","user",10),
        drop_chance=1,
        price=10
    )
}

items.update(consumable_items)

food_items : dict[str:Item] = {
    "roast_chicken":Food(
        name=("meat", "Roast Chicken"),
        ability_handler=AbilityHandler([SingleUse()]),
        drop_chance=0.5,
        foodeffect=HealEvent("item","user",15),
        price=2
    ),
    "roast_pork":Food(
        name=("meat", "Roast Pork"),
        ability_handler=AbilityHandler([SingleUse()]),
        drop_chance=0.4,
        foodeffect=HealEvent("item","user",20),
        price=3
    ),
    "roast_beef":Food(
        name=("meat", "Roast Beef"),
        ability_handler=AbilityHandler([SingleUse()]),
        drop_chance=0.3,
        foodeffect=HealEvent("item","user",25),
        price=4
    ),
    "uneaten_scraps":Food(
        name=("meat", "Uneaten Scraps"),
        ability_handler=AbilityHandler([SingleUse()]),
        drop_chance=0.6,
        foodeffect=HealEvent("item","user",10),
        price=4
    ),
    "bone_marrow_stew":Food(
        name=("food", "Bone Marrow Stew"),
        ability_handler=AbilityHandler([SingleUse()]),
        foodeffect=EffectSequence([
            HealEvent("item","user",20),
            AddAbilityEffect("user",Status(Armor("strong_bones", ("iron", "Strong Bones"),2),10))
        ]),
        price=5
    ),
    "torchroot_buds":Food(
        name=("heat", "Torchroot Buds"),
        ability_handler=AbilityHandler([MultiUse(3)]),
        foodeffect=EffectSequence([
            HealEvent("item","user",10),
            AddAbilityEffect("user",Status(DamageTypeBuff("torchroot_buff",("heat","Spicy"),"heat",5),10))
        ]),
        price=20
    ),
    "shockflower_blossom":Food(
        name=("lightning", "Shockflower Blossom"),
        ability_handler=AbilityHandler([MultiUse(3)]),
        foodeffect=EffectSequence([
            HealEvent("item","user",10),
            AddAbilityEffect("user",Status(DamageTypeBuff("shockflower_buff",("lightning","Shocking"),"lightning",5),10))
        ]),
        price=20
    ),
    "surface_apple":Food(
        name=("celestial", "Surface Apple"),
        ability_handler=AbilityHandler([MultiUse(3)]),
        foodeffect=EffectSequence([
            HealEvent("item","user",10),
            AddAbilityEffect("user",Status(get_ability("empowered"),10))
        ]),
        price=20
    ),
}

items.update(food_items)

enemy_items : dict[str:Item] = {
    "magic_barbs":MeleeWeapon(
        name=("magic","Magic Barbs"),
        drop_chance=0,
        attackeffect=DamageEvent(damage=10,damage_type="arcane",armor_penetrate=2)
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
    "maneater_bite":MeleeWeapon(
        name=("shadow","Maneater Jaw"),
        drop_chance=0,
        attackeffect=EffectSequence([DamageEvent(damage=10,damage_type="shadow"),
            ProbabilityEvent(AddAbilityEffect("target", Status(get_ability("doomed"),3)),0.25)])
    ),
    "wave_crash":MeleeWeapon(
        name=("water","Wave Crash"),
        drop_chance=0,
        attackeffect=EffectSequence([DamageEvent(damage=5,damage_type="bashing"),DamageEvent(damage=5,damage_type="cold"),
            ProbabilityEvent(AddAbilityEffect("target", Status(get_ability("freeze"),3)),0.5)])
    ),
    "flame_crash":MeleeWeapon(
        name=("heat","Flame Crash"),
        drop_chance=0,
        attackeffect=RepeatEvent(DamageEvent(damage=5,damage_type="heat"),3)
    ),
    "bat_bite":MeleeWeapon(
        name=("shadow","Bat Bite"),
        drop_chance=0,
        attackeffect=EffectSequence([DamageEvent(damage=3,damage_type="shadow"),
            ProbabilityEvent(AddAbilityEffect("target", Status(get_ability("doomed"),3)),0.25)])
    ),
}

items.update(enemy_items)

tools : dict[str:Item] = {
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

final_boss_items : dict[str:Item] = {
    "shadow_blade":MeleeWeapon(
        name=[("shadow","Shadow Blade")],
        attackeffect=
            EffectSequence([
                DamageEvent(damage=10, damage_type="slashing"),
                DamageEvent(damage=10, damage_type="shadow"),
                ProbabilityEvent(AddAbilityEffect("target", Status(get_ability("doomed"),3)),0.25)
            ]),
        drop_chance=0.3,
        durability=0.95,
        price=20
    ),
    "gloom_helm":Equipment(
        name=("shadow","Gloom Helm"),
        ability_handler=AbilityHandler([Armor("armor",None,5),DamageTypeBuff("shadow_armor",("shadow","Murky Blades"),"shadow",3)]),
        slot="Helmet",
        drop_chance=0.3,
        price=20
    ),
    "umbra_cloak":Equipment(
        name=("shadow","Umbra Cloak"),
        ability_handler=AbilityHandler([Armor("armor",None,5),SelectiveArmor("shadow_armor",("shadow","Armor of Darkness"),"shadow",3)]),
        slot="Armor",
        drop_chance=0.3,
        price=20
    ),
    "blight_treads":Equipment(
        name=("shadow","Blight Treads"),
        ability_handler=AbilityHandler([Armor("armor",None,5),ImmuneToAbility("shadow_armor",("shadow","Fatetwister"),get_ability("doomed"))]),
        slot="Boots",
        drop_chance=0.3,
        price=20
    ),
    "twilight_ring":Equipment(
        name=("shadow","Twilight Ring"),
        ability_handler=AbilityHandler([SelectiveBuff("shadow_armor",("shadow","Mystic Drain"),get_ability("magic"),3),AbilityArmor("shadow_armor",None,get_ability("magic"),3)]),
        slot="Ring",
        drop_chance=0.3,
        price=20
    ),
    "dusk_shield":Equipment(
        name=("shadow","Dusk Shield"),
        ability_handler=AbilityHandler([Armor("armor",None,5),Reciprocate("spikes",("shadow","Dark Equilibrium"),AddAbilityEffect("attacker",get_ability("doomed")))]),
        slot="Offhand",
        drop_chance=0.3,
        price=20
    ),
}

items.update(final_boss_items)

for x in items:
    items[x].id = x

def get_item(item_id : str) -> Item:
    return copy.deepcopy(items[item_id])