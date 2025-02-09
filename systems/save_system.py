import pickle
import os
#The filenames of our saved files
save_file_path : str = "data.pkl"


def save_game(game):
    with open(save_file_path, 'wb') as f:
        pickle.dump(game,f)

def has_save() -> bool:
    return os.path.isfile(save_file_path)

def load_save():
    with open(save_file_path, 'rb') as f:
        loaded_game = pickle.load(f)
        return loaded_game