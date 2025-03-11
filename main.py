import telebot
import time
from handlers import *  # استيراد جميع المعالجات من handlers.py

# إعداد البوت
bot = telebot.TeleBot("7383597510:AAHsQBH05yVEN96rL783BDkRD1YO1yXY1R4")
ADMIN_GROUP_CHAT_ID = "-1002482962804"
PRODUCTS_FILE = "products.json"
PRODUCTS_PER_PAGE = 5
DEVELOPER_ID = "6789179634"

user_data = {}
user_ids = set()

print("جاري تسجيل المعالجات...")  # للتأكد من أن الكود يصل إلى هنا

if __name__ == "__main__":
    print("البوت يعمل الآن...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"حدث خطأ: {e}")
            time.sleep(5)
