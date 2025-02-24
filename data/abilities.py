from classes.ability import *
import utility

abilities : dict[str:Ability] = {
    "melee":Ability(
        id="melee",
        name=("melee","Melee"),
        desc=None
    ),
    "magic":Ability(
        id="magic",
        name=("magic","Magic"),
        desc=None
    ),
    "goblin":Ability(
        id="goblin",
        name=("goblin","Goblin"),
        desc="Goblins are creatures with a knack for cooperation and collateral damage."
    ),
    "greedling":Ability(
        id="greedling",
        name=("meat","Greedling"),
        desc=[("meat","Greedlings"), " are small pests that inhabit ancient ruins, scavenging for shiny objects which they love."]
    ),
    "spined":Ability(
        id="spined",
        name=("iron","Spined"),
        desc=[("iron","Spined"), " are creatures brought to madness by painful iron spines driven into their backs."]
    ),
    "regen":EndOfTurnEffect(
        id="regen",
        name=("healing","Regeneration"),
        effect=HealEvent("self","user",5)
    ),
    "poison":EndOfTurnEffect(
        id="poison",
        name=("toxic","Poison"),
        effect=DamageEvent("self","user",5,"toxic",-1)
    ),
    "starved":DamageTypeBuff(
        "starved",
        ("meat", "Starved"),
        "slashing",
        3
    ),
    "hidden_single_use":HiddenAbility(SingleUse())
}

def get_ability(ability_id : str) -> "Ability":
    return copy.deepcopy(abilities[ability_id])

abilities["goblin_boss"]= BattleCry(
        id="goblin_boss",
        name=utility.alternate_colors("Big Goblin",["goblin","damage"]),
        tag_id=get_ability("goblin"),
        strength=5
    )
abilities["stun"]=Stunned(
        id="stun",
        name=("stunned","Stunned"),
        tag_id=get_ability("melee"),
        damage_mod=2
    )
abilities["greedling_boss"]= BattleCry(
        id="greedling_boss",
        name=("meat","Greedling Boss"),
        tag_id=get_ability("greedling"),
        strength=3
    )