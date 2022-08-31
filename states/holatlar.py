from aiogram.dispatcher.filters.state import StatesGroup, State

class Food(StatesGroup):
    menu = State()
    verify = State()
    order_verify = State()
    finish_order = State()
    zakaz = State()
    cart = State()
    zakaznoy = State()
    zakazat = State()
    litr = State()
    amount_burger = State()
    amount_hotdog = State()
    amount_drinks = State()
    amount_sous = State()
    amount_ketchup = State()
    amount_chicken = State()
    amount_free = State()