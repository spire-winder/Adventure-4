import pickle
import os
import sys
import pathlib
#The filenames of our saves
save_dir_name : str = "saves"
save_ext : str = ".adventure"

#The filenames of our maps
map_dir_name : str = "maps"
map_ext : str = ".map"

def get_save_filepath(filename : str) -> str:
    return os.path.join(save_dir_name, filename + save_ext)

def get_saves() -> list:
    files : list[str] = os.listdir(save_dir_name)
    validsaves : list[str] = []
    for x in files:
        if pathlib.Path(x).suffix == save_ext:
            validsaves.append(os.path.splitext(os.path.basename(x))[0])
    return validsaves

def has_saves() -> bool:
    return len(get_saves()) > 0

def save_game(filename : str, game):
    with open(get_save_filepath(filename), 'wb') as f:
        pickle.dump(game,f)

def has_save_of_name(filename : str) -> bool:
    return os.path.isfile(get_save_filepath(filename))

def load_save(filename : str):
    with open(get_save_filepath(filename), 'rb') as f:
        loaded_game = pickle.load(f)
        return loaded_game

def get_map_filepath(filename : str) -> str:
    return os.path.join(map_dir_name, filename + map_ext)

def save_map(filename : str, game):
    with open(get_map_filepath(filename), 'wb') as f:
        pickle.dump(game,f)

def load_map(filename : str):
    with open(get_map_filepath(filename), 'rb') as f:
        loaded_game = pickle.load(f)
        return loaded_game

def create_folder(folder_name):
        # Create the directory
        try:
            os.mkdir(folder_name)
            #print(f"Directory '{directory_name}' created successfully.")
        except FileExistsError:
            pass
            #print(f"Directory '{directory_name}' already exists.")
        except PermissionError:
            sys.exit(f"Permission denied: Unable to create '{folder_name}'.")
        except Exception as e:
            sys.exit(f"An error occurred: {e}")