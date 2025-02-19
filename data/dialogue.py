from classes.actions import *
from collections.abc import Callable, Hashable, MutableSequence
from data.items import get_item

class DialogueNode:
    def __init__(self, response_text : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], text : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], choices : str | list[str] = None, effect : Effect = None):
        self.response_text : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]] = response_text
        self.text : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]] = text
        self.choices : str | list[str]= choices or []
        self.effect : Effect = effect
    
    def get_response_text(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return self.response_text

    def get_text(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return self.text

    def get_effect(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return self.effect
    
    def get_choices(self) -> list[str]:
        if isinstance(self.choices, str):
            return [self.choices]
        else:
            return self.choices
    
    def has_choices(self) -> bool:
        return len(self.choices) > 0

dialogue_nodes : dict[str:DialogueNode] = {
    "wise_figure_1" : DialogueNode(
        None,
        ["\"Well hello there traveller...\nIt appears you've awoken from your fall.\""],
        "wise_figure_2"
    ),
    "wise_figure_2" : DialogueNode(
        "Who are you?",
        ["\"That's not important right now.\nWhat is important is teaching you how to survive.\""],
        "wise_figure_3"
    ),
    "wise_figure_3" : DialogueNode(
        "Where am I?",
        ["\"A chatty one! Haha!\nWelcome to Subterra.\nYou came from up there.\"\nThe figure points upwards to a small patch of sky, barely visible."],
        "wise_figure_4"
    ),
    "wise_figure_4" : DialogueNode(
        "Subterra?",
        ["\"Yes, that's what we call this.\"\nThe figure gestures around to an abandoned temple.\n\"These are the Ruins of the Sun.\nBefore, we were a mighty religion, but we've crumbled to dust.\""],
        "wise_figure_5",
    ),
    "wise_figure_5" : DialogueNode(
        "How can I leave?",
        ["\"Well, this won't be easy for you to hear...\nThere is no way out. As far as we know, at least.\nFor now, why don't you take some supplies from that wooden chest and explore around for a bit.\""],
        None,
        EffectSelectorPredefinedTarget(SetDialogueEffect(),"wise_figure_done")
    ),
    "wise_figure_done" : DialogueNode(
        None,
        ["\"Good luck out there.\""],
        None,
    ),
    "fellow_traveller_1" : DialogueNode(
        None,
        ["\"Hail! I haven't seen you before.\nI hate to ask, but did you just fall down?\""],
        "fellow_traveller_2"
    ),
    "fellow_traveller_2" : DialogueNode(
        "How did you know?",
        ["\"You've got all the gear that old man gives everyone.\nBy the way, watch out in this area\""],
        ["fellow_traveller_3", "fellow_traveller_4"]
    ),
    "fellow_traveller_3" : DialogueNode(
        "Why?",
        ["\"There's a goblin cave to the north of here. I'd hate to lose another human down here.\""],
        "fellow_traveller_4"
    ),
    "fellow_traveller_4" : DialogueNode(
        "I'll be fine",
        ["\"Well, no matter what happens, why don't you take this. Hopefully it will help.\""],
        "fellow_traveller_5",
        EffectSelectorPlayerSource(EffectSelectorPredefinedTarget(AddtoInventoryEvent(), get_item("lightning_tome")))
    ),
    "fellow_traveller_5" : DialogueNode(
        "Thank you!",
        ["\"Well, no matter what happens, why don't you take this. Hopefully it will help.\""],
        None,
        EffectSelectorPredefinedTarget(SetDialogueEffect(),"fellow_traveller_done")
    ),
    "fellow_traveller_done" : DialogueNode(
        None,
        ["\"Remember, goblin cave up north!\""],
        None,
    ),
}

def get_dialogue(dia_id : str) -> DialogueNode:
    return copy.deepcopy(dialogue_nodes[dia_id])