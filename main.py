# bot.py
import logging
import os
import requests
from datetime import datetime
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === CẤU HÌNH ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # API thời tiết từ OpenWeatherMap
EXCHANGE_API_URL = "https://api.exchangerate.host/latest?base=THB&symbols=VND"  # API tỷ giá THB-VND

# === GHI LOG ===
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# === CÁC LỆNH ===
async def bat_dau(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thong_diep = (
        "🤖 Xin chào! Tôi là trợ lý Telegram hỗ trợ cuộc sống tại Bangkok 🇹🇭\n\n"
        "Các lệnh bạn có thể dùng:\n"
        "/weather - Xem thời tiết hôm nay\n"
        "/exchange - Tỷ giá THB → VND\n"
        "/quote - Câu nói truyền động lực\n"
        "/food - Gợi ý món ăn sáng\n"
        "/translate <nội dung> - Dịch TH-VI-EN\n"
        "/remind <nội dung> - Nhắc việc (giả lập)\n"
        "/note <ghi chú> - Ghi chú nhanh"
    )
    await update.message.reply_text(thong_diep)

async def thoi_tiet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Bangkok&appid={WEATHER_API_KEY}&units=metric"
    res = requests.get(url).json()
    mo_ta = res['weather'][0]['description'].capitalize()
    nhiet_do = res['main']['temp']
    ket_qua = f"🌤️ Thời tiết Bangkok: {mo_ta}, {nhiet_do}°C"
    await update.message.reply_text(ket_qua)

async def ty_gia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = requests.get(EXCHANGE_API_URL).json()
    gia = res['rates']['VND']
    ket_qua = f"💱 100 THB ≈ {int(gia*100):,} VND"
    await update.message.reply_text(ket_qua)

async def cau_noi_truyen_dong_luc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    noi_dung = {"contents": [{"parts": [{"text": "Give me one short motivational quote in English."}]}]}
    res = requests.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent", json=noi_dung, headers=headers)
    trich_dan = res.json()["candidates"][0]["content"]["parts"][0]["text"]
    await update.message.reply_text(f"✨ {trich_dan}")

async def goi_y_mon_an(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    noi_dung = {"contents": [{"parts": [{"text": "Suggest one Thai breakfast dish with short description."}]}]}
    res = requests.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent", json=noi_dung, headers=headers)
    mon_an = res.json()["candidates"][0]["content"]["parts"][0]["text"]
    await update.message.reply_text(f"🍜 {mon_an}")

async def dich_ngon_ngu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Vui lòng nhập nội dung để dịch. Ví dụ: /translate Xin chào")
    van_ban = ' '.join(context.args)
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    prompt = f"Translate this between Thai, Vietnamese, and English automatically: {van_ban}"
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    res = requests.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent", json=body, headers=headers)
    ket_qua = res.json()["candidates"][0]["content"]["parts"][0]["text"]
    await update.message.reply_text(ket_qua)

async def nhac_viec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cong_viec = ' '.join(context.args)
    if not cong_viec:
        return await update.message.reply_text("Vui lòng nhập nội dung cần nhắc. Ví dụ: /remind họp lúc 2 giờ chiều")
    await update.message.reply_text(f"⏰ Đã lưu lời nhắc: {cong_viec} (demo, chưa lưu thật)")

async def ghi_chu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    noi_dung = ' '.join(context.args)
    if not noi_dung:
        return await update.message.reply_text("Vui lòng nhập ghi chú. Ví dụ: /note Gọi mẹ")
    await update.message.reply_text(f"📝 Đã lưu ghi chú: {noi_dung} (demo, chưa lưu thật)")

# === KHỞI ĐỘNG BOT ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", bat_dau))
    app.add_handler(CommandHandler("weather", thoi_tiet))
    app.add_handler(CommandHandler("exchange", ty_gia))
    app.add_handler(CommandHandler("quote", cau_noi_truyen_dong_luc))
    app.add_handler(CommandHandler("food", goi_y_mon_an))
    app.add_handler(CommandHandler("translate", dich_ngon_ngu))
    app.add_handler(CommandHandler("remind", nhac_viec))
    app.add_handler(CommandHandler("note", ghi_chu))

    app.bot.set_my_commands([
        BotCommand("start", "Khởi động bot"),
        BotCommand("weather", "Thời tiết Bangkok"),
        BotCommand("exchange", "Tỷ giá THB-VND"),
        BotCommand("quote", "Câu nói truyền động lực"),
        BotCommand("food", "Gợi ý món ăn sáng"),
        BotCommand("translate", "Dịch ngôn ngữ"),
        BotCommand("remind", "Nhắc việc"),
        BotCommand("note", "Ghi chú")
    ])

    print("Bot đang chạy...")
    app.run_polling()
