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

dialogue_nodes : dict[str:DialogueNode] = {}

wise_figure : dict[str:DialogueNode] = {
    "wise_figure_1" : DialogueNode(
        "\"Hello?\"",
        ["\"Well hello there traveller...\nIt appears you've awoken from your fall.\""],
        "wise_figure_2"
    ),
    "wise_figure_2" : DialogueNode(
        "\"Who are you?\"",
        ["\"That's not important right now.\nWhat is important is teaching you how to survive.\""],
        "wise_figure_3"
    ),
    "wise_figure_3" : DialogueNode(
        "\"Where am I?\"",
        ["\"A chatty one! Haha!\nWelcome to the Subterra.\nYou came from up there.\"\nThe figure points upwards to a small patch of sky, barely visible."],
        "wise_figure_4"
    ),
    "wise_figure_4" : DialogueNode(
        "\"The Subterra?\"",
        ["\"Yes, that's what we call this.\"\nThe figure gestures around to an abandoned temple.\n\"These are the Ruins of the Sun.\nBefore, we were a mighty religion, but we've crumbled to dust.\""],
        "wise_figure_5"
    ),
    "wise_figure_5" : DialogueNode(
        "\"How can I leave?\"",
        ["\"Well, this won't be easy for you to hear...\nThere is no way out. As far as we know, at least.\nThat is, unless you could defeat the Shadowed One...\nNevermind that. For now, why don't you take this.\""],
        None,
        EffectSequence([GiveItemEffect("speaker","player",get_item("wooden_sword")),SetDialogueEffect(source="wise_figure_6",target="speaker")])
    ),
    "wise_figure_6" : DialogueNode(
        "\"What do I do?\"",
        ["\"Select the training dummy and attack it.\nProve to me you'll be able to survive.\""],
        None
    ),
    "wise_figure_proud" : DialogueNode(
        "\"I showed that dummy.\"",
        ["\"Excellent. You have what it takes to survive down here. Have this.\""],
        None,
        EffectSequence([GiveItemEffect("speaker","player",get_item("wooden_key")),SetDialogueEffect(source="wise_figure_done",target="speaker")])
    ),
    "wise_figure_done" : DialogueNode(
        "\"I want to talk.\"",
        ["\"Good luck out there. May you see the stars, friend.\""],
        None,
    ),
    "wise_figure_gift" : DialogueNode(
        "\"Can you help me? The beasts of the Shadowed Forest are too strong.\"",
        ["\"Oh, you're travelling into the forest now? You've come a long way! Well, I may have something that could be helpful. Take this, and may you see the stars.\""],
        None,
        EffectSequence([GiveItemEffect("speaker","player",get_item("celestial_staff")),SetDialogueEffect(source="wise_figure_done",target="speaker")])
    ),
}

dialogue_nodes.update(wise_figure)

coral_king : dict[str:DialogueNode] = {
    "coral_king_1" : DialogueNode(
        "\"King of Coral, I come seeking assistance.\"",
        ["\"You may stand. What brings you before my court under the sea?\""],
        "coral_king_2"
    ),
    "coral_king_2" : DialogueNode(
        "\"I come seeking the key to the Iron Gate.\"",
        ["\"You do recognise that the Iron Gate is the only thing stopping the Darkened One from wrecking havoc on the Subterra!\nYour foolishness seemingly knows no bounds.\""],
        "coral_king_3"
    ),
    "coral_king_3" : DialogueNode(
        "\"When I defeat the Darkened One, you will be free of this prison.\"",
        ["\"And what makes you think that you will win?\nYou humans are always so arrogant.\""],
        "coral_king_4"
    ),
    "coral_king_4" : DialogueNode(
        "\"I have no proof other than my desire to see the stars once again.\"",
        ["The king thinks for a moment.\n\"I once had the desire to see the sky. Recently, I've found myself content at living underground.\""],
        "coral_king_5"
    ),
    "coral_king_5" : DialogueNode(
        "\"Consider for a moment your kingdom. Your people wish to swim in the moonlight once again.\"",
        ["\"You speak the truth, human...\nYou've convinced me.\nI hand you this out of trust. You must defeat the beast that keeps us prisoner.\""],
        None,
        EffectSequence([GiveItemEffect("speaker","player",get_item("iron_key")),SetDialogueEffect(source="coral_king_done",target="speaker")])
    ),
    "coral_king_done" : DialogueNode(
        "\"I will be victorious.\"",
        ["\"May you see the stars.\""],
        None,
    )
}

dialogue_nodes.update(coral_king)

