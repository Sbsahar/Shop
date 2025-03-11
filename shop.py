import telebot
from telebot import types
import json
import os
from datetime import datetime, timedelta
import time

# إعداد البوت
bot = telebot.TeleBot("7383597510:AAHsQBH05yVEN96rL783BDkRD1YO1yXY1R4")
ADMIN_GROUP_CHAT_ID = "-1002482962804"
PRODUCTS_FILE = "products.json"
PRODUCTS_PER_PAGE = 5
DEVELOPER_ID = "6789179634"

user_data = {}
user_ids = set()

# تحميل المنتجات
def load_products():
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

# حفظ المنتجات
def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

# التحقق من حظر المستخدم وحذف سلعه
def check_blocked_and_clean(user_id):
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

# تنظيف المنتجات المنتهية أو للمستخدمين المحظورين
def clean_expired_products():
    products = load_products()
    current_time = datetime.now()
    updated_products = []
    for product in products:
        creation_date = datetime.strptime(product["created_at"], "%Y-%m-%d %H:%M:%S")
        if current_time - creation_date <= timedelta(days=7):
            if not check_blocked_and_clean(product["seller_id"]):
                updated_products.append(product)
        else:
            if not check_blocked_and_clean(product["seller_id"]):
                bot.send_message(product["seller_id"],
                                 f"عزيزي المستخدم، للأسف لم يتم شراء سلعتك '{product['name']}' خلال 7 أيام.\n"
                                 "تم حذفها من العرض. يمكنك إعادة عرضها مجددًا! 🔄")
    save_products(updated_products)
    return updated_products

# الترحيب
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_ids.add(message.from_user.id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_sell = types.InlineKeyboardButton("اعرض منتجك للبيع", callback_data="sell")
    btn_buy = types.InlineKeyboardButton("شراء منتج متوافر", callback_data="buy")
    btn_stats = types.InlineKeyboardButton("الإحصائيات 📊", callback_data="stats")
    btn_channel = types.InlineKeyboardButton("قناة الإعلانات 📢", url="https://t.me/QUEEN_SH963")
    btn_dev = types.InlineKeyboardButton("المطور", url="https://t.me/SB_SAHAR")
    markup.add(btn_sell, btn_buy)
    markup.add(btn_stats, btn_channel)
    markup.add(btn_dev)
    
    bot.reply_to(message,
                 "أهلاً بك في بوت *متجرك*! 👋\n"
                 "يمكنك من خلال هذا البوت عرض سلعتك للبيع أو شراء سلعة متوافرة.\n"
                 "اختر من الأزرار أدناه ⬇️\n\n"
                 "للمزيد من المعلومات، استخدم /help\n"
                 "للبحث عن سلعة، استخدم /search\n"
                 "لمعلومات عن طلب، استخدم /info",
                 parse_mode="Markdown", reply_markup=markup)

# الأمر /help
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message,
                 "📖 *دليل استخدام بوت متجرك*\n\n"
                 "1️⃣ *اعرض منتجك للبيع*: اختر الزر، أدخل اسم المنتج، السعر، نوع العملة، ومعلومات إضافية إذا رغبت.\n"
                 "2️⃣ *شراء منتج*: تصفح المنتجات المتوفرة واضغط 'شراء' للتواصل مع البائع.\n"
                 "3️⃣ سيتم إرسال طلبات البيع للمشرفين للموافقة.\n"
                 "4️⃣ هناك مشرفين ووسطاء مسؤولين عن البوت، كل العمليات تتم عبر وسطاء موثوقين، حقك مضمون! ✅\n\n"
                 "ابدأ بـ /start\n"
                 "ابحث بـ /search\n"
                 "استعلم عن طلب بـ /info",
                 parse_mode="Markdown")

