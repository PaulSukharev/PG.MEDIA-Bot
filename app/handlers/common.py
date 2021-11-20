from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import IDFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from random import choice

available_main_menu_commands = ['Photoshop', 'Premiere Pro']

#сделать динамически заполняемым
sticker_set = ['CAACAgIAAxkBAAEDSb1hklUxCay07jbXckLBdVzY3KhB4QAClQwAArc5oUi18T2XA385JSIE', 
    'CAACAgIAAxkBAAEDSb9hklVM2KoXAkuMlcHXSWWcU9mFwgACgg8AAk0GqEggs7C059bnZCIE', 
    'CAACAgIAAxkBAAEDScFhklVYbaz_QoJg499raR4H92bhqQAC3wwAAltfqEi9vSXUxV1VYSIE', 
    'CAACAgIAAxkBAAEDScNhklVrDVcJ0ltbTHXDkIFu4Sp4MgACzA0AAjwuqUjiENzznhFZrCIE', 
    'CAACAgIAAxkBAAEDScVhklV45jWJx8PeU-Piuzej4W3kYgACPAwAAu_NsEh9UhvEEnG91SIE', 
    'CAACAgIAAxkBAAEDScdhklWXKJ4rBuDvyTSLHdLSmlMG9QACGw4AAtdIwEhN5ZDN1OKoVCIE',
    'CAACAgIAAxkBAAEDSclhklW8o3TQQmN8CFsgtyTBUNvnOgACrg8AAhGPKUhfeicGyiZjmSIE',
    'CAACAgIAAxkBAAEDScthklXHuVa7rsKzUEI5sHli8MsaowACew4AAud3IUi0NP49_OQ0JCIE',
    'CAACAgIAAxkBAAEDSc1hklXTv2he61n7t7bBsft4AAH_HqQAAj4PAAIukChIVIymnQ101QciBA',
    'CAACAgIAAxkBAAEDSc9hklXeG0kx-1cbZnLuX0WlEG-FNwACEQ4AArV1IEia5Up7rxLSjCIE',
    'CAACAgIAAxkBAAEDSdFhklXud4Fi-dEWqu1uIBbNEKHvAwACwQ4AAvNAIUhYfOn0n92ZTyIE',
    'CAACAgIAAxkBAAEDSdNhklX7u7ii3JAPgZ3-4Ih3vI3_ZwACJxEAAiuOIUguPPFjyjXa7iIE',
    'CAACAgIAAxkBAAEDSdVhklYJk-D6Ev6PuW--6kiWgyz66AACShMAAvtsIEjkmPPoaP2h5iIE',
    'CAACAgIAAxkBAAEDSddhklYWIg8SsIiwXYFKpiscyfkfygACJxAAAohiIEhsP2eKcp-AqSIE',
    'CAACAgIAAxkBAAEDSdlhklYlEwMaCW57IsfDq_hHiNrZjAACGA8AAtXHaEigrdyWY6vp7CIE',
    'CAACAgIAAxkBAAEDSdthklYyEQyFsAERKyqfhzrcoQi_3wACyBAAAjTNyUvP3n8EZ7yjFyIE',
    'CAACAgIAAxkBAAEDSd1hklY8P_FUMFWmUgvbp-m3EG2ajQACRhEAAi_o0EuKhIDSFzLYRiIE',
    'CAACAgIAAxkBAAEDSd9hklZH2wrf7Zp8EU9m9DP2d38Q_QACOBAAAnJWQEj8aeVTWa93USIE']

class Common(StatesGroup):
    main_menu = State()


async def cmd_main_menu(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).row()
    for command in available_main_menu_commands:
        keyboard.insert(command)

    await Common.main_menu.set()  
    await message.answer_sticker(sticker=choice(sticker_set))  
    await message.answer(text=f'Привет привет, {message.chat.first_name}', reply_markup=keyboard)


# Просто функция, которая доступна только администратору,
# чей ID указан в файле конфигурации.
async def secret_command(message: types.Message):
    await message.answer("Поздравляю! Эта команда доступна только администратору бота.")


def register_handlers_common(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(cmd_main_menu, commands="start", state="*")
    dp.register_message_handler(cmd_main_menu, commands="main_menu", state="*")
    dp.register_message_handler(secret_command, IDFilter(user_id=admin_id), commands="abracadabra")