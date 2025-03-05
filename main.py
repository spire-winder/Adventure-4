
import systems.save_system
import typing
import urwid
from classes.game import Game
import classes.ui
import utility

import os
os.system('title Adventure 4')

class Program:
    def __init__(self) -> None:
        self.game = None
        self.load_ui()
        if systems.save_system.has_saves():
            self.load_main_menu()
        else:
            self.load_info_menu()

    def load_ui(self):
        self.header : urwid.Widget = urwid.AttrMap(urwid.Text("Adventure 4 - Games for Blind Gamers", align="center"), "header")
        self.center : urwid.Widget = urwid.Text("")
        self.top : urwid.Frame = urwid.Frame(self.center, header=self.header)

    def load_main_menu_wrapper(self, button):
        self.load_main_menu()

    def i(self, button):
        pass

    def load_info_menu(self):
        info_menu_options = []
        info_menu_options.append(urwid.Text("Adventure 4 makes use of menus that can be navigated using the arrow keys. After you have the option you wish to choose selected, press ENTER to select it."))
        info_menu_options.append(classes.ui.ActionButton("Option 1", self.i))
        info_menu_options.append(classes.ui.ActionButton("Option 2", self.i))
        info_menu_options.append(classes.ui.ActionButton("Select this option to begin", self.load_main_menu_wrapper))
        info_menu = urwid.ListBox(urwid.SimpleFocusListWalker(info_menu_options))
        self.set_center(info_menu)

    def load_main_menu(self):
        start_menu_options = []
        start_menu_options.append(classes.ui.ActionButton("Play", self.play))
        start_menu_options.append(classes.ui.ActionButton("Quit", self.exit_game))
        main_menu = urwid.ListBox(urwid.SimpleFocusListWalker(start_menu_options))
        self.set_center(main_menu)
    
    def play(self, button : classes.ui.ActionButton):
        systems.save_system.create_folder(systems.save_system.save_dir_name)
        if systems.save_system.has_saves():
            self.load_saves()
        else:
            self.load_make_new_save()

    def new_character(self, button):
        self.load_make_new_save()

    def load_make_new_save(self):
        save_menu_options = []
        self.namebox : urwid.Edit = classes.ui.QuestionBox("What is your name, adventurer?\n", self.new_game)
        save_menu_options.append(self.namebox)
        save_menu = urwid.ListBox(urwid.SimpleFocusListWalker(save_menu_options))
        self.set_center(save_menu)

    def load_saves(self):
        save_menu_options = []
        for save in systems.save_system.get_saves():
            save_menu_options.append(classes.ui.SaveButton(save, self.load_game, save))
        save_menu_options.append(classes.ui.ActionButton("New Game", self.new_character))
        save_menu_options.append(classes.ui.ActionButton("Return", self.load_main_menu_wrapper))
        main_menu = urwid.ListBox(urwid.SimpleFocusListWalker(save_menu_options))
        self.set_center(main_menu)
    
    def load_game(self, button : classes.ui.SaveButton):
        self.game : Game = Game(button.save_file, True)
        self.init_game()

    def new_game(self):
        charactername : str = self.namebox.get_edit_text().strip()
        if charactername:
            save_file = "".join(c for c in charactername if c.isalnum() or c in (" _-")).rstrip()
            self.game : Game = Game(save_file, False)
            self.game.set_player_name(charactername)
            self.init_game()
    
    def init_game(self):
        self.connect_signals()
        self.game.start_game()

    def connect_signals(self):
        self.game.set_center_event.subscribe(self.set_center)
        self.game.quit_event.subscribe(self.load_main_menu)

    def clear_center(self):
        pass

    def set_center(self, new_center : urwid.Widget):
        self.top.body = urwid.SolidFill(" ")
        self.center = new_center
        if 'loop' in globals():
            loop.set_alarm_in(0.1, self.set_body)
        else:
            self.top.body = self.center

    def set_body(self, a, b):
        self.top.body = self.center

    def exit_game(self, button : classes.ui.ActionButton) -> typing.NoReturn:
        raise urwid.ExitMainLoop()
    
    def unhandled(self, key: str) -> None:
        if key in {"backspace", "delete", "esc"}:
            if self.game != None:
                self.game.back_pressed()
            

if __name__ == "__main__":
    program = Program()
    loop = urwid.MainLoop(program.top, palette=classes.ui.full_palette, unhandled_input=program.unhandled)
    loop.run()