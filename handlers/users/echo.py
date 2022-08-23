from aiogram import types

from loader import dp, db, bot
from keyboards.default import menu_bot
from keyboards.inline import call
from states.holatlar import Food
from aiogram.dispatcher import FSMContext
from utils.misc.product import Product
from aiogram.types import LabeledPrice

@dp.message_handler(text='Меню', state='*')
async def send_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Выберите категорию', reply_markup=menu_bot.menu)
    await Food.zakaz.set()

@dp.message_handler(text='Главное меню')
async def send_main_menu(message: types.Message):
    await message.answer('Главное меню', reply_markup=menu_bot.main_menu)

@dp.message_handler(text='📥 Корзина')
async def send_menu(message: types.Message, state: FSMContext):
    if len(db.get_korzinka(message.from_user.id))==0:
        await message.answer('Siz hech narsa buyurtirmadingiz iltimos biror nima buyurtma bering', reply_markup=menu_bot.menu)
        await Food.zakaz.set()
    else:
        a = db.get_korzinka(message.from_user.id)
        # print(a)
        total = 0
        lst = []
        clear_korzinka = types.InlineKeyboardMarkup()
        for i in a:
            msg = f"{i[0]} - {i[1]} x {int(i[2])} = {int(i[1]*i[2])} so'm"
            total += int(i[1]*i[2])
            clear_korzinka.add(types.InlineKeyboardButton(text=f"❌{i[0]}❌", callback_data=f"product:{i[0]}"))
            db.set_call(tel_id=message.from_user.id, calldata=f"product:{i[0]}", product=i[0])
            lst.append(msg)
            # print(f'product:{i[0]}')
        clear_korzinka.add(types.InlineKeyboardButton(text=f"❌Korzinkani tozalash❌", callback_data=f"product:❌Korzinkani tozalash❌"))
        clear_korzinka.add(types.InlineKeyboardButton(text=f"Buyurtma berish🚕", callback_data="deliver"))
        new_msg = ''
        for j in lst:
            new_msg += f'{j}\n'
        new_msg += f"<b>\nUmumiy buyurtma bergan summangiz = {total} so'm</b>"
        # print(new_msg)
        await state.update_data(
            {"total" : total}
        )
        await message.answer(f"{new_msg}", reply_markup=clear_korzinka)
        await Food.cart.set()

@dp.callback_query_handler(text='product:❌Korzinkani tozalash❌', state=Food.cart)
async def clear_zakaz(call: types.CallbackQuery, state: FSMContext):
    # print(call.from_user)
    db.clear_del(call.from_user.id)
    await call.message.delete()
    await call.answer('Korzinka tozalandi', show_alert=True)
    await call.message.answer('Bosh menyu', reply_markup=menu_bot.main_menu)
    await state.finish()


