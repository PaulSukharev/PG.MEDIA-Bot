import json
import configparser
from dataclasses import dataclass
from typing import List


@dataclass
class TgBot:
    token: str
    white_list: List[str]


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config["tg_bot"]

    return Config(
        tg_bot=TgBot(
            token=tg_bot["token"],
            white_list=json.loads(tg_bot["white_list"])
            )
        )
    