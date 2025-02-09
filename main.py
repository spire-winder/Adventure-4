
import systems.save_system
import typing
import urwid
import time
from classes.dungeon import Dungeon

from classes.ui import full_palette
from classes.ui import ActionButton

import os
os.system('title Adventure 4')

class AdventureGame:
    def __init__(self) -> None:
        self.load_ui()
        self.load_main_menu()
    
    def load_ui(self):
        self.header : urwid.Widget = urwid.AttrMap(urwid.Text("Adventure 4", align="center"), "header")
        self.center : urwid.Widget = urwid.Text("")
        self.top : urwid.Frame = urwid.Frame(self.center, header=self.header)

    def load_main_menu(self):
        start_menu_options = []
        systems.save_system.save_file_path = "save.pkl"
        if systems.save_system.has_save():
            start_menu_options.append(ActionButton("Continue", self.load_game))
        start_menu_options.append(ActionButton("New Game", self.new_game))
        start_menu_options.append(ActionButton("Quit", self.exit_game))
        main_menu = urwid.ListBox(urwid.SimpleFocusListWalker(start_menu_options))
        self.set_center(main_menu)
    
    def load_game(self, button : ActionButton):
        systems.save_system.save_file_path = "save.pkl"
        self.dungeon : Dungeon = Dungeon(systems.save_system.load_save())
        self.dungeon.load_game_setup()
        self.init_game()

    def debug_message(self, msg):
        loop.screen.stop()
        print(msg)
        input()
        loop.screen.start()

    def new_game(self, button : ActionButton):
        systems.save_system.save_file_path = "starting_map.pkl"
        self.dungeon : Dungeon = Dungeon(systems.save_system.load_save())
        self.dungeon.new_game_setup()
        self.init_game()
    
    def init_game(self):
        self.connect_signals()
        self.dungeon.start_game()

    def save_game(self):
        systems.save_system.save_file_path = "save.pkl"
        systems.save_system.save_game(game.dungeon.map)
        self.load_main_menu()

    def connect_signals(self):
        self.dungeon.set_center_event.subscribe(self.set_center)
        self.dungeon.save_game_event.subscribe(self.save_game)
        self.dungeon.debug_event.subscribe(self.debug_message)

    def clear_center(self):
        self.top.body = urwid.SolidFill(" ")
        if 'loop' in globals():
            loop.draw_screen()
            time.sleep(0.1)

    def set_center(self, new_center : urwid.Widget):
        self.clear_center()
        self.center = new_center
        self.top.body = self.center

    def exit_game(self, button : ActionButton) -> typing.NoReturn:
        raise urwid.ExitMainLoop()

if __name__ == "__main__":
    game = AdventureGame()
    loop = urwid.MainLoop(game.top, palette=full_palette)
    loop.run()