fellow_traveller : dict[str:DialogueNode] = {
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
        AddtoInventoryEvent("player",get_item("lightning_staff"))
    ),
    "fellow_traveller_5" : DialogueNode(
        "Thank you!",
        ["\"Live long, friend.\""],
        None,
        SetDialogueEffect(source="fellow_traveller_done",target="speaker")
    ),
    "fellow_traveller_done" : DialogueNode(
        None,
        ["\"Remember, goblin cave up north!\""],
        None,
    ),
}

dialogue_nodes.update(fellow_traveller)

old_figure : dict[str:DialogueNode] = {
    "old_figure_1" : DialogueNode(
        "Hello!",
        ["The figure doesn't move."],
        "old_figure_2"
    ),
    "old_figure_2" : DialogueNode(
        "Uhh, hello?",
        ["The figure shoots up with a start!\n\"The Shadowed One rages, the stars have dimmed.\""],
        "old_figure_3"
    ),
    "old_figure_3" : DialogueNode(
        "What?",
        ["\"A hero stands, awaiting their fate. Yet undersea they may be free.\""],
        "old_figure_4"
    ),
    "old_figure_4" : DialogueNode(
        "Am I the hero of which you speak?",
        ["The figure looks directly at you.\n\"This was not for you to know.\"\nThe figure sprints into the forest.\nYou are unable to follow them."],
        None,
        RemoveRoomObjEffect("place","speaker")
    )
}

dialogue_nodes.update(old_figure)

young_child : dict[str:DialogueNode] = {
    "young_child_1" : DialogueNode(
        "\"Hello there!\"",
        ["\"Are you from the surface?\""],
        ["young_child_2","young_child_3"]
    ),
    "young_child_2" : DialogueNode(
        "\"Yes.\"",
        ["\"Wow, the sky must have looked cool.\""],
        "young_child_4"
    ),
    "young_child_3" : DialogueNode(
        "\"No.\"",
        ["\"I would know if you're from here. And you're not a monster, so you must be from the surface.\""],
        "young_child_4"
    ),
    "young_child_4" : DialogueNode(
        "\"Is there anything around here?\"",
        ["\"I have a friend who lives around here. They're a fish. Sometimes I see them on the shore. The elder said I shouldn't go near them.\""],
        None,
        SetDialogueEffect(source="young_child_done",target="speaker")
    ),
    "young_child_done" : DialogueNode(
        "\"What are you doing now?\"",
        ["\"I'm a fish! Look at me!\""],
        None,
    ),
}

dialogue_nodes.update(young_child)

tired_parent : dict[str:DialogueNode] = {
    "tired_parent_1" : DialogueNode(
        "\"Hello!\"",
        ["\"Have you seen where my child has gone off to? I turn around for one second and they're gone.\""],
        ["tired_parent_2","tired_parent_3"]
    ),
    "tired_parent_2" : DialogueNode(
        "\"Yes. They're by the shore.\"",
        ["\"They know they're not supposed to do that! We don't want them getting snatched by those fish monsters.\""],
        "tired_parent_4"
    ),
    "tired_parent_3" : DialogueNode(
        "\"No.\"",
        ["\"Well, could you help me find them?\""],
        "tired_parent_1"
    ),
    "tired_parent_4" : DialogueNode(
        "\"I'm going to escape from the Subterra.\"",
        ["\"Good luck with that. I've never heard of anyone escaping. It's best to just accept life down here.\""],
        None,
        SetDialogueEffect(source="tired_parent_done",target="speaker")
    ),
    "tired_parent_done" : DialogueNode(
        "\"Hello.\"",
        ["\"Stay safe out there.\""],
        None,
    ),
}

dialogue_nodes.update(tired_parent)

wise_elder : dict[str:DialogueNode] = {
    "wise_elder_1" : DialogueNode(
        "\"Greetings, elder.\"",
        ["\"Oh, you must be that person that fell from the surface!\""],
        ["wise_elder_2","wise_elder_3"]
    ),
    "wise_elder_2" : DialogueNode(
        "\"How did you know?\"",
        ["\"Word gets around fast in the Subterra.\""],
        "wise_elder_4"
    ),
    "wise_elder_3" : DialogueNode(
        "\"No.\"",
        ["\"You must think you're funny.\""],
        "wise_elder_1"
    ),
    "wise_elder_4" : DialogueNode(
        "\"How can I get out of this place?\"",
        ["\"I explored every cavern down here in my youth. I haven't been able to find any way out. The only place I was never able to get to was past the Iron Gate in the forest. Maybe try that?\""],
        None,
        SetDialogueEffect(source="wise_elder_done",target="speaker")
    ),
    "wise_elder_done" : DialogueNode(
        "\"Greetings, elder.\"",
        ["\"Remember, Iron Gate.\nAnd my child, take care of yourself.\nWe do not speak of what is past the Iron Gate, but you must defeat it for our sakes.\""],
        None,
    ),
}

dialogue_nodes.update(wise_elder)

