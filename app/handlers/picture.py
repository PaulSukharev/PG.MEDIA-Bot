from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime
import app.helpers.pictureHelper as PictureHelper
import requests
import os

available_picture_types = ['трансляция', 'по ссылке']
available_picture_trans = ['утро', 'вечер', 'вторник']
available_picture_trans_tue = ['вторник']
available_picture_trans_sun = ['утро', 'вечер']
week = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']

class MakePicture(StatesGroup):
    waiting_for_picture_type = State()
    waiting_for_picture_trans = State()
    waiting_for_picture_link = State()
    waiting_for_picture_photo = State()

async def picture_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_picture_types:
        keyboard.add(name)
    await message.answer("Выберите что-нибудь:", reply_markup=keyboard)
    await MakePicture.waiting_for_picture_type.set()

async def picture_type_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_picture_types:
        await message.answer("Хватит ломать бота! Иначе добавим тебя в черный список!")
        return
    await state.update_data(chosen_picture_type=message.text.lower())

    if message.text.lower() == available_picture_types[0]:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        weekday = datetime.today().weekday()

        match weekday:
            case 6:
                buttons = available_picture_trans_sun
            case 1:
                buttons = available_picture_trans_tue
            case _:
                await message.answer(f'Отдыхай, сегодня же {week[weekday]}', reply_markup=types.ReplyKeyboardRemove())
                return

        for name in buttons:
            keyboard.add(name)
        await message.answer("Выберите что-нибудь:", reply_markup=keyboard)
        await MakePicture.waiting_for_picture_trans.set()
    
    if message.text.lower() == available_picture_types[1]:
        await message.answer("Скинь ссылку на видео(трансляция или исход)", reply_markup=types.ReplyKeyboardRemove())
        await MakePicture.waiting_for_picture_link.set()

async def picture_trans_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_picture_trans:
        await message.answer("Снова ломаешь?!")
        return
    await state.update_data(chosen_picture_trans=message.text.lower())

    trans_type = message.text.lower()
    match trans_type:
        case "утро":
            picture_path = PictureHelper.get_picture("УТРЕННЕЕ БОГОСЛУЖЕНИЕ")
        case "вечер":
            picture_path = PictureHelper.get_picture("ВЕЧЕРНЕЕ БОГОСЛУЖЕНИЕ")
        case "вторник":
            picture_path = PictureHelper.get_picture("ВТОРНИЧНОЕ БОГОСЛУЖЕНИЕ")

    picture = open(picture_path, 'rb')
    await message.answer_document(picture, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()
    os.remove(picture_path)

async def picture_from_link(message: types.Message, state: FSMContext):
    if "Video unavailable" in requests.get(message.text).text:
        await message.answer("Снова ломаешь?!")
        return
    
    picture_path = PictureHelper.get_picture_from_link(message.text)

    if picture_path:
        picture = open(picture_path, 'rb')
        await message.answer_document(picture, reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        os.remove(picture_path)
    else:
        await message.answer("Не ломай!")
        return

def register_handlers_pictures(dp: Dispatcher):
    dp.register_message_handler(picture_start, commands="picture", state="*")
    dp.register_message_handler(picture_start, Text(equals="картинки", ignore_case=True), state="*")
    dp.register_message_handler(picture_type_chosen, state=MakePicture.waiting_for_picture_type)
    dp.register_message_handler(picture_trans_chosen, state=MakePicture.waiting_for_picture_trans)
    dp.register_message_handler(picture_from_link, state=MakePicture.waiting_for_picture_link)
