from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery, LabeledPrice
from database import *
from keyboards import *

TOKEN = 'Your telegram bottoken'
PAYMENT = '398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065' #Instead paste your payment token

bot = Bot(TOKEN)

dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def command_start(message: Message):
    await message.answer(f'Здавствуйте {message.from_user.full_name}.\nВас приветствует Бот Афигенный Хавчик')

    await authenticated_or_register_user(message)


async def authenticated_or_register_user(message: Message):
    chat_id = message.chat.id
    user = first_select(chat_id)
    if user:  # Если есть пользователь Авторизуемся
        await message.answer('Авторизация прошла успешно')
        await show_main_menu(message)
    else:  # Если нет то пройдём регистрацию
        await message.answer('Просим пройти регистрацию.\nДля этого нажмите кнопку Поделится контактом',
                             reply_markup=send_contact())


@dp.message_handler(content_types=['contact'])
async def register_user(message: Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    phone = message.contact.phone_number
    try:
        first_register_user(chat_id, full_name, phone)  # Функция для сохранения данных пользователя
        await create_cart_for_user(message)
        await message.answer('Регистрация прошла успешно')
    except:
        await message.answer('Вы уже зарегистрированы')

    await show_main_menu(message)


async def create_cart_for_user(message: Message):
    chat_id = message.chat.id
    try:
        insert_to_cart(chat_id)  # Функция для создания козины пользователя
    except:
        pass


async def show_main_menu(message: Message):
    await message.answer('Выберите направление', reply_markup=generate_main_menu())


#  @dp.message_handler(regexp='✔ Сделать заказ')
@dp.message_handler(lambda message: '✔ Сделать заказ' in message.text)
async def make_order(message: Message):
    await message.answer('Выберите категорию: ', reply_markup=generate_category_menu())


@dp.callback_query_handler(lambda call: 'category' in call.data)
async def show_products(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, category_id = call.data.split('_')
    category_id = int(category_id)
    message_id = call.message.message_id  # Получили id сообщения

    await bot.edit_message_text('Выберите продукт: ', chat_id, message_id,
                                reply_markup=product_by_category(category_id))


@dp.callback_query_handler(lambda call: 'main_menu' in call.data)
async def return_to_category(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выберите категорию: ',
                                reply_markup=generate_category_menu())


@dp.callback_query_handler(lambda call: 'product' in call.data)
async def show_detail_product(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, product_id = call.data.split('_')
    product_id = int(product_id)

    product = get_product_detail(product_id)  # Функция для получения всё о продукте по id продукта
    print(product)

    await bot.delete_message(chat_id, message_id)
    with open(product[-1], mode='rb') as img:
        await bot.send_photo(chat_id=chat_id, photo=img, caption=f'''{product[2]}

Ингридиенты: {product[4]}

Цена: {product[3]}''', reply_markup=generate_product_detail_menu(product_id=product_id, category_id=product[1]))


@dp.callback_query_handler(lambda call: 'back' in call.data)
async def return_to_category_product(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, category_id = call.data.split('_')
    await bot.delete_message(chat_id, message_id)
    await bot.send_message(chat_id, 'Выберите продукт: ', reply_markup=product_by_category(category_id))


@dp.callback_query_handler(lambda call: 'cart' in call.data)
async def add_product_in_product_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, product_id, quantity = call.data.split('_')
    product_id, quantity = int(product_id), int(quantity)

    cart_id = get_user_cart_id(chat_id)  # Функция для получения id карточки по тг id
    product = get_product_detail(product_id)
    print(product)
    final_price = quantity * product[3]

    # Функция для добавления данных о заказе в корзину продуктов или изменения
    if insert_or_update_cart_products(cart_id, product[2], quantity, final_price):
        await bot.answer_callback_query(call.id, 'Продукт успешно добавлен')
    else:
        await bot.answer_callback_query(call.id, 'Количество успешно изменено')


@dp.message_handler(regexp='🛒 Корзина')
async def show_cart(message: Message, edit_message: bool = False):
    chat_id = message.chat.id
    cart_id = get_user_cart_id(chat_id)

    try:
        update_total_products_total_price(cart_id)  # Функция для изменения кол-ва продуктов и суммы в таблице carts
    except Exception as e:
        print(e)
        await message.answer('Корзина не доступна')
        return

    cart_products = get_cart_products(cart_id)  # Функция для получения названия продукта, количества и суммы
    total_products, total_price = get_total_products_total_price(
        cart_id)  # Функция для получения кол-ва и суммы продуктов
    print(cart_products)
    print(total_products, total_price)

    text = 'Ваша корзина: \n\n'
    i = 0
    for product_name, quantity, final_price in cart_products:
        i += 1
        text += f'''{i}. {product_name}
Количество: {quantity}
Общая стоимость: {final_price} сумм\n\n'''

    text += f'''Общее количество продуктов: {0 if total_products is None else total_products}
Сумма заказа составляет: {0 if total_price is None else total_price}'''

    if edit_message:  # Если придёт True
        await bot.edit_message_text(text, chat_id, message.message_id, reply_markup=generate_cart_menu(cart_id))
    else:
        await bot.send_message(chat_id, text, reply_markup=generate_cart_menu(cart_id))


@dp.callback_query_handler(lambda call: 'delete' in call.data)
async def delete_cart_product(call: CallbackQuery):
    _, cart_product_id = call.data.split('_')
    cart_product_id = int(cart_product_id)
    message = call.message

    delete_cart_product_from_database(cart_product_id)  # Функция для удаления продукта из корзины
    await show_cart(message, edit_message=True)


@dp.callback_query_handler(lambda call: 'order' in call.data)
async def create_order(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, cart_id = call.data.split('_')
    cart_id = int(cart_id)

    cart_products = get_cart_products(cart_id)  # Функция для получения названия продукта, количества и суммы
    total_products, total_price = get_total_products_total_price(
        cart_id)  # Функция для получения кол-ва и суммы продуктов
    print(cart_products)
    print(total_products, total_price)

    text = 'Ваша корзина: \n\n'
    i = 0
    for product_name, quantity, final_price in cart_products:
        i += 1
        text += f'''{i}. {product_name}
Количество: {quantity}
Общая стоимость: {final_price} сумм\n\n'''

    text += f'''Общее количество продуктов: {0 if total_products is None else total_products}
Сумма заказа составляет: {0 if total_price is None else total_price}'''

    if total_products is None:
        await bot.answer_callback_query(call.id, 'Корзина пуста. Выберите продукты')
    else:
        await bot.send_invoice(  # Метод для совершения оплаты
            chat_id=chat_id,
            title=f'Заказ №{cart_id}',
            description=text,
            payload='bot-defined invoice payload',
            provider_token=PAYMENT,
            currency='UZS',
            prices=[
                LabeledPrice(label='Общая стоимость', amount=int(total_price * 100)),
                LabeledPrice(label='Доставка', amount=1000000)
            ],
            start_parameter='start_parameter'
        )


@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                        error_message='Ошибка при оплате. Проверьте карту')


@dp.message_handler(content_types=['successful_payment'])
async def get_payment(message: Message):
    chat_id = message.chat.id
    cart_id = get_user_cart_id(chat_id)
    await bot.send_message(chat_id, 'Ваша оплата прошла успешно. Мы вас кинули')
    cart_products = get_cart_products(cart_id)  # Функция для получения названия продукта, количества и суммы
    total_products, total_price = get_total_products_total_price(cart_id)

    save_order_user(cart_id, total_products, total_price)  # Фугкция сохранения заказа
    order_id = get_order_id(cart_id)

    for product_name, quantity, final_price in cart_products:
        save_order_products_user(order_id, product_name, quantity, final_price)  # Функция сохранения продуктов закзаза

    drop_cart_product_default(cart_id)  # Функция для очищения карзины пользователя



executor.start_polling(dispatcher=dp)
