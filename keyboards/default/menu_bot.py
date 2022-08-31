from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup


menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🍔 Бургер'), KeyboardButton(text='🌭 Хот-Дог')],
        [KeyboardButton(text='🍗 Куриные крылышки(острые)')],
        [KeyboardButton(text='🍹 Напитки'), KeyboardButton(text='🍟 Дополнительно')],
        [KeyboardButton(text='Главное меню')]
    ]
)
def create_inline(order_id):
    markup_pay = InlineKeyboardMarkup()
    markup_pay.row(InlineKeyboardButton(text='⬅️', callback_data='prev'), InlineKeyboardButton(text='💶', callback_data=f'pay:{order_id}'), InlineKeyboardButton(text='➡️', callback_data='next'))
    return markup_pay

korzinka = InlineKeyboardMarkup()
korzinka.add(InlineKeyboardButton(text='❌Korzinkani tozalash❌', callback_data='clear_cart'))

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row('Меню', '📥 Корзина')
# main_menu.row('🚖 Оформить заказ')
main_menu.row('Mening buyurtmalarim🗂')

burgers = ReplyKeyboardMarkup(resize_keyboard=True)
burgers.row('Бургер Классический', 'Бургер Двойной')
burgers.row('Главное меню', '⬅️ Назад')

amountburger = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
for i in range(1, 10):
    amountburger.insert(str(i))
amountburger.row('Главное меню', '⬅️ Назад')

amounthotdog = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
for i in range(1, 10):
    amounthotdog.insert(str(i))
amounthotdog.row('Главное меню', '⬅️ Назад')

amountdrinks = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
for i in range(1, 10):
    amountdrinks.insert(str(i))
amountdrinks.row('Главное меню', '⬅️ Назад')

amountsous = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
for i in range(1, 10):
    amountsous.insert(str(i))
amountsous.row('Главное меню', '⬅️ Назад')

amountketchup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
for i in range(1, 10):
    amountketchup.insert(str(i))
amountketchup.row('Главное меню', '⬅️ Назад')

amountchicken = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
for i in range(1, 10):
    amountchicken.insert(str(i))
amountchicken.row('Главное меню', '⬅️ Назад')

amountfree = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
for i in range(1, 10):
    amountfree.insert(str(i))
amountfree.row('Главное меню', '⬅️ Назад')

hotdogs = ReplyKeyboardMarkup(resize_keyboard=True)
hotdogs.row('Хот-Дог', 'Хот-Дог Двойной')
hotdogs.row('Главное меню', '⬅️ Назад')

drinks = ReplyKeyboardMarkup(resize_keyboard=True)
drinks.row('Кола 0.5 L', 'Кола 1 L', 'Кола 1.5 L')
drinks.row('Фанта 0.5 L', 'Фанта 1 L', 'Фанта 1.5 L')
drinks.row('Спрайт 0.5 L', 'Спрайт 1 L', 'Спрайт 1.5 L')
drinks.row('Главное меню', '⬅️ Назад')

extra_meals = ReplyKeyboardMarkup(resize_keyboard=True)
extra_meals.row('Картошка Фри')
extra_meals.row('Фирминни Соус', 'Кетчуп')
extra_meals.row('⬅️ Назад')

location = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Lokatsiya yuborish', request_location=True)],
        [KeyboardButton(text='Telefon raqam yuborish', request_contact=True)],
    ], resize_keyboard=True
)