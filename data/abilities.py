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
    "regen":EndOfTurnEffect(
        id="regen",
        name=("healing","Regeneration"),
        effect=HealEvent(5)
    ),
    "poison":EndOfTurnEffect(
        id="poison",
        name=("poison","Poison"),
        effect=DamageEvent(5,"poison",-1)
    )
}

def get_ability(ability_id : str) -> "Ability":
    return copy.deepcopy(abilities[ability_id])

abilities["goblin_boss"]= BattleCry(
        id="goblin_boss",
        name=utility.alternate_colors("Big Goblin",["goblin","fire"]),
        tag_id=get_ability("goblin"),
        strength=5
    )
abilities["stun"]=Stunned(
        id="stun",
        name=("stunned","Stunned"),
        tag_id=get_ability("melee"),
        damage_mod=2
    )