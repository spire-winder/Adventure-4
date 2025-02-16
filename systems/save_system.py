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
    return os.path.join(save_dir_name, f"{filename}{save_ext}")

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
        f.close()

def delete_game(filename : str):
    try:
        os.remove(get_save_filepath(filename))
    except:
        pass

def has_save_of_name(filename : str) -> bool:
    return os.path.isfile(get_save_filepath(filename))

def load_save(filename : str):
    with open(get_save_filepath(filename), 'rb') as f:
        loaded_game = pickle.load(f)
        f.close()
        return loaded_game

def get_map_filepath(filename : str) -> str:
    return os.path.join(map_dir_name, f"{filename}{map_ext}")

def save_map(filename : str, game):
    with open(get_map_filepath(filename), 'wb') as f:
        pickle.dump(game,f)
        f.close()

def load_map(filename : str):
    with open(get_map_filepath(filename), 'rb') as f:
        loaded_game = pickle.load(f)
        f.close()
        return loaded_game

def create_folder(folder_name):
    os.makedirs(folder_name, exist_ok=True)