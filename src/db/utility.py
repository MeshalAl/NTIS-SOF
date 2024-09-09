from dotenv import load_dotenv
from pathlib import Path


def load_env():
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)