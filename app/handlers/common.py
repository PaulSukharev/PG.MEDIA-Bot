from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import IDFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from random import choice

from misc import clear_commands, bot

available_main_menu_commands = ['Photoshop', 'Premiere Pro']
# available_main_menu_commands = ['я обиделся']

nasty_id = 975613790

class Common(StatesGroup):
    main_menu = State()
    not_active = State()


async def cmd_main_menu(message: types.Message, state: FSMContext):
    if (message.chat.type != 'private'):
        await Common.not_active.set()
        await message.answer('Пасхалки пока нет', reply_markup=types.ReplyKeyboardRemove())
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).row()
    for command in available_main_menu_commands:
        keyboard.insert(command)

    sticker_set = await bot.get_sticker_set('pg.media')
    choice_sticker = choice(sticker_set['stickers'])
    await Common.main_menu.set()  
    await message.answer_sticker(sticker=choice_sticker['file_id'])  
    await message.answer(text=f'Привет привет, {message.chat.first_name}', reply_markup=keyboard)


# Просто функция, которая доступна только администратору,
# чей ID указан в файле конфигурации.
async def secret_command(message: types.Message):
    await message.answer("Поздравляю! Эта команда доступна только администратору бота.")


def register_handlers_common(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(cmd_main_menu, commands="start", state="*")
    dp.register_message_handler(cmd_main_menu, commands="main_menu", state="*")
    dp.register_message_handler(secret_command, IDFilter(user_id=admin_id), commands="abracadabra")