import re
import shutil
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import message, user
from aiogram.utils.callback_data import CallbackData
from datetime import datetime

from matplotlib.pyplot import title
from handlers.common import Common
import helpers.pictureHelper as PictureHelper
import helpers.videoHelper as VideoHelper
import helpers.youtubeHelper as YoutubeHelper
import requests
import os
from misc import bot
from helpers.keyboardHelper import inline_keyboard_picture_edit

available_picture_types = ['трансляция', 'по ссылке', 'проповедь', 'СНКД', 'YouthPG']
available_picture_trans = ['утро', 'вечер', 'вторник']
available_picture_trans_tue = ['вторник']
available_picture_trans_sun = ['утро', 'вечер']
week = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']

class MakePicture(StatesGroup):
    waiting_for_picture_type = State()
    waiting_for_picture_trans = State()
    waiting_for_picture_link = State()
    waiting_for_picture_photo = State()
    waiting_for_trans_link = State()
    waiting_for_trans_clips = State()
    waiting_for_edit_video = State()
    waiting_for_preacing_title = State()
    waiting_for_preacing_description = State()
    waiting_for_preacing_date = State()
    waiting_for_preacing_edit = State()
    waiting_for_picture_photo_from_link = State()

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
        await message.answer("Скинь ссылку на видео(трансляция, исход или проповедь)", reply_markup=types.ReplyKeyboardRemove())
        await MakePicture.waiting_for_picture_link.set()

    if message.text.lower() == available_picture_types[2]:
        await message.answer("Скинь картинку для фона (как файл)", reply_markup=types.ReplyKeyboardRemove())
        await MakePicture.waiting_for_picture_photo.set()

    if message.text.lower() == available_picture_types[3]:
        await message.answer("Находится в разработке", reply_markup=types.ReplyKeyboardRemove())
        return

    if message.text.lower() == available_picture_types[4]:
        await message.answer("Находится в разработке", reply_markup=types.ReplyKeyboardRemove())
        return

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
    
    picture_info = PictureHelper.get_picture_info(message.text)
    print(picture_info)
    picture_type = picture_info[0]

    picture_path = None

    if (picture_type != 2):
        picture_path = PictureHelper.get_picture_from_link(message.text)
    else:
        await state.update_data(preacher = picture_info[1])
        await state.update_data(title = picture_info[2])
        await state.update_data(date = picture_info[3])
        await state.update_data(video_id = picture_info[4])
        await state.update_data(transparent = 0.5)
        await MakePicture.waiting_for_picture_photo_from_link.set()
        await message.answer("Скинь картинку для фона (как файл)", reply_markup=types.ReplyKeyboardRemove())
        return

    if picture_path:
        picture = open(picture_path, 'rb')
        await message.answer_document(picture, reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        os.remove(picture_path)
    else:
        await message.answer("Не ломай!")
        return

async def picture_preaching_from_link(message, state: FSMContext):
    print(100)
    file_info = await bot.get_file(message.document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    temp_dir = 'preaching_' + datetime.now().strftime("%Y%m%d-%H%M%S")
    os.makedirs(f'temp/{temp_dir}')

    picture_path = f'temp/{temp_dir}/{message.document.file_name}'
    print(picture_path)
    with open(picture_path, 'wb') as new_file:
        new_file.write(downloaded_file.getvalue())

    await state.update_data(picture_path = picture_path)
    user_data = await state.get_data()
    title = user_data['title']
    preacher = user_data['preacher']
    date = user_data['date']
    picture_path = user_data['picture_path']
    transparent = user_data['transparent']

    picture_path = PictureHelper.get_picture_preaching(preacher, title, date, picture_path, transparent)
    picture = open(picture_path, 'rb')
    await MakePicture.waiting_for_preacing_edit.set()
    await message.answer_photo(picture, reply_markup=inline_keyboard_picture_edit)

async def picture_preaching(message, state: FSMContext):
    file_info = await bot.get_file(message.document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    temp_dir = 'preaching_' + datetime.now().strftime("%Y%m%d-%H%M%S")
    os.makedirs(f'temp/{temp_dir}')

    picture_path = f'temp/{temp_dir}/{message.document.file_name}'
    print(picture_path)
    with open(picture_path, 'wb') as new_file:
        new_file.write(downloaded_file.getvalue())

    await state.update_data(picture_path = picture_path)
    await MakePicture.waiting_for_preacing_title.set()
    await message.answer("Введите название проповеди")

async def picture_preaching_title(message: types.Message, state: FSMContext):
    await state.update_data(title = message.text)
    await MakePicture.waiting_for_preacing_description.set()
    await message.answer("Введите ФИ проповедника")

async def picture_preaching_date(message: types.Message, state: FSMContext):
    await state.update_data(preacher = message.text)
    await state.update_data(transparent = 0.5)
    await MakePicture.waiting_for_preacing_date.set()
    await message.answer("Введите дату проповеди в формате: 01 января 2020")

async def picture_preacting_make_and_send(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    title = user_data['title']
    preacher = user_data['preacher']
    date = message.text.lower()
    await state.update_data(date = date)
    picture_path = user_data['picture_path']
    transparent = user_data['transparent']

    picture_path = PictureHelper.get_picture_preaching(preacher, title, date, picture_path, transparent)
    picture = open(picture_path, 'rb')
    await MakePicture.waiting_for_preacing_edit.set()
    await message.answer_photo(picture, reply_markup=inline_keyboard_picture_edit)
    # await state.finish()
    # os.remove(picture_path)

async def picture_preacting_edit(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup = None)
    user_data = await state.get_data()
    title = user_data['title']
    preacher = user_data['preacher']
    date = user_data['date']
    picture_path = user_data['picture_path']
    transparent = user_data['transparent']

    match callback_query.data:
        case 'file':
            picture_path = PictureHelper.get_picture_preaching(preacher, title, date, picture_path, transparent)
            PictureHelper.compress_under_size(2000000, picture_path)
            picture = open(picture_path, 'rb')
            await callback_query.message.delete()
            await callback_query.message.answer_document(picture)
            await state.finish()
            temp_dir = picture_path.rsplit('\\', 1)[0]
            shutil.rmtree(temp_dir)
            return

        case 'youtube':
            picture_path = PictureHelper.get_picture_preaching(preacher, title, date, picture_path, transparent)
            PictureHelper.compress_under_size(2000000, picture_path)
            video_id = user_data['video_id']
            if picture_path:
                YoutubeHelper.upload_thumbnail(video_id, picture_path)
            await callback_query.message.delete()
            await callback_query.message.answer('Картинка загружена на YouTube')
            await state.finish()
            temp_dir = picture_path.rsplit('\\', 1)[0]
            shutil.rmtree(temp_dir)
            return

        case 'dark':
            transparent = transparent -  0.2

        case 'light':
            transparent = transparent +  0.2

    await state.update_data(transparent = transparent)

    picture_path = PictureHelper.get_picture_preaching(preacher, title, date, picture_path, transparent)
    picture = open(picture_path, 'rb')

    await callback_query.message.edit_media(media = types.InputMediaPhoto(picture), reply_markup = inline_keyboard_picture_edit)
            

# async def edit_trans(message: types.Message, state: FSMContext):
#     if "Video unavailable" in requests.get(message.text).text:
#         await message.answer("Снова ломаешь?!")
#         return

#     res = VideoHelper.get_timestamps(message.text)
#     await state.update_data(timestamps=res, add_clips=[], link=message.text)
#     await MakePicture.waiting_for_trans_clips.set()
#     keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     for name in res:
#         print(name)
#         keyboard.add(types.InlineKeyboardButton(text = b'\xE2\x9D\x8C'.decode() + str(name[2]), callback_data = name[0]))
#     keyboard.add(types.InlineKeyboardButton(text="Готово", callback_data="Done"))
#     await message.answer("Выберите что-нибудь:", reply_markup=keyboard)

# async def edit_trans_choose_clips(callback_query: types.CallbackQuery, state: FSMContext):
#     timestamps = (await state.get_data())['timestamps']
#     add_clips = (await state.get_data())['add_clips']
#     print(add_clips)

#     if callback_query.data == 'Done':
#         keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         keyboard.add("Нарезать видео")
#         await MakePicture.waiting_for_edit_video.set()
#         await callback_query.message.delete()
#         await callback_query.message.answer("Что делать?", reply_markup=keyboard)
#         return

#     if callback_query.data not in add_clips:
#         add_clips.append(callback_query.data)
#     else:
#         add_clips.remove(callback_query.data)
    
#     keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     for name in timestamps:
#         if name[0] in add_clips:
#             keyboard.add(types.InlineKeyboardButton(text = b'\xE2\x9C\x85'.decode() + name[2], callback_data = name[0]))
#         else:
#             keyboard.add(types.InlineKeyboardButton(text = b'\xE2\x9D\x8C'.decode() + name[2], callback_data = name[0]))
#     keyboard.add(types.InlineKeyboardButton(text="Готово", callback_data="Done"))
#     await state.update_data(add_clips = add_clips)
#     await callback_query.message.edit_reply_markup(reply_markup=keyboard)

# async def edit_trans_finish_step(message: types.Message, state: FSMContext):
#     if message.text != 'Нарезать видео':
#         await message.answer("Снова ломаешь?!")
#         return
#     await message.answer(text='Пожалуйста ожидайте', reply_markup=types.ReplyKeyboardRemove())
#     user_data = await state.get_data()
#     add_clips = user_data['add_clips']
#     timestamps = user_data['timestamps']

#     if add_clips == []:
#         await message.answer("Хватит ломать бота! Иначе добавим тебя в черный список!")
#         return

#     cut_clips = []
#     for timestamp in timestamps:
#         if timestamp[1] in add_clips:
#             cut_clips.append(timestamp)

#     videos = VideoHelper.cut_video(user_data['link'], cut_clips)

#     temp_dir = videos[0].rsplit('/', 1)[0].strip()

#     print(videos)
#     for video_path in videos:
#         video = open(video_path, 'rb')
#         await message.answer_document(video)
#     os.remove(temp_dir)
#     await state.finish()


def register_handlers_pictures(dp: Dispatcher):
    dp.register_message_handler(picture_start, Text(equals="photoshop", ignore_case=True), state=Common.main_menu)
    dp.register_message_handler(picture_type_chosen, state=MakePicture.waiting_for_picture_type)
    dp.register_message_handler(picture_trans_chosen, state=MakePicture.waiting_for_picture_trans)
    dp.register_message_handler(picture_from_link, state=MakePicture.waiting_for_picture_link)
    dp.register_message_handler(picture_preaching, content_types=['document'], state=MakePicture.waiting_for_picture_photo)
    dp.register_message_handler(picture_preaching_title, state=MakePicture.waiting_for_preacing_title)
    dp.register_message_handler(picture_preaching_date, state=MakePicture.waiting_for_preacing_description)
    dp.register_message_handler(picture_preacting_make_and_send, state=MakePicture.waiting_for_preacing_date)
    dp.register_message_handler(picture_preaching_from_link, content_types=['document'], state=MakePicture.waiting_for_picture_photo_from_link)
    dp.register_callback_query_handler(picture_preacting_edit, state=MakePicture.waiting_for_preacing_edit)
    # dp.register_message_handler(edit_trans, state=MakePicture.waiting_for_trans_link)
    # dp.register_message_handler(edit_trans_finish_step, Text(equals="нарезать видео", ignore_case=True), state=MakePicture.waiting_for_edit_video)
    # dp.register_message_handler(edit_trans_finish_step, commands="Загрузить на ютуб", state=MakePicture.waiting_for_trans_clips)
    # dp.register_callback_query_handler(edit_trans_choose_clips, state=MakePicture.waiting_for_trans_clips)
