"""Seed the database with the auto-admin and rich demo content.

Run:  python seed.py
Idempotent — safe to run multiple times.
"""
from datetime import date, timedelta

from app import create_app
from app.extensions import db
from app.models import (User, LoyaltyPoints, MenuCategory, MenuItem,
                        Gallery, BlogPost, Promotion, SiteContent)

app = create_app()

CATEGORIES = [
    ("Coffee", "coffee", "☕", 1),
    ("Tea", "tea", "🍵", 2),
    ("Desserts", "desserts", "🍰", 3),
    ("Breakfast", "breakfast", "🥐", 4),
    ("Main Dishes", "main", "🍽", 5),
    ("Drinks", "drinks", "🥤", 6),
    ("Premium Specials", "premium", "✦", 7),
]

ITEMS = [
    # slug, title, desc, ingredients, price, kcal, popularity, badge
    ("coffee", "Signature Gold Latte", "Шёлковый латте с золотой пудрой и ванилью бурбон.",
     "Эспрессо, молоко, ваниль, 24k золото", 38, 180, 95, "best"),
    ("coffee", "Cortado Noir", "Двойной эспрессо, уравновешенный тёплым молоком.",
     "Эспрессо, молоко", 26, 120, 80, ""),
    ("coffee", "Affogato Royale", "Эспрессо поверх крем-брюле мороженого.",
     "Эспрессо, мороженое, карамель", 34, 260, 78, "premium"),
    ("coffee", "Iced Caramel Velvet", "Холодный кофе с солёной карамелью и сливками.",
     "Эспрессо, карамель, сливки, лёд", 32, 220, 72, "new"),
    ("tea", "Imperial Jasmine", "Зелёный жасминовый чай ручной скрутки.",
     "Зелёный чай, жасмин", 24, 5, 60, ""),
    ("tea", "Saffron Gold Tea", "Чёрный чай с шафраном и мёдом горных трав.",
     "Чёрный чай, шафран, мёд", 30, 40, 66, "premium"),
    ("tea", "Mint Oasis", "Освежающий марокканский мятный чай.",
     "Зелёный чай, мята, сахар", 22, 30, 55, ""),
    ("desserts", "Pistachio Cloud", "Воздушный фисташковый мусс с малиной.",
     "Фисташка, сливки, малина", 36, 320, 88, "best"),
    ("desserts", "Dark Gold Fondant", "Тёплый шоколадный фондан с золотым листом.",
     "Шоколад 70%, масло, золото", 40, 420, 90, "premium"),
    ("desserts", "Honey Baklava Royale", "Слоёная пахлава с фисташкой и мёдом.",
     "Тесто фило, фисташка, мёд", 28, 380, 70, ""),
    ("breakfast", "Truffle Eggs Benedict", "Яйца бенедикт с трюфельным голландезом.",
     "Яйца, бриошь, трюфель, бекон", 44, 540, 84, "best"),
    ("breakfast", "Avocado Gold Toast", "Тост на закваске с авокадо и пашот.",
     "Авокадо, яйцо, закваска", 34, 410, 75, "new"),
    ("breakfast", "Saffron Shakshuka", "Шакшука с шафраном и фетой.",
     "Яйца, томаты, шафран, фета", 36, 460, 68, ""),
    ("main", "Wagyu Smash Plate", "Вагю-котлета с трюфельным картофелем.",
     "Говядина вагю, картофель, трюфель", 78, 720, 92, "premium"),
    ("main", "Saffron Risotto", "Кремовое ризотто с шафраном и пармезаном.",
     "Рис арборио, шафран, пармезан", 52, 610, 80, ""),
    ("main", "Grilled Sea Bass", "Сибас на гриле с лимонным маслом.",
     "Сибас, лимон, травы", 64, 480, 77, "best"),
    ("drinks", "Pomegranate Spritz", "Игристый гранатовый спритц со льдом.",
     "Гранат, тоник, лайм", 28, 150, 64, "new"),
    ("drinks", "Citrus Gold Fizz", "Цитрусовый лимонад с медом и розмарином.",
     "Лимон, мёд, розмарин, сода", 24, 130, 58, ""),
    ("drinks", "Matcha Frappe", "Холодный матча-фраппе со сливочной пеной.",
     "Матча, молоко, лёд", 30, 210, 69, ""),
    ("premium", "MERVE Tasting Board", "Дегустационный сет шефа: 7 фирменных позиций.",
     "Сет от шефа", 120, 0, 99, "premium"),
    ("premium", "Caviar & Blini Set", "Икра с блинами и сметаной.",
     "Икра, блины, сметана", 145, 380, 86, "premium"),
]

GALLERY = [
    ("Главный зал", "Interior", "placeholder-interior.svg", 1),
    ("Барная стойка", "Interior", "placeholder-coffee.svg", 2),
    ("Фирменный латте", "Drinks", "placeholder-drinks.svg", 3),
    ("Десерты", "Food", "placeholder-desserts.svg", 4),
    ("Завтраки", "Food", "placeholder-breakfast.svg", 5),
    ("Вечерняя атмосфера", "Atmosphere", "placeholder-atmosphere.svg", 6),
    ("VIP-зона", "VIP zone", "placeholder-premium.svg", 7),
    ("Основные блюда", "Food", "placeholder-main.svg", 8),
    ("Чайная церемония", "Drinks", "placeholder-tea.svg", 9),
]