# أمر /info لعرض معلومات الطلب
@bot.message_handler(commands=['info'])
def show_product_info(message):
    try:
        product_id = int(message.text.split()[1])
        products = clean_expired_products()
        for product in products:
            if product["product_id"] == product_id:
                currency = {"crypto": "عملة مشفرة", "dollar": "دولار", "stars": "نجوم تلغرام", "transfer": "تحويل دولي", "bot_points": "نقاط بوتات", "all": "جميع وسائل الدفع"}[product['currency']]
                extra_info = product.get("extra_info", "لا توجد معلومات إضافية")
                bot.reply_to(message,
                             f"📦 معلومات الطلب رقم {product_id}:\n"
                             f"اسم المنتج: {product['name']}\n"
                             f"💵 السعر: {product['price']}\n"
                             f"💸 العملة: {currency}\n"
                             f"ℹ️ معلومات إضافية: {extra_info}\n"
                             f"🕒 تاريخ العرض: {product['created_at']}",
                             parse_mode="Markdown")
                return
        bot.reply_to(message, "عذرًا، هذا الطلب غير موجود! ربما تم بيعه أو حذفه 🔍")
    except (IndexError, ValueError):
        bot.reply_to(message, "يرجى إدخال رقم الطلب بشكل صحيح، مثال: /info 123")

# أمر الحذف للمطور
@bot.message_handler(commands=['delete'])
def delete_product(message):
    if str(message.from_user.id) != DEVELOPER_ID:
        bot.reply_to(message, "عذرًا، هذا الأمر مخصص للمطور فقط!")
        return
    try:
        product_id = int(message.text.split()[1])
        products = clean_expired_products()
        for i, product in enumerate(products):
            if product["product_id"] == product_id:
                del products[i]
                save_products(products)
                bot.reply_to(message, f"تم حذف المنتج رقم {product_id} بنجاح! ✅")
                return
        bot.reply_to(message, "لم يتم العثور على المنتج بهذا الرقم! 🔍")
    except (IndexError, ValueError):
        bot.reply_to(message, "يرجى إدخال رقم المنتج بشكل صحيح، مثال: /delete 123")

# وظيفة البحث
@bot.message_handler(commands=['search'])
def search_product(message):
    try:
        keyword = message.text.split(maxsplit=1)[1].strip().lower()
        products = clean_expired_products()
        matching_products = [p for p in products if keyword in p["name"].lower()]
        
        if not matching_products:
            bot.reply_to(message, "عذرًا، لم يتم العثور على سلع تحتوي على هذه الكلمة! 🔍")
            return
        
        show_search_results(message, matching_products, keyword, page=0)
    except IndexError:
        bot.reply_to(message, "يرجى إدخال كلمة مفتاحية بعد الأمر، مثال: /search زين")

