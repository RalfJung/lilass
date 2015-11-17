import os, os.path

def getConfigDirectory():
    d = os.environ.get("XDG_CONFIG_HOME")
    if d:
        return os.path.join(d, "lilass")
    d = os.path.expanduser("~")
    if d:
        return os.path.join(d, ".config", "lilass")
    raise Exception("Couldn't find config directory")

def getDataDirectory():
    d = os.environ.get("XDG_DATA_HOME")
    if d:
        return os.path.join(d, "lilass")
    d = os.path.expanduser("~")
    if d:
        return os.path.join(d, ".local", "share", "lilass")
    raise Exception("Couldn't find data directory.")

def mkdirP(path, mode=0o700):
    os.makedirs(path, mode=mode, exist_ok=True)