fishy_peasant : dict[str:DialogueNode] = {
    "fishy_peasant_1" : DialogueNode(
        "\"Hello...?\"",
        ["\"Well, hello! Are you a human?\""],
        ["fishy_peasant_2","fishy_peasant_3"]
    ),
    "fishy_peasant_2" : DialogueNode(
        "\"Yes!\"",
        ["\"Oh wow! I've never seen a human under the water's surface before!\nI have a friend up there, but they've never visited my home.\""],
        "fishy_peasant_4"
    ),
    "fishy_peasant_3" : DialogueNode(
        "\"No.\"",
        ["\"Oh, well you sure are a strange looking fish.\""],
        "fishy_peasant_4"
    ),
    "fishy_peasant_4" : DialogueNode(
        "\"What is this place?\"",
        ["\"This is the Undersea Keep. We live below the water of the lake in our bioluminescent kingdom.\nI've never seen the sky, but I've heard it is as if the lights of our city were brighter than anything.\""],
        None,
        SetDialogueEffect(source="fishy_peasant_done",target="speaker")
    ),
    "fishy_peasant_done" : DialogueNode(
        "\"Hello!\"",
        ["\"Nice to see you again. Enjoy your time in the city!\""],
        None,
    ),
}

dialogue_nodes.update(fishy_peasant)

fishy_merchant : dict[str:DialogueNode] = {
    "fishy_merchant_1" : DialogueNode(
        "\"Do you have wares for sale?\"",
        ["\"For a customer as fine as yourself, of course.\nAnd I'll even take your bones as currency.\nNot everyone will do that down here. What do you say?\""],
        "fishy_merchant_2"
    ),
    "fishy_merchant_2" : DialogueNode(
        "\"Sounds great!\"",
        ["\"Well, don't hesitate! Take a look.\""],
        None,
        SetDialogueEffect(source="fishy_merchant_done",target="speaker")
    ),
    "fishy_merchant_done" : DialogueNode(
        "\"Hello.\"",
        ["\"I've always got the best items in stock!\nTake a look.\""],
        None,
    ),
}

dialogue_nodes.update(fishy_merchant)

fishy_noble : dict[str:DialogueNode] = {
    "fishy_noble_1" : DialogueNode(
        "\"The city is beautiful.\"",
        ["\"I'm sure it's unlike anything you've ever seen in the Subterra. Granted, I've never been above the water's surface, but I digress.\""],
        "fishy_noble_2"
    ),
    "fishy_noble_2" : DialogueNode(
        "\"Do you hope to see the stars someday?\"",
        ["\"Don't we all? I hope we're released from this prison before I die. But the Shadowed One keeps us here, nonetheless.\""],
        None,
        SetDialogueEffect(source="fishy_noble_done",target="speaker")
    ),
    "fishy_noble_done" : DialogueNode(
        "\"Hello!\"",
        ["\"I hope you will be the one to deliver us unto freedom.\""],
        None,
    ),
}

dialogue_nodes.update(fishy_noble)