def show_search_results(message_or_call, products, keyword, page):
    total_pages = (len(products) + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE
    start_idx = page * PRODUCTS_PER_PAGE
    end_idx = min(start_idx + PRODUCTS_PER_PAGE, len(products))
    products_to_show = products[start_idx:end_idx]
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for idx, product in enumerate(products_to_show):
        btn = types.InlineKeyboardButton(f"{product['name']}", callback_data=f"view_{product['product_id']}")
        markup.add(btn)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton("⬅️ السابق", callback_data=f"search_page_{keyword}_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(types.InlineKeyboardButton("التالي ➡️", callback_data=f"search_page_{keyword}_{page+1}"))
    nav_buttons.append(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main"))
    markup.add(*nav_buttons)
    
    text = f"📋 نتائج البحث عن '{keyword}' (صفحة {page + 1} من {total_pages}):"
    if isinstance(message_or_call, types.Message):
        bot.reply_to(message_or_call, text, reply_markup=markup)
    else:
        bot.edit_message_text(chat_id=message_or_call.message.chat.id, message_id=message_or_call.message.message_id,
                              text=text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("search_page_"))
def handle_search_page(call):
    parts = call.data.split("_")
    keyword = parts[2]
    page = int(parts[3])
    products = clean_expired_products()
    matching_products = [p for p in products if keyword in p["name"].lower()]
    show_search_results(call, matching_products, keyword, page)
    bot.answer_callback_query(call.id)

# عرض منتج للبيع
@bot.callback_query_handler(func=lambda call: call.data == "sell")
def handle_sell(call):
    user_id = call.from_user.id
    user_data[user_id] = {"step": "product_name"}
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="حسنًا! الآن أرسل اسم المنتج الذي تود بيعه 📦")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.from_user.id in user_data and user_data[message.from_user.id]["step"] == "product_name")
def get_product_name(message):
    user_id = message.from_user.id
    user_data[user_id]["product_name"] = message.text.strip()[:50]  # تقييد الطول لتجنب مشاكل
    user_data[user_id]["step"] = "price"
    bot.reply_to(message, "رائع! الآن أرسل السعر (أرقام فقط) 💰")

@bot.message_handler(func=lambda message: message.from_user.id in user_data and user_data[message.from_user.id]["step"] == "price")
def get_price(message):
    user_id = message.from_user.id
    if message.text.isdigit():
        user_data[user_id]["price"] = message.text
        user_data[user_id]["step"] = "currency"
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_crypto = types.InlineKeyboardButton("عملة مشفرة", callback_data="crypto")
        btn_dollar = types.InlineKeyboardButton("دولار", callback_data="dollar")
        btn_stars = types.InlineKeyboardButton("نجوم تلغرام", callback_data="stars")
        btn_transfer = types.InlineKeyboardButton("تحويل دولي", callback_data="transfer")
        btn_bot_points = types.InlineKeyboardButton("نقاط بوتات", callback_data="bot_points")
        btn_all = types.InlineKeyboardButton("جميع وسائل الدفع", callback_data="all")
        markup.add(btn_crypto, btn_dollar)
        markup.add(btn_stars, btn_transfer)
        markup.add(btn_bot_points, btn_all)
        
        bot.reply_to(message, "حسنًا! الآن اختر نوع العملة التي تريدها 💸", reply_markup=markup)
    else:
        bot.reply_to(message, "عذرًا، أرسل السعر أرقام فقط! 🔢")

@bot.callback_query_handler(func=lambda call: call.data in ["crypto", "dollar", "stars", "transfer", "bot_points", "all"])
def handle_currency(call):
    user_id = call.from_user.id
    user_data[user_id]["currency"] = call.data
    user_data[user_id]["step"] = "extra_info"
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="حسنًا! الآن أرسل لي معلومات إضافية (رابط، نوع محدد من العملة، أو أي شيء ترغب بذكره مع منتجك). إذا ما بدك تضيف شي، اكتب 'لا شيء'.")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.from_user.id in user_data and user_data[message.from_user.id]["step"] == "extra_info")
def get_extra_info(message):
    user_id = message.from_user.id
    extra_info = message.text.strip()[:200] if message.text.lower() != "لا شيء" else "لا توجد معلومات إضافية"  # تقييد الطول
    user_data[user_id]["extra_info"] = extra_info
    
    product_name = user_data[user_id]["product_name"]
    price = user_data[user_id]["price"]
    currency = user_data[user_id]["currency"]
    
    products = load_products()
    product_id = max([p["product_id"] for p in products], default=0) + 1
    
    # حفظ المنتج مؤقتًا مع حالة "pending"
    product = {
        "seller_id": user_id,
        "product_id": product_id,
        "name": product_name,
        "price": price,
        "currency": currency,
        "extra_info": extra_info,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending"  # حالة انتظار الموافقة
    }
    products.append(product)
    save_products(products)
    
    markup = types.InlineKeyboardMarkup()
    btn_approve = types.InlineKeyboardButton("موافقة ✅", callback_data=f"approve_{product_id}")
    btn_reject = types.InlineKeyboardButton("رفض ❌", callback_data=f"reject_{product_id}")
    markup.add(btn_approve, btn_reject)
    
    currency_display = {"crypto": "عملة مشفرة", "dollar": "دولار", "stars": "نجوم تلغرام", "transfer": "تحويل دولي", "bot_points": "نقاط بوتات", "all": "جميع وسائل الدفع"}[currency]
    bot.send_message(ADMIN_GROUP_CHAT_ID,
                     f"مرحبًا أعزائي المشرفين! هناك طلب جديد للبيع:\n"
                     f"📦 اسم السلعة: {product_name}\n"
                     f"💵 السعر: {price}\n"
                     f"💸 نوع العملة: {currency_display}\n"
                     f"ℹ️ معلومات إضافية: {extra_info}\n"
                     f"🆔 رقم الطلب: {product_id}",
                     reply_markup=markup)
    
    bot.reply_to(message, "تم إرسال طلبك للمشرفين! سيتم إعلامك عند الموافقة ⏳")
    del user_data[user_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def handle_approve(call):
    try:
        product_id = int(call.data.split("_")[1])
        products = load_products()
        for product in products:
            if product["product_id"] == product_id and product["status"] == "pending":
                product["status"] = "approved"  # تغيير الحالة إلى موافق عليه
                save_products(products)
                user_id = product["seller_id"]
                product_name = product["name"]
                if not check_blocked_and_clean(user_id):
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text=f"تمت الموافقة على المنتج: {product_name} ✅")
                    bot.send_message(user_id,
                                     f"تمت الموافقة على منتجك '{product_name}'! 🎉\n"
                                     f"🆔 رقم المنتج: {product_id}\n"
                                     "احفظ هذا الرقم، فهو لتتبع سلعتك. استعلم عنه بـ /info {product_id}")
                bot.answer_callback_query(call.id)
                return
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="عذرًا، هذا الطلب لم يعد موجودًا أو تمت معالجته!")
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"خطأ في الموافقة: {e}")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="حدث خطأ أثناء الموافقة، حاول مرة أخرى لاحقًا!")
        bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def handle_reject(call):
    try:
        product_id = int(call.data.split("_")[1])
        products = load_products()
        for i, product in enumerate(products):
            if product["product_id"] == product_id and product["status"] == "pending":
                user_id = product["seller_id"]
                del products[i]
                save_products(products)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="تم رفض المنتج ❌")
                if not check_blocked_and_clean(user_id):
                    bot.send_message(user_id, "عذرًا، تم رفض منتجك من قبل المشرفين. حاول مرة أخرى!")
                bot.answer_callback_query(call.id)
                return
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="عذرًا، هذا الطلب لم يعد موجودًا أو تمت معالجته!")
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"خطأ في الرفض: {e}")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="حدث خطأ أثناء الرفض، حاول مرة أخرى لاحقًا!")
        bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "stats")
