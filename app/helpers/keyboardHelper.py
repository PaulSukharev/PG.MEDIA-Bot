from aiogram import types

inline_keyboard_picture_edit = types.InlineKeyboardMarkup()
# keyboard.add(types.InlineKeyboardButton('Тема', callback_data='title'))
# keyboard.add(types.InlineKeyboardButton('ФИ проповедника', callback_data='preacher'))
# keyboard.add(types.InlineKeyboardButton('Дата', callback_data='date'))
inline_transparent_dark = types.InlineKeyboardButton('Темнее', callback_data='dark')
inline_transparent_light = types.InlineKeyboardButton('Светлее', callback_data='light')
inline_keyboard_picture_edit.row(inline_transparent_dark, inline_transparent_light)
inline_keyboard_picture_edit.add(types.InlineKeyboardButton('Редактировать тему', callback_data='title'))
inline_keyboard_picture_edit.add(types.InlineKeyboardButton('Получить файл', callback_data='file'))
inline_keyboard_picture_edit.add(types.InlineKeyboardButton('Загрузить на YouTube', callback_data='youtube'))