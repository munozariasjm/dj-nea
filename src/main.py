from cli import start_dj
from config import load_config

if __name__ == "__main__":
    config = load_config()
    start_dj(config)
