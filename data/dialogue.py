from classes.actions import *
from collections.abc import Callable, Hashable, MutableSequence

class DialogueNode:
    def __init__(self, response_text : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], text : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]], choices : str | list[str] = []):
        self.response_text : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]] = response_text
        self.text : str | tuple[Hashable, str] | list[str | tuple[Hashable, str]] = text
        self.choices : str | list[str]= choices
    
    def get_response_text(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return self.response_text

    def get_text(self) -> str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]:
        return self.text
    
    def get_choices(self) -> list[str]:
        if isinstance(self.choices, str):
            return [self.choices]
        else:
            return self.choices
    
    def has_choices(self) -> bool:
        return self.choices != None

dialogue_nodes : dict[str:DialogueNode] = {
    "wise_figure_1" : DialogueNode(
        "",
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
        ["\"A chatty one! Haha!\nWelcome to the Below-earth.\nYou came from up there.\"\nThe figure points upwards to a small patch of sky, barely visible."],
        "wise_figure_4"
    ),
    "wise_figure_4" : DialogueNode(
        "The Below-earth?",
        ["\"Yes, that's what we call this.\"\nThe figure gestures around to an abandoned temple.\n\"These are the Ruins of the Sun.\nBefore, we were a mighty religion,\""],
        None
    ),
}

def get_dialogue(dia_id : str) -> DialogueNode:
    return copy.deepcopy(dialogue_nodes[dia_id])