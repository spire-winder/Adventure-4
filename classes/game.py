from classes.ui import ActionButton
from classes.ui import InteractableActionButton
import sys
import urwid
from systems.event_system import Event
import systems.save_system
from classes.interactable import Interactable
from classes.interactable import Player
from classes.interactable import RoomObject
from classes.interactable import Room
import classes.dungeon
import classes.actions

class Game:
    def __init__(self, character_name : str, load : bool):
        self.save_file = "".join(c for c in character_name if c.isalnum() or c in (" _-")).rstrip()
        self.dungeon : classes.dungeon.Dungeon
        if load:
            self.dungeon = systems.save_system.load_save(self.save_file)
        else:
            self.dungeon = classes.dungeon.Dungeon()
        self.set_center_event = Event()
        self.quit_event = Event()

    def connect_signals(self):
        self.dungeon.ui_event.subscribe(self.handle_ui_event)
        self.dungeon.save_game_event.subscribe(self.save)

    def handle_ui_event(self, action : classes.actions.UIAction):
        if action != None:
            action.execute(self)

    def start_game(self) -> None:
        self.connect_signals()
        self.set_player_name(self.save_file)
        self.dungeon.start_game()

    def set_player_name(self, name):
        self.dungeon.player.name = name

    def player_interact(self, inter: classes.actions.PlayerInteractAction):
        self.dungeon.previous_interactable = self.dungeon.current_interactable
        self.dungeon.current_interactable = inter.interactable
        room_list = []
        room_list.append(urwid.Text(inter.get_name()))
        room_list.append(urwid.Text(inter.get_description()))
        room_list.append(urwid.Divider())
        for x in inter.get_choices(self.dungeon):
            if hasattr(x, "prev"):
                x.prev = inter
            room_list.append(InteractableActionButton(self.dungeon, x))
        if inter.interactable.include_back:
            room_list.append(urwid.Divider())
            if inter.prev != None:
                room_list.append(InteractableActionButton(self.dungeon, inter.prev))
            else:
                room_list.append(ActionButton("Save and Quit", self.save_and_quit))
        center_widget : urwid.ListBox = urwid.ListBox(urwid.SimpleFocusListWalker(room_list))
        self.set_center_event.emit(new_center=center_widget)

    def show_message_queue(self, queue : list):
        li : list = []
        for x in queue:
            li.append(urwid.Text(x))
        li.append(urwid.Divider())
        if not self.dungeon.game_over:
            li.append(ActionButton(["Okay"], self.end_round))
        else:
            li.append(ActionButton(["Return to menu"], self.delete_and_quit))
        notif_widget = urwid.ListBox(urwid.SimpleFocusListWalker(li))
        self.set_center_event.emit(new_center=notif_widget)


    def save(self) -> None:
        systems.save_system.save_game(self.save_file, self.dungeon)
    
    def delete_save(self) -> None:
        systems.save_system.delete_game(self.save_file)

    def delete_and_quit(self, button : ActionButton) -> None:
        self.delete_save()
        self.quit_event.emit()

    def save_and_quit(self, button : ActionButton) -> None:
        self.save()
        self.quit_event.emit()

    def end_round(self, button : ActionButton) -> None:
        self.dungeon.start_round()