POSTS = [
    ("Новое меню осени в MERVE Café", "new-autumn-menu",
     "Встречайте сезонные новинки: трюфель, шафран и согревающие напитки.",
     "Осень — время насыщенных вкусов. Наша команда шефов представляет новое сезонное "
     "меню, вдохновлённое ароматами Ближнего Востока и европейской классикой. "
     "В центре сезона — трюфель, шафран и тёмный шоколад. Каждое блюдо создано так, "
     "чтобы стать частью атмосферы вечера в MERVE.", "News"),
    ("Искусство латте-арта", "art-of-latte",
     "Как наши бариста создают идеальную чашку каждый день.",
     "За каждой чашкой кофе в MERVE стоит ремесло. Наши бариста проходят обучение "
     "по экстракции, текстуре молока и латте-арту. Мы используем только зёрна "
     "specialty-обжарки и фильтрованную воду, чтобы раскрыть вкус полностью.", "Coffee"),
    ("Вечера живой музыки по пятницам", "friday-live-music",
     "Каждую пятницу — джаз, свечи и фирменные коктейли.",
     "Мы превращаем вечер пятницы в маленький праздник: живой джаз, приглушённый свет, "
     "авторские напитки и особое меню. Бронируйте столик заранее — места ограничены.", "Events"),
]

PROMOS = [
    ("5+1 Кофе бесплатно", "Купите 5 кофе — шестой за наш счёт.", "COFFEE5", 0, True),
    ("VIP вечер -20%", "Скидка 20% на меню в VIP-зоне по будням.", "VIP20", 20, True),
    ("Завтраки -15%", "Скидка на все завтраки до 11:00.", "MORNING15", 15, True),
]

CONTENT = {
    "hero_title": "MERVE Café — Luxury Experience",
    "hero_subtitle": "Место, где вкус, атмосфера и эстетика встречаются.",
    "hero_tagline": "DUSHANBE · FINE DINING & COFFEE",
    "about_text": "MERVE Café — это пространство, где каждая деталь создана с любовью к "
                  "эстетике. Мы соединяем восточное гостеприимство с европейской "
                  "утончённостью, чтобы подарить вам незабываемый опыт.",
    "banner_text": "Открыто ежедневно · 08:00 — 00:00",
}


def run():
    with app.app_context():
        db.create_all()

        # --- auto admin ---
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", role="admin", full_name="MERVE Admin",
                         is_vip=True)
            admin.set_password("merve2026")
            db.session.add(admin)
            db.session.flush()
            db.session.add(LoyaltyPoints(user_id=admin.id, points=0, tier="Platinum"))
            print("✔ Admin created  →  username: admin  password: merve2026")

        # --- demo customer ---
        if not User.query.filter_by(username="guest").first():
            guest = User(username="guest", role="customer", full_name="Гость MERVE")
            guest.set_password("guest123")
            db.session.add(guest)
            db.session.flush()
            db.session.add(LoyaltyPoints(user_id=guest.id, points=320,
                                         coffees_bought=3, tier="Gold"))

        # --- categories ---
        cat_map = {}
        for name, slug, icon, order in CATEGORIES:
            cat = MenuCategory.query.filter_by(slug=slug).first()
            if not cat:
                cat = MenuCategory(name=name, slug=slug, icon=icon, sort_order=order)
                db.session.add(cat)
                db.session.flush()
            cat_map[slug] = cat

        # --- menu items ---
        if MenuItem.query.count() == 0:
            for slug, title, desc, ing, price, kcal, pop, badge in ITEMS:
                db.session.add(MenuItem(
                    category_id=cat_map[slug].id, title=title, description=desc,
                    ingredients=ing, price=price, calories=kcal, popularity=pop,
                    badge=badge))

        # --- gallery ---
        if Gallery.query.count() == 0:
            for title, section, img, order in GALLERY:
                db.session.add(Gallery(title=title, section=section,
                                       image="img/" + img, sort_order=order))

        # --- blog ---
        if BlogPost.query.count() == 0:
            for title, slug, excerpt, body, cat in POSTS:
                db.session.add(BlogPost(
                    title=title, slug=slug, excerpt=excerpt, body=body,
                    category=cat, meta_description=excerpt, published=True))

        # --- promos ---
        if Promotion.query.count() == 0:
            for title, desc, code, disc, active in PROMOS:
                db.session.add(Promotion(
                    title=title, description=desc, code=code,
                    discount_percent=disc, active=active,
                    valid_until=date.today() + timedelta(days=60)))

        # --- site content ---
        for k, v in CONTENT.items():
            if not SiteContent.query.filter_by(key=k).first():
                db.session.add(SiteContent(key=k, value=v))

        db.session.commit()
        print("✔ Database seeded successfully.")
        print("  Menu items:", MenuItem.query.count())
        print("  Categories:", MenuCategory.query.count())


if __name__ == "__main__":
    run()