@dp.callback_query_handler(text='deliver', state=Food.cart)
async def clear_zakaz(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    total = data.get('total')
    # print('shu yer')
    db.inserttable(tel_id=call.message.chat.id, name=call.message.chat.first_name, zakaz=call.message.text, total=total)
    # print(call.message.text)
    await call.message.delete()
    db.clear_del(call.message.chat.id)
    await call.answer("Buyurtmalar qismiga qo`shildi✅", show_alert=True)
    await call.message.answer('Buyurtmani tasdiqlashingiz mumkin', reply_markup=menu_bot.main_menu)
    await state.finish()

@dp.callback_query_handler(state=Food.cart)
async def clear_zakaz(call: types.CallbackQuery, state: FSMContext):
    db.clear_current(call.data, call.message.chat.id)
    await call.message.delete()
    await call.answer(f"{call.message.text} o'chirildi✅", show_alert=True)
    await call.message.answer('Korzinka yangilandi', reply_markup=menu_bot.main_menu)
    await state.finish()

@dp.message_handler(text='Мои заказы🗂', state='*')
async def send_main_menu(message: types.Message, state: FSMContext):
    await state.finish()
    try:
        a = db.get_zakaz(message.from_user.id)
        print(a)
        msg = ""
        msg += a[3]
        await state.update_data(
            {'user' : a[0]}
        )
        # menu_bot.markup_pay.add(types.InlineKeyboardButton(text=f"{int(a[-1])} to'lash", callback_data='pay'))
        await message.answer(msg, reply_markup=menu_bot.create_inline(a[0]))
        await Food.verify.set()
    except:
        await message.answer('Siz hech qanday buyurtmani tasdiqlamgansiz\nBuyurtmani tasdqilang', reply_markup=menu_bot.main_menu)

@dp.callback_query_handler(text='next', state=Food.verify)
async def go_next(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    a = db.get_next(user=data.get('user'), tel_id=call.from_user.id)
    print(a)
    if a != None: 
        msg = ""
        msg += a[3]
        await state.update_data(
            {'user' : a[0]}
        )
        await call.message.edit_text(msg, reply_markup=menu_bot.create_inline(a[0]))
    else:
        await call.answer('Bu oxirgi buyurtmangiz')


@dp.callback_query_handler(text='prev', state=Food.verify)
async def go_next(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        a = db.get_prev(user=data.get('user'), tel_id=call.from_user.id)
        print(a)
        b = a[-1]
        print(b)
        if a != None:
            msg = ""
            msg += b[3]
            await state.update_data(
                {'user' : b[0]}
            )
            await call.message.edit_text(msg, reply_markup=menu_bot.create_inline(b[0]))
        else:
            await call.answer('Bu birinchi buyurtmangiz')
    except:
        await call.answer('Bu birinchi buyurtmangiz')
    

@dp.message_handler(text='🚖 Оформить заказ')
async def send_address(message: types.Message, state: FSMContext):
    await message.answer('Отправьте или введите адрес доставки:', reply_markup=menu_bot.location)
    await Food.zakazat.set()

@dp.message_handler(content_types=['contact'], state=Food.zakazat)
async def get_number(message: types.Message, state: FSMContext):
    await message.answer(f'{message.from_user.first_name} - {message.contact.phone_number} raqamingiz saqlandi', reply_markup=menu_bot.main_menu)
    await state.finish()

@dp.message_handler(text='🍔 Бургер', state=Food.zakaz)
async def send_burger(message: types.Message, state:FSMContext):
    await message.answer('Выберите пожалуйста', reply_markup=menu_bot.burgers)
    await Food.zakaznoy.set()

@dp.message_handler(text='Бургер Классический', state=Food.zakaznoy)
async def send_classik(message: types.Message, state: FSMContext):
    product = message.text
    a = db.get_product(product)
    await message.answer_photo(photo=a[2], caption = f"Baxosi: {a[1]} so`m\nTam va to`yimliligiga o`zingiz baxo bering")
    await message.answer('Укажите количество заказа', reply_markup=menu_bot.amountburger)
    await state.update_data(
        {'product' : product, 'price' : a[1]}
    )
    await Food.amount_burger.set()

@dp.message_handler(text='Бургер Двойной', state=Food.zakaznoy)
async def send_double(message: types.Message, state: FSMContext):
    product = message.text
    a = db.get_product(product)
    await message.answer_photo(photo=a[2], caption = f"Baxosi: {a[1]} so`m\nTam va to`yimliligiga o`zingiz baxo bering")
    await message.answer('Укажите количество заказа', reply_markup=menu_bot.amountburger)
    await state.update_data(
        {'product' : message.text, 'price' : a[1]}
    )
    await Food.amount_burger.set()

@dp.message_handler(text='🌭 Хот-Дог', state=Food.zakaz)
async def send_hotdog(message: types.Message):
    await message.answer('Выберите пожалуйста', reply_markup=menu_bot.hotdogs)
    await Food.zakaznoy.set()

@dp.message_handler(text='Хот-Дог', state=Food.zakaznoy)
async def one_hotdog(message: types.Message, state=FSMContext):
    product = message.text
    a = db.get_product(product)
    await message.answer_photo(photo=a[2], caption = f"Baxosi: {a[1]} so`m\nTam va to`yimliligiga o`zingiz baxo bering")
    await message.answer('Укажите количество заказа', reply_markup=menu_bot.amounthotdog)
    await state.update_data(
        {'product' : product, 'price' : a[1]}
    )
    await Food.amount_hotdog.set()

@dp.message_handler(text='Главное меню', state=Food.zakaz)
async def send_main_menu(message: types.Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=menu_bot.main_menu)
    await Food.menu.set()
    await state.finish()

@dp.message_handler(text='Главное меню', state=Food.amount_hotdog)
async def send_main_menu(message: types.Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=menu_bot.main_menu)
    await Food.menu.set()
    await state.finish()

@dp.message_handler(text='Главное меню', state=Food.amount_burger)
async def send_main_menu(message: types.Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=menu_bot.main_menu)
    await Food.menu.set()
    await state.finish()

@dp.message_handler(text='Главное меню', state=Food.amount_drinks)
async def send_main_menu(message: types.Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=menu_bot.main_menu)
    await Food.menu.set()
    await state.finish()

@dp.message_handler(text='Главное меню', state=Food.amount_sous)
async def send_main_menu(message: types.Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=menu_bot.main_menu)
    await Food.menu.set()
    await state.finish()

@dp.message_handler(text='Главное меню', state=Food.amount_ketchup)
async def send_main_menu(message: types.Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=menu_bot.main_menu)
    await Food.menu.set()
    await state.finish()

@dp.message_handler(text='Главное меню', state=Food.amount_chicken)
async def send_main_menu(message: types.Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=menu_bot.main_menu)
    await Food.menu.set()
    await state.finish()

@dp.message_handler(text='Главное меню', state=Food.amount_free)
async def send_main_menu(message: types.Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=menu_bot.main_menu)
    await Food.menu.set()
    await state.finish()

@dp.message_handler(text='Хот-Дог Двойной', state=Food.zakaznoy)
async def double_hotdog(message: types.Message, state: FSMContext):
    hotdog = message.text
    a = db.get_product(hotdog)
    await message.answer_photo(photo=a[2], caption = f"Baxosi: {a[1]} so`m\nTam va to`yimliligiga o`zingiz baxo bering")
    await message.answer('Укажите количество заказа', reply_markup=menu_bot.amounthotdog)
    await state.update_data(
        {'product' : hotdog, 'price' : a[1]}
    )
    await Food.amount_hotdog.set()

@dp.message_handler(text='🍗 Куриные крылышки(острые)', state=Food.zakaz)
async def chicken_wings(message: types.Message, state: FSMContext):
    chicken = message.text
    a = db.get_product(chicken)
    await message.answer_photo(photo=a[2], caption = f"Baxosi: {a[1]} so`m\nTam va to`yimliligiga o`zingiz baxo bering")
    await message.answer('Укажите количество заказа', reply_markup=menu_bot.amountchicken)
    await state.update_data(
        {'product' : chicken, 'price' : a[1]}
    )
    await Food.amount_chicken.set()

@dp.message_handler(text='🍹 Напитки',state=Food.zakaz)
async def drink(message: types.Message):
    await message.answer('Выберите пожалуйста', reply_markup=menu_bot.drinks)
    await Food.zakaznoy.set()

@dp.message_handler(text='Кола 0.5 L', state=Food.zakaznoy)
async def cola(message: types.Message, state: FSMContext):
    drink = message.text
    a = db.get_product(drink)
    await message.answer_photo(photo=a[2], caption = f"Baxosi: {a[1]} so`m\nTam va to`yimliligiga o`zingiz baxo bering")
    await message.answer('Выберите пожалуйста:', reply_markup=menu_bot.amountdrinks)
    await state.update_data(
        {'product' : drink, 'price' : a[1]}
    )
    await Food.amount_drinks.set()

@dp.message_handler(text='Кола 1 L', state=Food.zakaznoy)
async def cola(message: types.Message, state: FSMContext):
    drink = message.text
    a = db.get_product(drink)
    await message.answer_photo(photo=a[2], caption = f"Baxosi: {a[1]} so`m\nTam va to`yimliligiga o`zingiz baxo bering")
    await message.answer('Выберите пожалуйста:', reply_markup=menu_bot.amountdrinks)
    await state.update_data(
        {'product' : drink, 'price' : a[1]}
    )
    await Food.amount_drinks.set()

@dp.message_handler(text='Кола 1.5 L', state=Food.zakaznoy)
async def cola(message: types.Message, state: FSMContext):
    drink = message.text
    a = db.get_product(drink)
    await message.answer_photo(photo=a[2], caption = f"Baxosi: {a[1]} so`m\nTam va to`yimliligiga o`zingiz baxo bering")
    await message.answer('Выберите пожалуйста:', reply_markup=menu_bot.amountdrinks)
    await state.update_data(
        {'product' : drink, 'price' : a[1]}
    )
    await Food.amount_drinks.set()

@dp.message_handler(text='Фанта 0.5 L', state=Food.zakaznoy)
async def send_fanta(message: types.Message, state: FSMContext):
    drink = message.text
    a = db.get_product(drink)
    await message.answer_photo(photo=a[2], caption = f"Baxosi: {a[1]} so`m\nTam va to`yimliligiga o`zingiz baxo bering")
    await message.answer('Выберите пожалуйста:', reply_markup=menu_bot.amountdrinks)
    await state.update_data(
        {'product' : drink, 'price' : a[1]} 
    )
    await Food.amount_drinks.set()

@dp.message_handler(text='Фанта 1 L', state=Food.zakaznoy)
async def send_fanta(message: types.Message, state: FSMContext):
    drink = message.text
    a = db.get_product(drink)
    await message.answer_photo(photo=a[2], caption = f"Baxosi: {a[1]} so`m\nTam va to`yimliligiga o`zingiz baxo bering")
    await message.answer('Выберите пожалуйста:', reply_markup=menu_bot.amountdrinks)
    await state.update_data(
        {'product' : drink, 'price' : a[1]}
    )
    await Food.amount_drinks.set()

@dp.message_handler(text='Фанта 1.5 L', state=Food.zakaznoy)
async def send_fanta(message: types.Message, state: FSMContext):
    drink = message.text
    a = db.get_product(drink)
    await message.answer_photo(photo=a[2], caption = f"Baxosi: {a[1]} so`m\nTam va to`yimliligiga o`zingiz baxo bering")
    await message.answer('Выберите пожалуйста:', reply_markup=menu_bot.amountdrinks)
    await state.update_data(
        {'product' : drink, 'price' : a[1]}
    )
    await Food.amount_drinks.set()

@dp.message_handler(text='Спрайт 0.5 L', state=Food.zakaznoy)
async def send_fanta(message: types.Message, state: FSMContext):
    drink = message.text
    a = db.get_product(drink)
    await message.answer_photo(photo=a[2], caption = f"Baxosi: {a[1]} so`m\nTam va to`yimliligiga o`zingiz baxo bering")
    await message.answer('Выберите пожалуйста:', reply_markup=menu_bot.amountdrinks)
    await state.update_data(
        {'product' : drink, 'price' : a[1]}
    )
    await Food.amount_drinks.set()

@dp.message_handler(text='Спрайт 1 L', state=Food.zakaznoy)
async def send_fanta(message: types.Message, state: FSMContext):
    drink = message.text
    a = db.get_product(drink)
    await message.answer_photo(photo=a[2], caption = f"Baxosi: {a[1]} so`m\nTam va to`yimliligiga o`zingiz baxo bering")
    await message.answer('Выберите пожалуйста:', reply_markup=menu_bot.amountdrinks)
    await state.update_data(
        {'product' : drink, 'price' : a[1]}
    )
    await Food.amount_drinks.set()

@dp.message_handler(text='Спрайт 1.5 L', state=Food.zakaznoy)
async def send_fanta(message: types.Message, state: FSMContext):
    drink = message.text
    a = db.get_product(drink)
    await message.answer_photo(photo=a[2], caption = f"Baxosi: {a[1]} so`m\nTam va to`yimliligiga o`zingiz baxo bering")
    await message.answer('Выберите пожалуйста:', reply_markup=menu_bot.amountdrinks)
    await state.update_data(
        {'product' : drink, 'price' : a[1]}
    )
    await Food.amount_drinks.set()

@dp.message_handler(text='🍟 Дополнительно', state=Food.zakaz)
async def extra(message: types.Message, state: FSMContext):
    await message.answer('Выберите пожалуйста', reply_markup=menu_bot.extra_meals)
    await Food.zakaznoy.set()

@dp.message_handler(text='Картошка Фри', state=Food.zakaznoy)
async def free_potato(message: types.Message, state: FSMContext):
    free = message.text
    a = db.get_product(free)
    await message.answer_photo(photo=a[2], caption=f"Baxosi: {a[1]} so`m")
    await message.answer('Укажите количество заказа', reply_markup=menu_bot.amountfree)
    await state.update_data(
        {'product' : free, 'price' : a[1]}
    )
    await Food.amount_free.set()

@dp.message_handler(text='Фирминни Соус', state=Food.zakaznoy)
async def send_sous(message: types.Message, state: FSMContext):
    sous = message.text
    a = db.get_product(sous)
    await message.answer_photo(photo=a[2], caption=f"Baxosi: {a[1]} so`m")
    await message.answer('Укажите количество заказа', reply_markup=menu_bot.amountsous)
    await state.update_data(
        {'product' : sous, 'price' : a[1]}
    )
    await Food.amount_sous.set()

@dp.message_handler(text='Кетчуп', state=Food.zakaznoy)
async def send_ketchup(message: types.Message, state: FSMContext):
    ketchup = message.text
    a = db.get_product(ketchup)
    await message.answer_photo(photo=a[2], caption=f"Baxosi: {a[1]} so`m")
    await message.answer('Укажите количество заказа', reply_markup=menu_bot.amountketchup)
    await state.update_data(
        {'product' : ketchup, 'price' : a[1]}
    )
    await Food.amount_ketchup.set()

@dp.message_handler(text='⬅️ Назад', state=Food.zakaznoy)
async def back1(message: types.Message, state: FSMContext):
    await message.answer('Выберите пожалуйста', reply_markup=menu_bot.menu)
    await Food.zakaz.set()

@dp.message_handler(text='⬅️ Назад', state=Food.amount_burger)
async def back1(message: types.Message, state: FSMContext):
    await message.answer('Выберите пожалуйста', reply_markup=menu_bot.burgers)
    await Food.zakaznoy.set()
    await state.reset_data()

@dp.message_handler(text='⬅️ Назад', state=Food.amount_hotdog)
async def back1(message: types.Message, state: FSMContext):
    await message.answer('Выберите пожалуйста', reply_markup=menu_bot.hotdogs)
    await Food.zakaznoy.set()
    await state.reset_data()

@dp.message_handler(text='⬅️ Назад', state=Food.amount_drinks)
async def back1(message: types.Message, state: FSMContext):
    await message.answer('Выберите пожалуйста', reply_markup=menu_bot.drinks)
    await Food.zakaznoy.set()
    await state.reset_data()

@dp.message_handler(text='⬅️ Назад', state=Food.amount_chicken)
async def back1(message: types.Message, state: FSMContext):
    await message.answer('Выберите пожалуйста', reply_markup=menu_bot.menu)
    await Food.zakaz.set()
    await state.reset_data()

@dp.message_handler(text='⬅️ Назад', state=Food.amount_free)
async def back1(message: types.Message, state: FSMContext):
    await message.answer('Выберите пожалуйста', reply_markup=menu_bot.extra_meals)
    await Food.zakaznoy.set()
    await state.reset_data()

@dp.message_handler(text='⬅️ Назад', state=Food.amount_sous)
async def back1(message: types.Message, state: FSMContext):
    await message.answer('Выберите пожалуйста', reply_markup=menu_bot.extra_meals)
    await Food.zakaznoy.set()
    await state.reset_data()

@dp.message_handler(text='⬅️ Назад', state=Food.amount_ketchup)
async def back1(message: types.Message, state: FSMContext):
    await message.answer('Выберите пожалуйста', reply_markup=menu_bot.extra_meals)
    await Food.zakaznoy.set()
    await state.reset_data()

@dp.message_handler(state=Food.amount_burger)
async def count(message: types.Message, state: FSMContext):
    try:
        print(message.text)
        if int(message.text) > 0 and int(message.text) < 10:
            await state.update_data(
                {'amount' : int(message.text)}
            )
            data = await state.get_data()
            price = data.get('price')
            product = data.get('product')
            amount = data.get('amount')
            await message.answer(f"{message.text} ta {product} qo`shildi", reply_markup=menu_bot.main_menu)
            # print(data)
            if len(db.check_zakaz(message.from_user.id, pro_name=product))>0:
                b = db.check_zakaz(message.from_user.id, pro_name=product)[0][1]+amount
                # print(b)
                db.update_checked_zakaz(message.from_user.id, prod_name=product, current_amount=b)
                await state.finish()
            elif len(db.check_zakaz(message.from_user.id, pro_name=product))==0:
                db.add_zakaz(tel_id=message.from_user.id, fullname=message.from_user.full_name, product=product, amount=amount, price=price)
                await state.finish()
        else:
            await message.answer("To`g`ri miqdor kiriting")
    except:
        await message.answer('To`g`ri son kiriting')


@dp.message_handler(state=Food.amount_hotdog)
async def count(message: types.Message, state: FSMContext):
    try:
        if int(message.text) > 0 and int(message.text) < 10:
            await state.update_data(
                {'amount' : int(message.text)}
            )
            data = await state.get_data()
            price = data.get('price')
            product = data.get('product')
            amount = data.get('amount')
            await message.answer(f"{message.text} ta {product} qo`shildi", reply_markup=menu_bot.main_menu)
            # print(data)
            # print(len(db.check_zakaz(message.from_user.id, pro_name=product)))
            if len(db.check_zakaz(message.from_user.id, pro_name=product))>0:
                b = db.check_zakaz(message.from_user.id, pro_name=product)[0][1]+amount
                # print(b)
                db.update_checked_zakaz(message.from_user.id, prod_name=product, current_amount=b)
                await state.finish()
            elif len(db.check_zakaz(message.from_user.id, pro_name=product))==0:
                db.add_zakaz(tel_id=message.from_user.id, fullname=message.from_user.full_name, product=product, amount=amount, price=price)
                await state.finish()
        else:
            await message.answer("To`g`ri miqdor kiriting")
    except:
        await message.answer('To`g`ri son kiriting')


@dp.message_handler(state=Food.amount_drinks)
async def count(message: types.Message, state: FSMContext):
    try:
        if int(message.text) > 0 and int(message.text) < 10:
            await state.update_data(
                {'amount' : int(message.text)}
            )
            data = await state.get_data()
            price = data.get('price')
            product = data.get('product')
            amount = data.get('amount')
            await message.answer(f"{message.text} ta {product} qo`shildi", reply_markup=menu_bot.main_menu)
            # print(data)
            if len(db.check_zakaz(message.from_user.id, pro_name=product))>0:
                b = db.check_zakaz(message.from_user.id, pro_name=product)[0][1]+amount
                # print(b)
                db.update_checked_zakaz(message.from_user.id, prod_name=product, current_amount=b)
                await state.finish()
            elif len(db.check_zakaz(message.from_user.id, pro_name=product))==0:
                db.add_zakaz(tel_id=message.from_user.id, fullname=message.from_user.full_name, product=product, amount=amount, price=price)
                await state.finish()
        else:
            await message.answer("To`g`ri miqdor kiriting")
    except:
        await message.answer('To`g`ri son kiriting')


@dp.message_handler(state=Food.amount_free)
async def count(message: types.Message, state: FSMContext):
    try:
        if int(message.text) > 0 and int(message.text) < 10:
            await state.update_data(
                {'amount' : int(message.text)}
            )
            data = await state.get_data()
            price = data.get('price')
            product = data.get('product')
            amount = data.get('amount')
            await message.answer(f"{message.text} ta {product} qo`shildi", reply_markup=menu_bot.main_menu)
            # print(data)
            if len(db.check_zakaz(message.from_user.id, pro_name=product))>0:
                b = db.check_zakaz(message.from_user.id, pro_name=product)[0][1]+amount
                # print(b)
                db.update_checked_zakaz(message.from_user.id, prod_name=product, current_amount=b)
                await state.finish()
            elif len(db.check_zakaz(message.from_user.id, pro_name=product))==0:
                db.add_zakaz(tel_id=message.from_user.id, fullname=message.from_user.full_name , product=product, amount=amount, price=price)
                await state.finish()
            # await state.finish()
        else:
            await message.answer("To`g`ri miqdor kiriting")
    except:
        await message.answer('To`g`ri son kiriting')


@dp.message_handler(state=Food.amount_sous)
async def count(message: types.Message, state: FSMContext):
    try:
        if int(message.text) > 0 and int(message.text) < 10:
            await state.update_data(
                {'amount' : int(message.text)}
            )
            data = await state.get_data()
            price = data.get('price')
            product = data.get('product')
            amount = data.get('amount')
            await message.answer(f"{message.text} ta {product} qo`shildi", reply_markup=menu_bot.main_menu)
            # print(data)
            if len(db.check_zakaz(message.from_user.id, pro_name=product))>0:
                b = db.check_zakaz(message.from_user.id, pro_name=product)[0][1]+amount
                # print(b)
                db.update_checked_zakaz(teleg_id=message.from_user.id, prod_name=product, current_amount=b)
                await state.finish()
            elif len(db.check_zakaz(tel_id=message.from_user.id, pro_name=product))==0:
                db.add_zakaz(tel_id=message.from_user.id, fullname=message.from_user.full_name, product=product, amount=amount, price=price)
                await state.finish()
        else:
            await message.answer("To`g`ri miqdor kiriting")
    except:
        await message.answer('To`g`ri son kiriting')


@dp.message_handler(state=Food.amount_ketchup)
async def count(message: types.Message, state: FSMContext):
    try:
        if int(message.text) > 0 and int(message.text) < 10:
            await state.update_data(
                {'amount' : int(message.text)}
            )
            data = await state.get_data()
            price = data.get('price')
            product = data.get('product')
            amount = data.get('amount')
            await message.answer(f"{message.text} ta {product} qo`shildi", reply_markup=menu_bot.main_menu)
            # print(data)
            if len(db.check_zakaz(tel_id=message.from_user.id, pro_name=product))>0:
                b = db.check_zakaz(tel_id=message.from_user.id, pro_name=product)[0][1]+amount
                # print(b)
                db.update_checked_zakaz(message.from_user.id, prod_name=product, current_amount=b)
                await state.finish()
            elif len(db.check_zakaz(tel_id=message.from_user.id, pro_name=product))==0:
                db.add_zakaz(tel_id=message.from_user.id, fullname=message.from_user.full_name, product=product, amount=amount, price=price)
                await state.finish()
        else:
            await message.answer("To`g`ri miqdor kiriting")
    except:
        await message.answer('To`g`ri son kiriting')


@dp.message_handler(state=Food.amount_chicken)
async def count(message: types.Message, state: FSMContext):
    try:
        if int(message.text) > 0 and int(message.text) < 10:
            await state.update_data(
                {'amount' : int(message.text)}
            )
            data = await state.get_data()
            price = data.get('price')
            product = data.get('product')
            amount = data.get('amount')
            await message.answer(f"{message.text} ta {product} qo`shildi", reply_markup=menu_bot.main_menu)
            # print(data)
            if len(db.check_zakaz(tel_id=message.from_user.id, pro_name=product))>0:
                b = db.check_zakaz(tel_id=message.from_user.id, pro_name=product)[0][1]+amount
                # print(b)
                db.update_checked_zakaz(teleg_id=message.from_user.id, prod_name=product, current_amount=b)
                await state.finish()
            elif len(db.check_zakaz(tel_id=message.from_user.id, pro_name=product))==0:
                db.add_zakaz(tel_id=message.from_user.id, fullname=message.from_user.full_name, product=product, amount=amount, price=price)
                await state.finish()
        else:
            await message.answer("To`g`ri miqdor kiriting")
    except:
        await message.answer('To`g`ri son kiriting')


@dp.callback_query_handler(text_contains='pay', state=Food.verify)
async def get_order_id(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    order_id = call.data.split(':')[1]
    a = db.get_pay_order(call.from_user.id, order_id)
    product = Product(
        title="To'lov qilish uchun quyidagi tugmani bosing",
        description=a[3],
        currency='UZS',
        prices=[
            LabeledPrice(
                label='Barcha buyurtmalar',
                amount=int(a[-1])*100,
            ),
            LabeledPrice(
                label='Yetkazib berish',
                amount=2000000,
            ),
        ],
    start_parameter='create_invoice_products',
    need_email=True,
    need_phone_number=True,
    need_name=True,
    need_shipping_address=True,
    is_flexible=True 
    )
    await bot.send_invoice(call.from_user.id, **product.generate_invoice(), payload='payload:product')
    await call.answer("To'lov qog'ozi")
    await state.update_data(
        {'pay_order_id': order_id}
    )