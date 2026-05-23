from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'merve_cafe_secret_key_dushanbe_2024'

DATABASE = os.path.join(os.path.dirname(__file__), 'cafe.db')


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        guests INTEGER NOT NULL,
        comment TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        rating INTEGER NOT NULL,
        text TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL
    )''')

    c.execute('SELECT COUNT(*) FROM menu_items')
    if c.fetchone()[0] == 0:
        menu = [
            ('coffee','Эспрессо','Классический насыщенный эспрессо из отборных зёрен',15),
            ('coffee','Американо','Мягкий кофе с горячей водой',18),
            ('coffee','Капучино','Идеальный баланс кофе и нежной молочной пены',25),
            ('coffee','Латте','Кремовый кофе с бархатным молоком',28),
            ('coffee','Макиато','Эспрессо с капелькой молочной пены',22),
            ('coffee','Раф кофе','Сливочный кофе с ванильным сахаром и сливками',32),
            ('coffee','Айс Латте','Освежающий холодный латте со льдом',30),
            ('coffee','Флэт Уайт','Двойной эспрессо с гладким молоком',27),
            ('tea','Зелёный чай','Нежный японский чай сенча',15),
            ('tea','Чёрный чай','Крепкий цейлонский чай',12),
            ('tea','Мятный чай','Освежающий чай с мятой и мёдом',18),
            ('tea','Масала чай','Индийский пряный чай с молоком и специями',22),
            ('tea','Травяной чай','Ромашка, лаванда и имбирь',20),
            ('desserts','Тирамису','Классический итальянский десерт с маскарпоне',38),
            ('desserts','Чизкейк','Нежный сырный торт с ягодным соусом',40),
            ('desserts','Медовик','Традиционный медовый торт со сметанным кремом',32),
            ('desserts','Шоколадный фондан','Тёплый шоколадный кекс с жидкой начинкой',42),
            ('desserts','Макарон','Французские пирожные ассорти (6 шт.)',45),
            ('desserts','Круассан','Хрустящий слоёный круассан',22),
            ('desserts','Эклер','Классический эклер с заварным кремом',30),
            ('breakfast','Яичница с беконом','Классический завтрак с хрустящим беконом и тостом',42),
            ('breakfast','Авокадо тост','Тост с авокадо, яйцом пашот и микрозеленью',48),
            ('breakfast','Блины с ягодами','Нежные блины с сезонными ягодами и сметаной',36),
            ('breakfast','Овсянка с фруктами','Питательная овсянка с фруктами и мёдом',30),
            ('breakfast','Омлет с сыром','Пышный омлет с сыром и зеленью',38),
            ('lunch','Паста Карбонара','Классическая итальянская паста с беконом',68),
            ('lunch','Ризотто с грибами','Сливочное ризотто с лесными грибами',72),
            ('lunch','Куриный салат','Свежий салат с куриным филе и авокадо',52),
            ('lunch','Суп дня','Свежеприготовленный суп из сезонных ингредиентов',35),
            ('lunch','Стейк из лосося','Запечённый лосось с овощами гриль',95),
        ]
        c.executemany('INSERT INTO menu_items (category,name,description,price) VALUES(?,?,?,?)', menu)

    c.execute('SELECT COUNT(*) FROM reviews')
    if c.fetchone()[0] == 0:
        sample = [
            (None,'Алишер К.',5,'Невероятная атмосфера и потрясающий кофе! Обязательно вернусь снова. Лучшее место в Душанбе!'),
            (None,'Нилуфар М.',5,'Лучшее кафе в городе! Тирамису просто тает во рту. Очень уютно и красиво оформлено.'),
            (None,'Рустам Т.',4,'Отличное место для встреч с друзьями. Прекрасный сервис и вкусная еда. Рекомендую всем!'),
            (None,'Зарина Х.',5,'Атмосфера волшебная, кофе божественный. Раф кофе — лучший что я пробовала в жизни!'),
            (None,'Фирдавс Р.',5,'Элегантное место с отличным меню. Всегда приятно приходить сюда после работы.'),
        ]
        c.executemany('INSERT INTO reviews (user_id,name,rating,text) VALUES(?,?,?,?)', sample)

    conn.commit()
    conn.close()


def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    conn = get_db()
    featured = conn.execute("SELECT * FROM menu_items WHERE category='coffee' LIMIT 4").fetchall()
    reviews = conn.execute("SELECT * FROM reviews ORDER BY id DESC LIMIT 3").fetchall()
    conn.close()
    return render_template('index.html', featured=featured, reviews=reviews)


@app.route('/menu')
def menu():
    conn = get_db()
    items = conn.execute('SELECT * FROM menu_items ORDER BY category,id').fetchall()
    conn.close()
    categories = {
        'coffee':   {'name':'Кофе',    'icon':'coffee',   'dishes':[]},
        'tea':      {'name':'Чай',     'icon':'leaf',     'dishes':[]},
        'desserts': {'name':'Десерты', 'icon':'cake',     'dishes':[]},
        'breakfast':{'name':'Завтраки','icon':'sun',      'dishes':[]},
        'lunch':    {'name':'Обеды',   'icon':'utensils', 'dishes':[]},
    }
    for item in items:
        if item['category'] in categories:
            categories[item['category']]['dishes'].append(item)
    return render_template('menu.html', categories=categories)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/booking', methods=['GET','POST'])
@login_required
def booking():
    conn = get_db()
    if request.method == 'POST':
        conn.execute(
            'INSERT INTO bookings (user_id,name,date,time,guests,comment) VALUES(?,?,?,?,?,?)',
            (session['user_id'], request.form['name'], request.form['date'],
             request.form['time'], int(request.form['guests']), request.form.get('comment',''))
        )
        conn.commit()
        flash('Ваш столик забронирован! Ждём вас в МЕРВЕ. 🎉', 'success')
        return redirect(url_for('booking'))
    user_bookings = conn.execute(
        'SELECT * FROM bookings WHERE user_id=? ORDER BY date DESC,time DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('booking.html', user_bookings=user_bookings)


@app.route('/reviews', methods=['GET','POST'])
def reviews():
    conn = get_db()
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Войдите, чтобы оставить отзыв', 'warning')
            return redirect(url_for('login'))
        conn.execute(
            'INSERT INTO reviews (user_id,name,rating,text) VALUES(?,?,?,?)',
            (session['user_id'], request.form['name'],
             int(request.form['rating']), request.form['text'])
        )
        conn.commit()
        flash('Спасибо за ваш отзыв! ⭐', 'success')
        return redirect(url_for('reviews'))
    all_reviews = conn.execute('SELECT * FROM reviews ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('reviews.html', reviews=all_reviews)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE email=? AND password=?',
            (request.form['email'], hash_password(request.form['password']))
        ).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Добро пожаловать, {user["username"]}! ☕', 'success')
            return redirect(url_for('index'))
        flash('Неверный email или пароль', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET','POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        conn = get_db()
        try:
            conn.execute(
                'INSERT INTO users (username,email,password) VALUES(?,?,?)',
                (request.form['username'], request.form['email'],
                 hash_password(request.form['password']))
            )
            conn.commit()
            flash('Регистрация прошла успешно! Войдите в систему.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Пользователь с таким email или именем уже существует', 'error')
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы. До встречи в МЕРВЕ! ☕', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
