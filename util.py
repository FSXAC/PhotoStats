from pathlib import Path

import osxphotos

def createFolder(dir:str):
    dir_path = Path(dir)
    try:
        dir_path.rmdir()
    except OSError as e:
        pass
    return Path(dir).mkdir(parents=True, exist_ok=True)
