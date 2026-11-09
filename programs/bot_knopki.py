# 🤖 Второй Telegram-бот — с командами и кнопками
# Умеет: /start (приветствие), /help (подсказка), кнопки под сообщением.
# Каждая строка с комментарием — читай, потом смотри вопросы.

# ── Импорты: как в эхо, + F и фильтры команд, + кнопки ──
# F — фильтр по тексту | Command/CommandStart — фильтры команд
# ReplyKeyboardMarkup — клавиатура снизу | KeyboardButton — одна кнопка
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio

# TOKEN — тот же «пропуск», что у эхо-бота. Вставь свой.
TOKEN = "ВСТАВЬ_СЮДА_ТОКЕН_ОТ_BOTFATHER"

# Bot(token=TOKEN) — создаём бота
bot = Bot(token=TOKEN)
# Dispatcher — решает, кто на что отвечает
dp = Dispatcher()

# get_keyboard — функция, которая ВОЗВРАЩАЕТ клавиатуру с кнопками
def get_keyboard():
    # ReplyKeyboardMarkup — собираем клавиатуру. keyboard — список списков (ряды)
    return ReplyKeyboardMarkup(
        # Внутри: ряд из двух кнопок (KeyboardButton) — «📞 Контакты» и «ℹ️ О боте»
        keyboard=[[KeyboardButton(text="📞 Контакты"),
                   KeyboardButton(text="ℹ️ О боте")]],
        # resize_keyboard=True — кнопки занимают столько места, сколько нужно
        resize_keyboard=True,
    )

# /start — приветствие. reply_markup=get_keyboard() — показать кнопки под сообщением
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!", reply_markup=get_keyboard())

# /help — команда. @dp.message(Command("help")) — реагирует на /help
@dp.message(Command("help"))
async def help_(message: types.Message):
    await message.answer("Нажми кнопку ниже, я отвечу.")

# F.text == "📞 Контакты" — если прислали ИМЕННО такой текст (нажали кнопку)
@dp.message(F.text == "📞 Контакты")
async def contacts(message: types.Message):
    await message.answer("Мой создатель: Алекс.")

# Ещё одна кнопка — «ℹ️ О боте»
@dp.message(F.text == "ℹ️ О боте")
async def about(message: types.Message):
    await message.answer("Я учебный бот: Python + aiogram.")

# main — точка запуска: слушаем сообщения бесконечно
async def main():
    await dp.start_polling(bot)

# if __name__ == '__main__' — запусти main при прямом запуске файла
if __name__ == "__main__":
    asyncio.run(main())
