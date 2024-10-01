import configparser
from dataclasses import dataclass, field

from environs import Env

env = Env()
env.read_env()
config = configparser.ConfigParser()
config.read('websocket/ws_config.conf')


@dataclass
class Settings:
    DB_USER: str = field(default_factory=lambda: env("DB_USER"))
    DB_PASS: str = field(default_factory=lambda: env("DB_PASS"))
    DB_HOST: str = field(default_factory=lambda: env("DB_HOST"))
    DB_NAME: str = field(default_factory=lambda: env("DB_NAME"))

    WS_IP: str = config['websocket_server']['ip_address']
    WS_PORT: str = int(config['websocket_server']['port'])
    WS_TOKEN: str = config['websocket_server']['token']
    WS_RUN: bool = config['websocket_server']['run']

    SECRET_AUTH: str = field(default_factory=lambda: env("SECRET_AUTH"))
    ALGORITHM: str = field(default_factory=lambda: env("ALGORITHM"))
    LIFE_TOKEN: int = field(default_factory=lambda: env("LIFE_TOKEN"))

    LOGIN: str = field(default_factory=lambda: env("LOGIN"))
    PASSWORD: str = field(default_factory=lambda: env("PASSWORD"))
