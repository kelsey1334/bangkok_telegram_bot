import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

# Bật log để dễ debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hàm lấy dữ liệu thời tiết Bangkok từ OpenWeatherMap
def lay_thoi_tiet():
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Bangkok,TH&appid={api_key}&units=metric&lang=vi"
    try:
        response = requests.get(url)
        data = response.json()
        mo_ta = data['weather'][0]['description'].capitalize()
        nhiet_do = data['main']['temp']
        do_am = data['main']['humidity']
        gio = data['wind']['speed']
        return f"🌤 Thời tiết Bangkok hôm nay:\n{mo_ta}\n🌡 Nhiệt độ: {nhiet_do}°C\n💧 Độ ẩm: {do_am}%\n💨 Gió: {gio} m/s"
    except:
        return "Không thể lấy dữ liệu thời tiết."

# Hàm gọi Gemini để lấy gợi ý món ăn sáng
def goi_y_bua_sang():
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    prompt = "Hãy gợi ý một món ăn sáng ngon miệng phù hợp với người Việt sống ở Bangkok."
    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"})
    try:
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Không thể lấy gợi ý món ăn."

# Hàm gọi Gemini để lấy câu nói truyền động lực
def trich_dan_truyen_dong_luc():
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    prompt = "Hãy tạo một câu nói truyền động lực ngắn gọn bằng tiếng Việt."
    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"})
    try:
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Không thể lấy câu truyền động lực."

# Hàm lấy tỷ giá 100 Baht sang VND từ exchangerate.host
def ty_gia_baht():
    try:
        res = requests.get("https://api.exchangerate.host/convert?from=THB&to=VND&amount=100")
        data = res.json()
        gia = round(data['result'])
        return f"💱 100 Baht = {gia} VND"
    except:
        return "Không thể lấy tỷ giá."

# Lệnh /start
async def bat_dau(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chao = "🤖 Xin chào! Đây là trợ lý của bạn tại Bangkok 🇹🇭.\n\nCác lệnh bạn có thể sử dụng:\n" \
           "+ /weather – Xem thời tiết hôm nay\n" \
           "+ /breakfast – Gợi ý món ăn sáng\n" \
           "+ /quote – Câu nói truyền động lực\n" \
           "+ /exchange – Tỷ giá Baht-VND"
    await update.message.reply_text(chao)

# Lệnh /weather
async def thoi_tiet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ket_qua = lay_thoi_tiet()
    await update.message.reply_text(ket_qua)

# Lệnh /breakfast
async def bua_sang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mon = goi_y_bua_sang()
    await update.message.reply_text(f"🍽 Gợi ý món ăn sáng:\n{mon}")

# Lệnh /quote
async def cau_noi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trich_dan = trich_dan_truyen_dong_luc()
    await update.message.reply_text(f"💬 {trich_dan}")

# Lệnh /exchange
async def ti_gia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gia = ty_gia_baht()
    await update.message.reply_text(gia)

# Khởi tạo bot
if __name__ == '__main__':
    token = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", bat_dau))
    app.add_handler(CommandHandler("weather", thoi_tiet))
    app.add_handler(CommandHandler("breakfast", bua_sang))
    app.add_handler(CommandHandler("quote", cau_noi))
    app.add_handler(CommandHandler("exchange", ti_gia))

    print("🤖 Bot đang chạy...")
    app.run_polling()
