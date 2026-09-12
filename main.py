import os
import qrcode
from io import BytesIO
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Render Environment Variables se keys read karna
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
UPI_ID = os.getenv("UPI_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Plan Selection Menu (/start)
@dp.message_handler(commands=['start', 'upgrade', 'plans'])
async def show_plans(message: types.Message):
    text = (
        "🌸 **Premium Plans And Pricing** 🌸\n\n"
        "📍 Plan 1: 50₹ - 1 Month\n"
        "📍 Plan 2: 90₹ - 2 Month\n"
        "📍 Plan 3: 140₹ - 3 Month\n"
        "📍 Plan 4: 190₹ - 4 Month\n\n"
        "📌 Click button to select plan:"
    )
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("1 Month", callback_data="pay_50_1 Month"),
        InlineKeyboardButton("2 Month", callback_data="pay_90_2 Month"),
        InlineKeyboardButton("3 Month", callback_data="pay_140_3 Month"),
        InlineKeyboardButton("4 Month", callback_data="pay_190_4 Month")
    )
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

# Payment QR Generator Callback
@dp.callback_query_handler(lambda c: c.data.startswith('pay_'))
async def process_payment(callback_query: types.CallbackQuery):
    _, amount, plan_name = callback_query.data.split('_')
    
    # UPI URL String
    upi_url = f"upi://pay?pa={UPI_ID}&pn=PremiumSub&am={amount}&cu=INR"
    
    # QR Code generate in memory
    qr_img = qrcode.make(upi_url)
    bio = BytesIO()
    qr_img.save(bio, 'PNG')
    bio.seek(0)
    
    caption_text = (
        f"💳 **{plan_name} premium plan amount is {amount} ₹**\n\n"
        "1️⃣ **Scan it and pay**\n"
        "2️⃣ After payment **Upload screenshot**"
    )
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📤 UPLOAD SCREENSHOT", callback_data=f"upload_{amount}"),
        InlineKeyboardButton("❌ CANCEL PAYMENT", callback_data="cancel_pay")
    )
    
    await bot.send_photo(
        chat_id=callback_query.message.chat.id,
        photo=bio,
        caption=caption_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# Cancel Button Handler
@dp.callback_query_handler(lambda c: c.data == 'cancel_pay')
async def cancel_payment(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await bot.send_message(callback_query.message.chat.id, "❌ Payment Cancelled.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
  
