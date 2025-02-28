from classes.ui import ActionButton
from classes.ui import InteractableActionButton
from classes.ui import BackActionButton
import sys
import urwid
from systems.event_system import Event
import systems.save_system
import classes.dungeon
import classes.actions
import utility

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
        room_list.append(urwid.Text(inter.get_description(self.dungeon)))
        room_list.append(urwid.Divider())
        for x in inter.get_choices(self.dungeon):
            if hasattr(x, "prev"):
                x.prev = inter
            room_list.append(InteractableActionButton(self.dungeon, x))
        if inter.interactable.include_back:
            room_list.append(urwid.Divider())
            if inter.prev != None:
                room_list.append(BackActionButton(self.dungeon, inter.prev))
            else:
                player_inter = classes.actions.PlayerInteractAction(self.dungeon.player)
                player_inter.prev = inter
                room_list.append(InteractableActionButton(self.dungeon,player_inter))
                room_list.append(urwid.Divider())
                room_list.append(ActionButton("Options", self.load_options_menu_wrapper))
        center_widget : urwid.ListBox = urwid.ListBox(urwid.SimpleFocusListWalker(room_list))
        self.set_center_event.emit(new_center=center_widget)

    def show_message_queue(self, queue : list):
        if len(queue) == 0:
            self.end_round(ActionButton("", self.end_round))
            return
        li : list = []
        for x in queue:
            li.append(urwid.Text(x))
        li.append(urwid.Divider())
        if not (self.dungeon.game_over or self.dungeon.game_win):
            li.append(ActionButton(["Continue"], self.end_round))
        else:
            li.append(ActionButton(["Return to menu"], self.delete_and_quit))
        notif_widget = urwid.ListBox(urwid.SimpleFocusListWalker(li))
        self.set_center_event.emit(new_center=notif_widget)

    def load_options_menu_wrapper(self, button):
        self.load_options_menu()

    def load_options_menu(self):
        options_menu_options = []
        options_menu_options.append(ActionButton("Resume", self.resume_wrapper))
        options_menu_options.append(ActionButton("Save", self.save_wrapper))
        options_menu_options.append(ActionButton("Save and quit", self.save_and_quit))
        options_menu = urwid.ListBox(urwid.SimpleFocusListWalker(options_menu_options))
        self.set_center_event.emit(new_center=options_menu)
    
    def load_victory_menu(self):
        menu_options = []
        menu_options.append(urwid.Text("You were victorious! You killed the Shadowed One, and the citizens of the Subterra are free to roam the external world."))
        menu_options.append(urwid.Text("Feel free to return to your save file with your new items."))
        menu_options.append(urwid.Divider())
        menu_options.append(ActionButton("Return to menu", self.save_and_quit))
        options_menu = urwid.ListBox(urwid.SimpleFocusListWalker(menu_options))
        self.set_center_event.emit(new_center=options_menu)
    
    def save_wrapper(self, button : ActionButton) -> None:
        self.save()

    def save(self) -> None:
        systems.save_system.save_game(self.save_file, self.dungeon)

    def resume_wrapper(self, button : ActionButton) -> None:
        self.resume()

    def resume(self) -> None:
        self.dungeon.interact_with_room()
    
    def delete_and_quit(self, button : ActionButton) -> None:
        if self.dungeon.game_win:
            self.load_victory_menu()
        else:
            self.quit_event.emit()

    def save_and_quit(self, button : ActionButton) -> None:
        self.save()
        self.quit_event.emit()

    def end_round(self, button : ActionButton) -> None:
        self.dungeon.start_round()
