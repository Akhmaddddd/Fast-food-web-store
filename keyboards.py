from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_all_categories, get_products_by_category_id, get_products_for_delete

def send_contact():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='Поделиться контактом', request_contact=True)]
    ], resize_keyboard=True)



def generate_main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='✔ Сделать заказ')],
        [KeyboardButton(text='📋 История заказов'), KeyboardButton(text='🛒 Корзина'), KeyboardButton(text='⚙ Настройки')  ]
    ], resize_keyboard=True)



def generate_category_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton(text='Наше Меню', url='https://telegra.ph/Afigennyj-Havchik-na-Kolyosah-09-13')
    )

    categories = get_all_categories()  # Функция для получения катгорий блюд из Бд
    buttons = []

    for category in categories:
        btn = InlineKeyboardButton(text=category[1], callback_data=f'category_{category[0]}')
        buttons.append(btn)

    markup.add(*buttons)
    return markup




def product_by_category(category_id):
    markup = InlineKeyboardMarkup(row_width=2)
    products = get_products_by_category_id(category_id) # Функция для получения из Бд продуктов по категориии id
    print(products)
    buttons = []

    for product_id, product_name in products:
        btn = InlineKeyboardButton(text=product_name, callback_data=f'product_{product_id}')
        buttons.append(btn)

    markup.add(*buttons)

    markup.row(
        InlineKeyboardButton(text='◀ Назад', callback_data='main_menu')
    )

    return markup




def generate_product_detail_menu(product_id, category_id):
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    for number in range(1, 10):
        btn = InlineKeyboardButton(text=str(number), callback_data=f'cart_{product_id}_{number}')
        buttons.append(btn)

    markup.add(*buttons)

    markup.row(
        InlineKeyboardButton(text='◀ Назад', callback_data=f'back_{category_id}')
    )

    return markup



def generate_cart_menu(cart_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text='🧨 Оформить заказа', callback_data=f'order_{cart_id}')
    )

    cart_products = get_products_for_delete(cart_id)  # Функция для получения названия продуктов и id для удаления

    for cart_product_id, product_name in cart_products:
        markup.row(
            InlineKeyboardButton(text=f'❌ {product_name}', callback_data=f'delete_{cart_product_id}')
        )

    return markup



















