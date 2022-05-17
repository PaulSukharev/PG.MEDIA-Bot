import logging
from aiogram import Bot, executor, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from config_reader import load_config

logger = logging.getLogger(__name__)
config = load_config("config/bot.ini")

bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot, storage=MemoryStorage())

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/main_menu", description="Вернуться в гланое меню")
    ]
    await bot.set_my_commands(commands)

async def clear_commands():
    commands = [
        BotCommand(command="/main_menu", description="Вернуться в гланое меню")
    ]
    await bot.delete_my_commands()

async def start():
    from handlers.picture import register_handlers_pictures
    from handlers.video_editor import register_handlers_video_editor
    from handlers.common import register_handlers_common

    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    # Парсинг файла конфигурации
    # config = load_config("config/bot.ini")

    # local_server = TelegramAPIServer.from_base('http://localhost')

    # Объявление и инициализация объектов бота и диспетчера
    # bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    register_handlers_common(dp, config.tg_bot.admin_id)
    register_handlers_pictures(dp)
    register_handlers_video_editor(dp)

    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()