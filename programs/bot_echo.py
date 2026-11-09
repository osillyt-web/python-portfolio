# 🤖 Первый Telegram-бот — «Эхо»
# Отвечает тем же текстом, что ему прислали.
# Каждая строка с комментарием — читай слева направо, как книгу.

# ── Импорты: берём готовые детали из библиотеки aiogram ──
# Bot — сам бот | Dispatcher — «диспетчер», решает кто на что отвечает | types — типы данных
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# импорт для кнопок
# CommandStart — фильтр: реагировать только на команду /start
from aiogram.filters import Command, CommandStart
# asyncio — чтобы бот работал «параллельно» и не замирал
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import json
import asyncio
import socket        # проверка: есть ли хост proxy.server (он есть только в облаке)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


#Блок хранилища
NOTES_FILE = "notes.json"   # имя файла с заметками
# функции хранилища должны быть определены до кода, который их использует
# ⚠️ переживает мусор: нет файла ИЛИ битый/пустой → чистый словарь (урок 20.09)
def load_notes():
    # файла нет ИЛИ он битый/пустой → начинаем с чистого словаря
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return {}

def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=1)

def next_number(notes):
    # словарь пуст → 1; иначе — максимальный номер + 1
    return max((int(n) for n in notes), default=0) + 1

# TOKEN читаем из файла token.txt (рядом с ботом) — секрет не в коде
with open("token.txt", "r", encoding="utf-8") as tf:
    TOKEN = tf.read().strip()   # strip — убрать пробел/перевод строки по краям

# Bot(token=TOKEN) — создаём бота, он умеет отправлять сообщения
# Прокси нужен ТОЛЬКО на PythonAnywhere: там без него нет интернета.
# Локально хоста proxy.server не существует, поэтому сначала проверяем его наличие.
try:
    socket.gethostbyname("proxy.server")          # имя разрешилось → мы в облаке
    session = AiohttpSession(proxy="http://proxy.server:3128")
except OSError:
    session = AiohttpSession()                    # обычный запуск на ПК, без прокси

bot = Bot(token=TOKEN, session=session)
# Dispatcher — решает, какая функция отвечает на какое входящее сообщение
dp = Dispatcher()
def get_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Контакты"),
                   KeyboardButton(text="ℹ️ О боте")]],
        resize_keyboard=True,
    )


# @dp.message(CommandStart()) — «выполни функцию, когда пришлют /start»
@dp.message(CommandStart())
# async def — функция-обработчик. message — это то, что прислал пользователь
async def start(message: types.Message):
    # await message.answer(...) — отправить ответ. from_user.first_name — имя пользователя
    await message.answer(f"Здравствуй, {message.from_user.first_name}!", reply_markup=get_keyboard())

@dp.message(Command("help"))        # ← Command, а не CommandStart
async def help_(message: types.Message):
    await message.answer("Вот что я умею: отвечаю тем же текстом")   # ← свой текст

@dp.message(F.text == "📞 Контакты")
async def contacts(message: types.Message):
    await message.answer("Мой создатель: Алекс.")

@dp.message(F.text == "ℹ️ О боте")
async def about(message: types.Message):
    await message.answer("Я учебный бот: Python + aiogram.")


class Anket(StatesGroup):     # «создай контейнер Anket по готовому шаблону StatesGroup»
    imya = State()            # внутри контейнера — ярлык этапа «ждём имя»
    gorod = State()           # ярлык этапа «ждём город»
    vozrast = State()         # ярлык этапа «ждём возраст»


@dp.message(Command("anketa"))
async def ank_start(message: types.Message, state: FSMContext):
    await state.set_state(Anket.imya)
    await message.answer("Как тебя зовут?")

@dp.message(Anket.imya)
async def ank_imya(message: types.Message, state: FSMContext):
    await state.update_data(imya=message.text)
    await state.set_state(Anket.gorod)
    await message.answer(f"Приятно, {message.text}! Какой город?")

@dp.message(Anket.gorod)
async def ank_gorod(message: types.Message, state: FSMContext):
    await state.update_data(gorod=message.text)
    await state.set_state(Anket.vozrast)
    await message.answer("Сколько тебе лет? (числом)")

@dp.message(Anket.vozrast)
async def ank_vozrast(message: types.Message, state: FSMContext):
    d = await state.get_data()            # достать всё из «кармана»
    await state.clear()                   # сбросить этапы
    await message.answer(f"Готово! {d['imya']}, {d['gorod']}, {message.text} лет.")



