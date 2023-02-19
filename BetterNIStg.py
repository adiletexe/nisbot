import logging
import sqlite3
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '6038200186:AAH4Bv_BV8X8YZ96ny2wEawqlMVWUF8SOcM'

conn = sqlite3.connect('nisbot.db', check_same_thread=False)
cursor = conn.cursor()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
adilet_id = 928960596
choice = 'Nothing'

class Adilet(StatesGroup):
    question1 = State()
    question2 = State()

class IT(StatesGroup):
    question1 = State()
    question2 = State()


@dp.message_handler(commands='start')
async def start_test(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    adilet_button = KeyboardButton('Мисс Магрипе')
    it_specialist_button = KeyboardButton('IT специалисту')
    markup.row(adilet_button, it_specialist_button)
    await message.answer(f"Привет, {message.from_user.full_name}! Кому вы хотите сообщить о проблеме?", reply_markup=markup)

    await Adilet.question1.set()

@dp.message_handler(commands='start', state='*')
async def reset_state(message: types.Message, state: FSMContext):
    await state.finish()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    adilet_button = KeyboardButton('Мисс Магрипе')
    it_specialist_button = KeyboardButton('IT специалисту')
    markup.row(adilet_button, it_specialist_button)
    await message.answer(f"Привет, {message.from_user.full_name}! Кому вы хотите сообщить о проблеме?", reply_markup=markup)

    await Adilet.question1.set()

@dp.message_handler(state=Adilet.question1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text
    global choice
    await state.update_data(answer1=answer)
    if message.text.lower() == 'мисс магрипе':
        choice = 'Мисс Магрипа'
        await Adilet.question2.set()
        await message.answer("Детально опишите проблему")
    elif message.text.lower() == 'it специалисту':
        choice = 'IT специалист'
        await IT.question2.set()
        await message.answer("Детально опишите проблему")


@dp.message_handler(state=IT.question2)
async def answer_q2(message: types.Message, state: FSMContext):
    answer = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    adilet_button = KeyboardButton('Мисс Магрипе')
    it_specialist_button = KeyboardButton('IT специалисту')
    markup.row(adilet_button, it_specialist_button)
    await bot.forward_message(chat_id=adilet_id, from_chat_id=message.chat.id, message_id=message.message_id)
    await state.finish()
    cursor.execute('INSERT INTO nisbot (name, problem, address) VALUES (?, ?, ?)',
                   (message.from_user.full_name, message.text, choice))
    conn.commit()
    await message.answer(f"Спасибо, ваша проблема отправлена IT специалисту. Если хотите отправить новую проблему выберите адресат:", reply_markup=markup)
    await Adilet.question1.set()

@dp.message_handler(state=Adilet.question2)
async def answer_q2(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    adilet_button = KeyboardButton('Мисс Магрипе')
    it_specialist_button = KeyboardButton('IT специалисту')
    markup.row(adilet_button, it_specialist_button)
    await bot.forward_message(chat_id=adilet_id, from_chat_id=message.chat.id, message_id=message.message_id)
    await state.finish()
    cursor.execute('INSERT INTO nisbot (name, problem, address) VALUES (?, ?, ?)', (message.from_user.full_name, message.text, choice))
    conn.commit()
    await message.answer(f"Спасибо, ваша проблема отправлена Мисс Магрипе. Если хотите отправить новую проблему выберите адресат:", reply_markup=markup)
    await Adilet.question1.set()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)