def show_stats(call):
    products = clean_expired_products()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"📊 *إحصائيات بوت متجرك*\n\n"
                               f"عدد السلع المعروضة: {len([p for p in products if p['status'] == 'approved'])}\n"
                               f"عدد المستخدمين: {len(user_ids)}",
                          parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "buy")
def handle_buy(call):
    approved_products = [p for p in clean_expired_products() if p["status"] == "approved"]
    if not approved_products:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="لا توجد منتجات متاحة للبيع حاليًا! عُد لاحقًا ⏳")
    else:
        show_products(call, page=0)
    bot.answer_callback_query(call.id)

def show_products(call, page):
    approved_products = [p for p in clean_expired_products() if p["status"] == "approved"]
    total_pages = (len(approved_products) + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE
    
    start_idx = page * PRODUCTS_PER_PAGE
    end_idx = min(start_idx + PRODUCTS_PER_PAGE, len(approved_products))
    products_to_show = approved_products[start_idx:end_idx]
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for product in products_to_show:
        btn = types.InlineKeyboardButton(f"{product['name']}", callback_data=f"view_{product['product_id']}")
        markup.add(btn)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(types.InlineKeyboardButton("التالي ➡️", callback_data=f"page_{page+1}"))
    nav_buttons.append(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main"))
    markup.add(*nav_buttons)
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"📋 المنتجات المتوفرة (صفحة {page + 1} من {total_pages}):",
                          reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
def handle_page(call):
    page = int(call.data.split("_")[1])
    show_products(call, page)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_sell = types.InlineKeyboardButton("اعرض منتجك للبيع", callback_data="sell")
    btn_buy = types.InlineKeyboardButton("شراء منتج متوافر", callback_data="buy")
    btn_stats = types.InlineKeyboardButton("الإحصائيات 📊", callback_data="stats")
    btn_channel = types.InlineKeyboardButton("قناة الإعلانات 📢", url="https://t.me/QUEEN_SH963")
    btn_dev = types.InlineKeyboardButton("المطور", url="https://t.me/SB_SAHAR")
    markup.add(btn_sell, btn_buy)
    markup.add(btn_stats, btn_channel)
    markup.add(btn_dev)
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="أهلاً بك في بوت *متجرك*! 👋\nاختر من الأزرار أدناه ⬇️\n\n"
                               "ابدأ بـ /start | ابحث بـ /search | استعلم بـ /info",
                          parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("view_"))
def view_product(call):
    product_id = int(call.data.split("_")[1])
    approved_products = [p for p in clean_expired_products() if p["status"] == "approved"]
    for product in approved_products:
        if product["product_id"] == product_id:
            currency = {"crypto": "عملة مشفرة", "dollar": "دولار", "stars": "نجوم تلغرام", "transfer": "تحويل دولي", "bot_points": "نقاط بوتات", "all": "جميع وسائل الدفع"}[product['currency']]
            extra_info = product.get("extra_info", "لا توجد معلومات إضافية")
            
            markup = types.InlineKeyboardMarkup()
            btn_buy = types.InlineKeyboardButton("شراء 🛒", callback_data=f"buy_{product_id}")
            btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="buy")
            markup.add(btn_buy)
            markup.add(btn_back)
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f"📦 المنتج: {product['name']}\n"
                                       f"💵 السعر: {product['price']}\n"
                                       f"💸 العملة: {currency}\n"
                                       f"ℹ️ معلومات إضافية: {extra_info}\n"
                                       f"🆔 رقم الطلب: {product['product_id']}",
                                  reply_markup=markup)
            bot.answer_callback_query(call.id)
            return
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="عذرًا، هذا المنتج لم يعد متاحًا!")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_purchase(call):
    product_id = int(call.data.split("_")[1])
    approved_products = [p for p in clean_expired_products() if p["status"] == "approved"]
    for product in approved_products:
        if product["product_id"] == product_id:
            seller_id = product["seller_id"]
            if check_blocked_and_clean(seller_id):
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="عذرًا، البائع غير متاح حاليًا والمنتج تم حذفه!")
                bot.answer_callback_query(call.id)
                return
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="تم اختيار المنتج! انضم إلى مجموعة المشرفين لإتمام عملية الشراء:\n"
                                       f"[رابط المجموعة](https://t.me/+RNl335NGakk2ODk0)",
                                  parse_mode="Markdown")
            
            bot.send_message(seller_id,
                             f"عزيزي المستخدم، هناك شخص طلب سلعتك '{product['name']}' ويريد شراءها!\n"
                             f"ارجو منك الانضمام إلى مجموعة المشرفين لإتمام العملية:\n"
                             f"[رابط المجموعة](https://t.me/+RNl335NGakk2ODk0)",
                             parse_mode="Markdown")
            bot.answer_callback_query(call.id)
            return
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="عذرًا، هذا المنتج لم يعد متاحًا!")
    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    print("البوت يعمل الآن...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"حدث خطأ: {e}")
            time.sleep(5)