# ── КОМАНДА /заметка — сохранить текст в файл ──
# Command("заметка") — реагирует на /заметка
@dp.message(Command("заметка"))
async def add_note(message: types.Message):
    text = message.text[len("/заметка "):].strip()
    if not text:
        await message.answer("Напиши так: /заметка купить хлеб")
        return
    notes = load_notes()
    num = next_number(notes)
    notes[str(num)] = text          # ключ — номер строкой (JSON любит строки)
    save_notes(notes)
    await message.answer(f"Заметка №{num} сохранена!")


# ── КОМАНДА /показать — прочитать все заметки ──
@dp.message(Command("показать"))
async def show_notes(message: types.Message):
    notes = load_notes()
    if not notes:
        await message.answer("Заметок пока нет.")
        return
    for num in sorted(notes, key=int):          # номера по порядку 1,2,3…
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"del_{num}"),
             InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{num}")],
        ])
        await message.answer(f"№{num}: {notes[num]}", reply_markup=kb)


# ── КОМАНДА /очистить — удалить все заметки ──
@dp.message(Command("очистить"))
async def clear_notes(message: types.Message):
    save_notes({})                      # пустой словарь = заметок нет
    await message.answer("Все заметки удалены.")


# ── /menu — сообщение с inline-кнопками ──
# Inline-кнопки = кнопки ВНУТРИ сообщения (не под полем ввода).
# У каждой кнопки callback_data — «метка», которая улетает боту при нажатии.
@dp.message(Command("menu"))
async def menu(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        # один список = один РЯД кнопок
        [InlineKeyboardButton(text="ℹ️ Кто я", callback_data="about")],
        [InlineKeyboardButton(text="🎲 Случайное число", callback_data="random")],
    ])
    await message.answer("Меню:", reply_markup=kb)

# Нажатие на inline-кнопку приходит НЕ как сообщение, а как callback.
# Ловим его по callback_data (F.data == метка кнопки).
@dp.callback_query(F.data == "about")
async def cb_about(call: types.CallbackQuery):
    await call.answer()                 # погасить «часики» на кнопке (обязательно!)
    await call.message.answer("Я бот Алекса, работаю 24/7 на PythonAnywhere.")

# Нажатие на inline-кнопку приходит НЕ как сообщение, а как callback.
# Ловим его по callback_data (F.data == метка кнопки).
@dp.callback_query(F.data == "random")          # 1) какая метка у кнопки «Случайное число»?
async def cb_random(call: types.CallbackQuery):
    await call.answer()                        # 2) что гасим в начале?
    await call.message.answer(f"Твоё число: {random.randint(1, 100)}")  # 3) какой модуль даёт randint?

# Ловим ЛЮБУЮ кнопку удаления: метка начинается с "del_"
@dp.callback_query(F.data.startswith("del_"))
async def cb_delete(call: types.CallbackQuery):
    num = call.data.split("_")[1]      # "del_3" → "3"
    notes = load_notes()
    if num in notes:                    # защита от двойного нажатия
        del notes[num]
        save_notes(notes)
    await call.answer()
    await call.message.answer(f"Заметка №{num} удалена.")
    await call.message.edit_reply_markup(reply_markup=None)   # потушить кнопки у старого сообщения

@dp.callback_query(F.data.startswith("edit_"))     # как ловим семейство?
async def cb_edit(call: types.CallbackQuery):
    num = call.data.split("_")[1]            # как режем и какой кусок?
    await call.answer()
    await call.message.answer(f"Чтобы заменить №{num}, пришли заново: /заметка новый текст")
            # свой текст: как изменить заметку №{num}?


# @dp.message() без фильтра — срабатывает на ЛЮБОЕ сообщение
@dp.message()
async def echo(message: types.Message):
    # message.text — текст, который прислали. Отвечаем этим же текстом (эхо)
    # У голосовых, фото, стикеров текста нет (message.text = None).
    # Без проверки бот падал с ошибкой «text: Input should be a valid string».
    if message.text:
        await message.answer(message.text)

# main — точка запуска: start_polling слушает сообщения бесконечно
async def main():
    await dp.start_polling(bot)

# if __name__ == '__main__' — запусти main, только если файл запускают напрямую
if __name__ == "__main__":
    asyncio.run(main())