trailblazer : dict[str:DialogueNode] = {
    "trailblazer_1" : DialogueNode(
        "\"Hail!\"",
        ["\"Hail to you! Traveller, do you know what danger you're in?\""],
        ["trailblazer_2","trailblazer_4"]
    ),
    "trailblazer_2" : DialogueNode(
        "\"Yes.\"",
        ["\"Then why have you come? You will surely die here!\""],
        "trailblazer_3"
    ),
    "trailblazer_3" : DialogueNode(
        "\"I'll survive.\"",
        ["\"No, you won't! I've been blazing trails here for the past week, and you don't want to know what I've seen!\""],
        ["trailblazer_5","trailblazer_6"]
    ),
    "trailblazer_4" : DialogueNode(
        "\"No.\"",
        ["\"This is the Shadowed forest. Have you not heard the legends? Humans rarely make it through alive, and you're much safer in the town of Lumin.\""],
        "trailblazer_5"
    ),
    "trailblazer_5" : DialogueNode(
        "\"I'm not from Lumin.\"",
        ["\"Wait, have you fallen from the surface? And you're still alive? Well, if you hope to keep it that way, I wouldn't enter the forest until you're ready. I've been blazing trails, and it's a scary place.\""],
        ["trailblazer_6","trailblazer_7"]
    ),
    "trailblazer_6" : DialogueNode(
        "\"What have you seen?\"",
        ["\"I've seen plants that will eat you alive! Beasts which can crunch your bones to dust!\""],
        "trailblazer_7"
    ),
    "trailblazer_7" : DialogueNode(
        "\"Thanks for the information.\"",
        ["\"Well, I can't have you going into there without some help, so take these.\""],
        "trailblazer_8",
        EffectSequence([GiveItemEffect("speaker","player",get_item("healing_potion")),GiveItemEffect("speaker","player",get_item("regen_potion"))])
    ),
    "trailblazer_8" : DialogueNode(
        "\"Thank you.\"",
        ["\"Stay save, and live long.\""],
        None,
        SetDialogueEffect(source="trailblazer_done",target="speaker")
    ),
    "trailblazer_done" : DialogueNode(
        "\"I want to talk.\"",
        ["\"Yes?\""],
        ["trailblazer_info1"],
    ),
    "trailblazer_very_done" : DialogueNode(
        "\"I want to talk.\"",
        ["\"Yes?\""],
        ["trailblazer_info2","trailblazer_info3"],
    ),
    "trailblazer_info1" : DialogueNode(
        "\"How can I fight the monsters in the Shadowed Forest?\"",
        ["\"Many of the monsters in the forest have been evolving here for centures. They're weak to celestial magic. You've fallen, so you must have met the Wise Figure, correct? They may be able to help you.\""],
        None,
        EffectSequence([SetDialogueEffect(source="trailblazer_very_done",target="speaker"),SetDialogueEffect(source="wise_figure_gift",target="roomid:starting_room:wise_figure")])
    ),
    "trailblazer_info2" : DialogueNode(
        "\"What's in the Shadowed Forest?\"",
        ["\"To the west is the Mystic Temple. I haven't been able to explore it yet, but it should have arcane relics that may be helpful.\nTo the north is the Iron Gate, but it's never been opened.\nTo the east is the Dark Lake, where you'll find Lumin.\nLumin is located on an island on the lake. It's a good strategic location.\""],
        None,
        SetDialogueEffect(source="trailblazer_very_done",target="speaker")
    ),
    "trailblazer_info3" : DialogueNode(
        "\"Why are you travelling into the forest?\"",
        ["\"The forest is dangerous, and needs someone to blaze the trails. I've set up a campfire in one of the clearings you can use.\""],
        None,
        SetDialogueEffect(source="trailblazer_very_done",target="speaker")
    ),
}

dialogue_nodes.update(trailblazer)

thrifty_traveller : dict[str:DialogueNode] = {
    "thrifty_traveller_1" : DialogueNode(
        "\"Hello!\"",
        ["\"Greetings friend!\nAre you new to the Subterra?\""],
        ["thrifty_traveller_2","thrifty_traveller_3"]
    ),
    "thrifty_traveller_2" : DialogueNode(
        "\"Yes.\"",
        ["\"Welcome to the underground. It's dangerous down here, make sure you never let your guard down.\""],
        "thrifty_traveller_4"
    ),
    "thrifty_traveller_3" : DialogueNode(
        "\"That's not for you to know.\"",
        ["\"Oh, very mysterious! Well I hope you can wash off some of those greedling guts.\"\nThe traveller points at your nasty clothes."],
        "thrifty_traveller_4"
    ),
    "thrifty_traveller_4" : DialogueNode(
        "\"What are you doing down here?\"",
        ["\"I'm what you might describe as a merchant. I peddle my wares and travel around.\""],
        "thrifty_traveller_5"
    ),
    "thrifty_traveller_5" : DialogueNode(
        "\"Goodbye.\"",
        ["\"Live long, friend.\""],
        None,
        SetDialogueEffect(source="thrifty_traveller_done",target="speaker")
    ),
    "thrifty_traveller_done" : DialogueNode(
        "\"I want to talk.\"",
        ["\"What is it?\""],
        ["thrifty_traveller_info1","thrifty_traveller_info2","thrifty_traveller_info3"],
    ),
    "thrifty_traveller_info1" : DialogueNode(
        "\"Why does your economy depend on bones?\"",
        ["\"Bones are the backbone of commerce in the Subterra.\nThey're readily avaliable, but scarce enough to make a good currency.\nNow why don't you buy some of my things?\""],
        None,
        SetDialogueEffect(source="thrifty_traveller_done",target="speaker")
    ),
    "thrifty_traveller_info2" : DialogueNode(
        "\"What's around here?\"",
        ["\"To the south are the Ruins of the Sun. The Wise Figure spends a lot of time there.\nTo the north are the Shattered Ruins. There's a castle there, but it's been overrun by goblins. Stay safe if you're going to check it out.\""],
        None,
        SetDialogueEffect(source="thrifty_traveller_done",target="speaker")
    ),
    "thrifty_traveller_info3" : DialogueNode(
        "\"Where are you from?\"",
        ["\"I was born in the town of Lumin. It's north of the ruins, and it's the main settlement in the Subterra.\""],
        None,
        SetDialogueEffect(source="thrifty_traveller_done",target="speaker")
    ),
}

dialogue_nodes.update(thrifty_traveller)

def get_dialogue(dia_id : str) -> DialogueNode:
    return dialogue_nodes[dia_id]