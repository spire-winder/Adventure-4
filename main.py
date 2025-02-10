
import systems.save_system
import typing
import urwid
import time
from classes.game import Game

import data.maps
import classes.ui

import os
os.system('title Adventure 4')

class Program:
    def __init__(self) -> None:
        self.load_ui()
        self.load_main_menu()
    
    def load_ui(self):
        self.header : urwid.Widget = urwid.AttrMap(urwid.Text("Adventure 4", align="center"), "header")
        self.center : urwid.Widget = urwid.Text("")
        self.top : urwid.Frame = urwid.Frame(self.center, header=self.header)

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
        self.namebox : urwid.Edit = urwid.Edit("What is your name, adventurer?\n")
        save_menu_options.append(self.namebox)
        save_menu_options.append(classes.ui.ActionButton("Enter", self.new_game))
        save_menu_options.append(classes.ui.ActionButton("Return", self.load_main_menu))
        save_menu = urwid.ListBox(urwid.SimpleFocusListWalker(save_menu_options))
        self.set_center(save_menu)

    def load_saves(self):
        save_menu_options = []
        for save in systems.save_system.get_saves():
            save_menu_options.append(classes.ui.SaveButton(save, self.load_game, save))
        save_menu_options.append(classes.ui.ActionButton("New Game", self.new_character))
        save_menu_options.append(classes.ui.ActionButton("Return", self.load_main_menu))
        main_menu = urwid.ListBox(urwid.SimpleFocusListWalker(save_menu_options))
        self.set_center(main_menu)
    
    def load_game(self, button : classes.ui.SaveButton):
        self.game : Game = Game(button.save_file)
        self.init_game()

    def new_game(self, button : classes.ui.ActionButton):
        filename : str = self.namebox.get_edit_text()
        if not filename == "":
            self.game : Game = Game(filename)
            self.init_game()
    
    def init_game(self):
        self.connect_signals()
        self.game.start_game()

    def connect_signals(self):
        self.game.set_center_event.subscribe(self.set_center)
        self.game.quit_event.subscribe(self.load_main_menu)

    def clear_center(self):
        self.top.body = urwid.SolidFill(" ")
        if 'loop' in globals():
            loop.draw_screen()
            time.sleep(0.1)  

    def set_center(self, new_center : urwid.Widget):
        self.clear_center()
        self.center = new_center
        self.top.body = self.center

    def exit_game(self, button : classes.ui.ActionButton) -> typing.NoReturn:
        raise urwid.ExitMainLoop()

if __name__ == "__main__":
    program = Program()
    loop = urwid.MainLoop(program.top, palette=classes.ui.full_palette)
    loop.run()