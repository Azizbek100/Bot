import sqlite3

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from data.config import ADMINS
from loader import dp, db, bot
from keyboards.default.menu_bot import main_menu
from aiogram.dispatcher import FSMContext

@dp.message_handler(CommandStart(), state='*')
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    name = message.from_user.full_name
    # Foydalanuvchini bazaga qo'shamiz
    try:
<<<<<<< HEAD
        db.add_user(fullname=name, telegram_id=message.from_user.id, language=message.from_user.language_code)
        await message.answer(f"Здравствуйте,{message.from_user.first_name}!\nЭто бот службы доставки Garage Burger\nОтдел доставки работает 24/7\nВыберите пожалуйста.", reply_markup=main_menu)
=======
        db.add_user(tel_id=message.from_user.id,
                    fullname=name, language=message.from_user.language_code)
        await message.answer(f"Xush kelibsiz! {name}")
>>>>>>> 92a3aa76820dec9efde75530aaeef824966d78ab
        # Adminga xabar beramiz
        count = db.count_users()[0]
        msg = f"{message.from_user.full_name} bazaga qo'shildi.\nBazada {count} ta foydalanuvchi bor."
        await bot.send_message(chat_id=ADMINS[0], text=msg)

    except sqlite3.IntegrityError as err:
        await bot.send_message(chat_id=ADMINS[0], text=f"{name} bazaga oldin qo'shilgan")
        await message.answer(f"Здравствуйте,{message.from_user.first_name}!\nЭто бот службы доставки Garage Burger\nОтдел доставки работает 24/7\nВыберите пожалуйста.", reply_markup=main_menu)


