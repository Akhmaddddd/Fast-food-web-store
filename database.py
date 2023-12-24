import sqlite3


def create_users_table():
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        telegram_id BIGINT NOT NULL UNIQUE,
        phone TEXT
    );
    ''')
    database.commit()
    database.close()

# create_users_table()


def create_carts_table():
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carts(
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(user_id),
        total_price DECIMAL(12, 2) DEFAULT 0, 
        total_products INTEGER DEFAULT 0
    );
    ''')
    database.commit()
    database.close()

# create_carts_table()




def create_cart_products_table():
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart_products(
        cart_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id INTEGER REFERENCES carts(cart_id),
        product_name VARCHAR(100) NOT NULL,
        quantity INTEGER NOT NULL,
        final_price DECIMAL(12, 2) NOT NULL,
        
        UNIQUE(cart_id, product_name)
    );
    ''')
    database.commit()
    database.close()


# create_cart_products_table()


def create_categories_table():
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories(
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name VARCHAR(50) NOT NULL UNIQUE
    );
    ''')
    database.commit()
    database.close()


# create_categories_table()


def insert_categories():
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO categories(category_name) VALUES
    ('Лавашы'),
    ('Бургеры'),
    ('Хот-Доги'),
    ('Пицца'),
    ('Соусы'),
    ('Напитки')
    ''')
    database.commit()
    database.close()

# insert_categories()



def create_products_table():
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products(
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER  NOT NULL,
        product_name VARCHAR(100) NOT NULL UNIQUE,
        price DECIMAL(12, 2) NOT NULL,
        description VARCHAR(150),
        image TEXT,
        FOREIGN KEY(category_id) REFERENCES categories(category_id)
    );
    ''')
    database.commit()
    database.close()

# create_products_table()


def insert_products_table():
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO products(category_id, product_name, price, description, image) VALUES
    (1, 'Лаваш говяжий', 30000, 'Мясо говяжье, тесто, помидоры, огурчики, чипсы, соус', 'media/lavash/lavash_1.jpg'),
    (1, 'Лаваш куриный', 28000, 'Мясо куриное, тесто, помидоры, огурчики, чипсы, соус', 'media/lavash/lavash_2.jpg'),
    (1, 'Лаваш с сыром', 32000, 'Мясо говяжье, тесто, помидоры, огурчики, чипсы, соус, сыр', 'media/lavash/lavash_3.jpg')
    ''')

    database.commit()
    database.close()

# insert_products_table()



# Функция для получения пользователя по тг id
def first_select(chat_id):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM users WHERE telegram_id = ?;
    ''', (chat_id,))
    user = cursor.fetchone()
    database.close()
    return user


def first_register_user(chat_id, full_name, phone):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO users(telegram_id, full_name, phone) VALUES(?, ?, ?)
    ''', (chat_id, full_name, phone))
    database.commit()
    database.close()



def insert_to_cart(chat_id):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO carts(user_id) VALUES
    (  
        (SELECT user_id FROM users WHERE telegram_id = ?) 
    )
    ''', (chat_id,))
    database.commit()
    database.close()


# Функ для получ всего из таблицы категорий
def get_all_categories():
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM categories;
    ''')
    categories = cursor.fetchall()
    database.close()
    return categories



# Функция для получения id продуктов и названия продуктов по category_id
def get_products_by_category_id(category_id):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT product_id, product_name FROM products
    WHERE category_id = ?
    ''', (category_id,))
    products = cursor.fetchall()
    database.close()
    return products




def get_product_detail(product_id):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM products WHERE product_id = ?
    ''', (product_id,))
    product = cursor.fetchone()
    database.close()
    return product


def get_user_cart_id(chat_id):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT cart_id FROM carts
    WHERE user_id = ( SELECT user_id FROM users WHERE telegram_id = ? )
    ''', (chat_id, ))
    cart_id = cursor.fetchone()[0]
    database.close()
    return cart_id



def insert_or_update_cart_products(cart_id, product_name, quantity, final_price):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    try:  # Если продукт добавлется в корзину продуктов
        cursor.execute('''
        INSERT INTO cart_products(cart_id, product_name, quantity, final_price)
        VALUES(?, ?, ?, ?)
        ''', (cart_id, product_name, quantity, final_price))
        database.commit()
        return True

    except:
        cursor.execute('''
        UPDATE cart_products
        SET quantity = ?,
        final_price = ?
        WHERE product_name = ? AND cart_id = ?
        ''', (quantity, final_price, product_name, cart_id))
        database.commit()
        return False

    finally:
        database.close()




def update_total_products_total_price(cart_id):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    UPDATE carts
    SET total_products = (SELECT SUM(quantity) FROM cart_products WHERE cart_id = :cart_id),
    total_price = (SELECT SUM(final_price) FROM cart_products WHERE cart_id = :cart_id)
    WHERE cart_id = :cart_id
    ''', {'cart_id': cart_id})
    database.commit()
    database.close()


def get_cart_products(cart_id):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT product_name, quantity, final_price 
    FROM cart_products WHERE cart_id = ?
    ''', (cart_id,))
    cart_products = cursor.fetchall()
    database.close()
    return cart_products


def get_total_products_total_price(cart_id):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT total_products, total_price FROM carts
    WHERE cart_id = ?
    ''', (cart_id,))
    total_products, total_price = cursor.fetchone()
    database.close()
    return total_products, total_price


def get_products_for_delete(cart_id):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT cart_product_id, product_name
    FROM cart_products WHERE cart_id = ?
    ''', (cart_id,))
    cart_products = cursor.fetchall()
    database.close()
    return cart_products



def delete_cart_product_from_database(cart_product_id):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    DELETE FROM cart_products WHERE cart_product_id = ?
    ''', (cart_product_id,))
    database.commit()
    database.close()


def drop_cart_product_default(cart_id):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    DELETE FROM cart_products WHERE cart_id = ?
    ''', (cart_id,))
    database.commit()
    database.close()




def save_order():
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders(
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        total_price DECIMAL(12, 2) DEFAULT 0, 
        total_products INTEGER DEFAULT 0,
        cart_id INTEGER REFERENCES carts(cart_id) 
    );
    ''')
    database.commit()
    database.close()



def save_products_order():
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products_order(
        product_order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name VARCHAR(50) not null,
        quantity INTEGER,
        final_price DECIMAL(12, 2) NOT NULL,
        order_id INTEGER REFERENCES orders(order_id)
    )
    ''')
    database.commit()
    database.close()




# save_order()
# save_products_order()



def save_order_user(cart_id, total_products, total_price):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO orders(cart_id, total_products, total_price)
    VALUES(?, ?, ?)
    ''', (cart_id, total_products, total_price))
    database.commit()
    database.close()


def get_order_id(cart_id):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT order_id FROM orders
    WHERE cart_id = ?
    ''', (cart_id,))
    order_id = cursor.fetchone()[0]
    database.close()
    return order_id


def save_order_products_user(order_id, product_name, quantity, final_price):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO products_order(order_id, product_name, quantity, final_price)
    VALUES(?, ?, ?, ?)
    ''', (order_id, product_name, quantity, final_price))
    database.commit()
    database.close()




def name_for_history(cart_id):
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM orders WHERE cart_id=?
    ''',(cart_id,))
    chek=cursor.fetchall()

    database.close()
    return chek[0][0],chek[0][1],chek[0][2]


def additional_name_for_history(order_id):
    history_chek=[]
    database = sqlite3.connect('havchik.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM products_order WHERE order_id=?
    ''',(order_id,))
    chek=cursor.fetchall()

    database.close()
    return chek










