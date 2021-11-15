import json
import configparser
from dataclasses import dataclass
from typing import List


@dataclass
class TgBot:
    token: str
    admin_id: int
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
            admin_id=int(tg_bot["admin_id"]),
            white_list=json.loads(tg_bot["white_list"])
            )
        )
    