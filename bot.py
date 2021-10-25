import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from picture import Picture

# Объект бота
bot = Bot(token="2062719035:AAG5P7npFV1SZCM0ah9Jbhxtk9zFb6746co")
# Диспетчер для бота
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["УТРО", "ВЕЧЕР", "ВТОРНИК"]
    keyboard.add(*buttons)
    await message.answer("Выбери уже что-нибудь!", reply_markup=keyboard)

@dp.message_handler(Text(equals="УТРО"))
async def cmd_test1(message: types.Message):
    result = Picture.get_picture("УТРЕННЕЕ БОГОСЛУЖЕНИЕ")
    photo = open(result, 'rb')
    await message.answer_document(photo)

@dp.message_handler(Text(equals="ВЕЧЕР"))
async def cmd_test1(message: types.Message):
    result = Picture.get_picture("ВЕЧЕРНЕЕ БОГОСЛУЖЕНИЕ")
    photo = open(result, 'rb')
    await message.answer_document(photo)

@dp.message_handler(Text(equals="ВТОРНИК"))
async def cmd_test1(message: types.Message):
    result = Picture.get_picture("ВТОРНИЧНОЕ БОГОСЛУЖЕНИЕ")
    photo = open(result, 'rb')
    await message.answer_document(photo)

@dp.message_handler(Text(equals="ПРО МОД"))
async def cmd_test1(message: types.Message):
    await message.reply('Заскамили тебя)')

@dp.message_handler()
async def cmd_test1(message: types.Message):
    result = Picture.get_picture_from_link(message.text)
    photo = open(result, 'rb')
    await message.answer_document(photo)

if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)