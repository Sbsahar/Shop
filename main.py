import telebot
import time
from handlers import *  # استيراد جميع المعالجات

# إعداد البوت
bot = telebot.TeleBot("7383597510:AAHsQBH05yVEN96rL783BDkRD1YO1yXY1R4")
ADMIN_GROUP_CHAT_ID = "-1002482962804"
PRODUCTS_FILE = "products.json"
PRODUCTS_PER_PAGE = 5
DEVELOPER_ID = "6789179634"

user_data = {}
user_ids = set()

if __name__ == "__main__":
    print("البوت يعمل الآن...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"حدث خطأ: {e}")
            time.sleep(5)
