import asyncio
import re
from typing import Awaitable
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import message, user
from aiogram.utils.callback_data import CallbackData
from datetime import datetime
from aiogram.bot.bot import Bot
from app.handlers.common import Common
import app.helpers.videoHelper as VideoHelper
import requests
import os
import shutil
from asgiref.sync import sync_to_async

available_video_editor_func = ['нарезать видео']
available_video_editor_users = [530098876, 296118129, 413125921, 341194216, 253799141, 331292554]

class EditVideo(StatesGroup):
    waiting_for_video_etidor_func = State()
    waiting_for_cut_video_link = State()
    waiting_for_cut_video_choose_timestamps = State()
    waiting_for_cut_video_choose_cut_or_upload = State()

async def video_editor_start(message: types.Message):
    if message.chat.id not in available_video_editor_users:
        await message.answer("Дружок-пирожок, у тебя нет доступа к этому разделу 🤨")
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_video_editor_func:
        keyboard.add(name)
    await message.answer("Что будем делать?", reply_markup=keyboard)
    await EditVideo.waiting_for_video_etidor_func.set()

async def video_editor_choose_func(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_video_editor_func:
        await message.answer("Не ломайте пожалуйста")
        return

    if message.text.lower() == 'нарезать видео':
        await EditVideo.waiting_for_cut_video_link.set()
        await message.answer("Скиньте ссылку на YouTube видео с таймкодами", reply_markup=types.ReplyKeyboardRemove())

async def cut_youtube_video(message: types.Message, state: FSMContext):
    if "Video unavailable" in requests.get(message.text).text:
        await message.answer("Снова ломаешь?!")
        return

    if await VideoHelper.check_video_1080p(message.text) == None:
        await message.answer("У видео недоступно разрешение 1080p. Проверьте пожалуйста ссылку.")
        return

    timestamps = await VideoHelper.get_timestamps(message.text)
    if timestamps == []:
        await message.answer("У видео нет таймкодов. Добавьте таймкоды или отправьте другое видео.")
        return

    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for timestamp in timestamps:
        keyboard.add(types.InlineKeyboardButton(text = f'❌ {timestamp[2]}', callback_data = timestamp[0]))

    await state.update_data(timestamps=timestamps, add_clips=[], link=message.text)
    await EditVideo.waiting_for_cut_video_choose_timestamps.set()
    await message.answer("Выберите что-нибудь:", reply_markup=keyboard)

async def cut_youtube_video_choose_clips(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    timestamps = user_data['timestamps']
    add_clips = user_data['add_clips']

    if callback_query.data == 'Done':
        if add_clips == []:
            await state.finish()
            await callback_query.message.answer("Ничего не выбрано. Возвращаемся в основное меню(")
            return

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # keyboard.add("Вырезать выбранные отрывки")
        keyboard.add("Вырезать и загрузить на YouTube")
        await EditVideo.waiting_for_cut_video_choose_cut_or_upload.set()
        await callback_query.message.delete()
        await callback_query.message.answer("Что делать?", reply_markup=keyboard)
        return

    if callback_query.data not in add_clips:
        add_clips.append(callback_query.data)
    else:
        add_clips.remove(callback_query.data)
    
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for timestamp in timestamps:
        if timestamp[0] in add_clips:
            keyboard.add(types.InlineKeyboardButton(text = f'✅ {timestamp[2]}', callback_data = timestamp[0]))
        else:
            keyboard.add(types.InlineKeyboardButton(text = f'❌ {timestamp[2]}', callback_data = timestamp[0]))
    keyboard.add(types.InlineKeyboardButton(text="Готово", callback_data="Done"))
    await state.update_data(add_clips = add_clips)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)

async def remove_dir(path_to_dir: str):
    files_in_dir = os.listdir(path_to_dir)
    for file in files_in_dir:                  
        os.remove(f'{path_to_dir}/{file}') 
    
    os.rmdir(path_to_dir) 

async def send_videos(message: types.Message, videos: list):
    for video_path in videos:
        with open(video_path, 'rb') as video:
            await message.answer(text = video_path.rsplit('/', 1)[1])
            await message.answer_document(video)

async def edit_trans_finish_step(message: types.Message, state: FSMContext):
    if message.text != 'Вырезать выбранные отрывки' and message.text != 'Вырезать и загрузить на YouTube':
        await message.answer("Снова ломаешь?!")
        return

    await message.answer(text='Пожалуйста ожидайте', reply_markup=types.ReplyKeyboardRemove())

    user_data = await state.get_data()
    add_clips = user_data['add_clips']
    timestamps = user_data['timestamps']

    cut_clips = []
    for timestamp in timestamps:
        if timestamp[0] in add_clips:
            cut_clips.append(timestamp)

    if (message.text == 'Вырезать выбранные отрывки'):
        videos = await asyncio.create_task(VideoHelper.cut_video(user_data['link'], cut_clips))
        temp_dir = (videos[0])[1].rsplit('/', 1)[0]

        await asyncio.create_task(send_videos(message, videos))
        await state.finish()

        shutil.rmtree(temp_dir)
    else:
        upload_clips = await VideoHelper.cut_video_and_upload(user_data['link'], cut_clips)
        await message.answer(text='Видео загружено на YouTube. Спасибо за ожидание', reply_markup=types.ReplyKeyboardRemove())
        # for clip in upload_clips:
            # await bot.send_message(chat_id=-557652012, text=f'На YouTube загружено видео: {clip[2]}')
        await state.finish()

def register_handlers_video_editor(dp: Dispatcher):
    dp.register_message_handler(video_editor_start, Text(equals="premiere pro", ignore_case=True), state=Common.main_menu)
    dp.register_message_handler(video_editor_choose_func, state=EditVideo.waiting_for_video_etidor_func)
    dp.register_message_handler(cut_youtube_video, state=EditVideo.waiting_for_cut_video_link)
    dp.register_message_handler(edit_trans_finish_step, state=EditVideo.waiting_for_cut_video_choose_cut_or_upload)

    dp.register_callback_query_handler(cut_youtube_video_choose_clips, state=EditVideo.waiting_for_cut_video_choose_timestamps)