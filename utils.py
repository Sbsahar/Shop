import json
import os
from datetime import datetime, timedelta
import telebot

PRODUCTS_FILE = "products.json"

def load_products():
    print("جاري تحميل المنتجات...")  # للتأكد من أن الدالة تعمل
    if not os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

def check_blocked_and_clean(bot, user_id):
    try:
        bot.send_chat_action(user_id, "typing")
        return False
    except telebot.apihelper.ApiTelegramException as e:
        if e.description == "Forbidden: bot was blocked by the user":
            products = load_products()
            updated_products = [p for p in products if p["seller_id"] != user_id]
            if len(updated_products) < len(products):
                save_products(updated_products)
                print(f"تم حذف منتجات المستخدم {user_id} لأنه حظر البوت")
            return True
    return False

def clean_expired_products(bot):
    products = load_products()
    current_time = datetime.now()
    updated_products = []
    for product in products:
        creation_date = datetime.strptime(product["created_at"], "%Y-%m-%d %H:%M:%S")
        if current_time - creation_date <= timedelta(days=7):
            if not check_blocked_and_clean(bot, product["seller_id"]):
                updated_products.append(product)
        else:
            if not check_blocked_and_clean(bot, product["seller_id"]):
                bot.send_message(product["seller_id"],
                                 f"عزيزي المستخدم، للأسف لم يتم شراء سلعتك '{product['name']}' خلال 7 أيام.\n"
                                 "تم حذفها من العرض. يمكنك إعادة عرضها مجددًا! 🔄")
    save_products(updated_products)
    return updated_products

def get_currency_display(currency):
    return {"crypto": "عملة مشفرة", "dollar": "دولار", "stars": "نجوم تلغرام", "transfer": "تحويل دولي", "bot_points": "نقاط بوتات", "all": "جميع وسائل الدفع"}[currency]
