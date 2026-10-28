import asyncio
import logging
import aiohttp
import os
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, LinkPreviewOptions
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode

# ==========================================
# بخش وب‌سرور برای زنده نگه داشتن ربات در Render
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()
# ==========================================

# توکن از متغیرهای محیطی خوانده می‌شود
TOKEN ="8835382268:AAGkKdZYq08Al-fbfTRmxsM05xR8v86Aieg"
BANNER_URL = "https://apvira.co.ir/og-image.png" # لینک بنر

bot = Bot(token=TOKEN)
dp = Dispatcher()

class LeadForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()

# --- منوی ثابت پایین صفحه (Reply Keyboard) ---
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍️ محصولات ما"), KeyboardButton(text="📞 درخواست مشاوره")],
        [KeyboardButton(text="🌐 وب‌سایت APVIRA"), KeyboardButton(text="💳 خرید اقساطی")]
    ],
    resize_keyboard=True,
    is_persistent=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    caption = (
        "<b>سلام! به اکوسیستم APVIRA خوش آمدید 👋</b>\n\n"
        "ما اینجا هستیم تا کسب‌وکار شما را دیجیتال کنیم.\n"
        "از کارت ویزیت هوشمند تا سیستم نوبت‌دهی و منوی دیجیتال.\n\n"
        "✨ <b>امکان خرید اقساطی (بدون چک و ضامن) فعال شد!</b>\n\n"
        "برای شروع، از منوی زیر یکی از گزینه‌ها را انتخاب کنید یا روی دکمه‌های شیشه‌ای زیر بزنید:"
    )
    
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎨 کارت ویزیت دیجیتال", callback_data="product_card")],
        [InlineKeyboardButton(text="📅 سیستم نوبت‌دهی", callback_data="product_booking")],
        [InlineKeyboardButton(text="🍔 منوی دیجیتال رستوران", callback_data="product_menu")]
    ])
    
    await message.answer_photo(
        photo=BANNER_URL,
        caption=caption,
        reply_markup=main_keyboard,
        parse_mode=ParseMode.HTML
    )
    await message.answer("لطفا یکی از محصولات زیر را انتخاب کنید:", reply_markup=inline_kb)

# --- پردازش دکمه‌های منوی پایین (Reply) ---
@dp.message(F.text == "🛍️ محصولات ما")
async def show_products(message: types.Message):
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎨 کارت ویزیت دیجیتال", callback_data="product_card")],
        [InlineKeyboardButton(text="📅 سیستم نوبت‌دهی", callback_data="product_booking")],
        [InlineKeyboardButton(text="🍔 منوی دیجیتال رستوران", callback_data="product_menu")]
    ])
    await message.answer("لطفا یکی از محصولات زیر را انتخاب کنید:", reply_markup=inline_kb)

@dp.message(F.text == "📞 درخواست مشاوره")
async def request_consult(message: types.Message, state: FSMContext):
    await message.answer("عالیه! لطفاً اسم سالن یا رستورانت رو بنویس:")
    await state.set_state(LeadForm.waiting_for_name)

@dp.message(F.text == "🌐 وب‌سایت APVIRA")
async def website(message: types.Message):
    await message.answer("🌐 <b>وب‌سایت رسمی ما:</b>\nhttps://apvira.co.ir", parse_mode=ParseMode.HTML)

@dp.message(F.text == "💳 خرید اقساطی")
async def installment_info(message: types.Message):
    text = (
        "<b>💳 شرایط خرید اقساطی</b>\n\n"
        "شما می‌توانید محصولات ما را با شرایط زیر خریداری کنید:\n"
        "🔹 <b>پیش‌پرداخت:</b> ۴۰ درصد مبلغ کل\n"
        "🔹 <b>تعداد اقساط:</b> ۳ قسط ماهانه\n"
        "🔹 <b>بدون نیاز به چک، سفته یا ضامن!</b>\n\n"
        "برای ثبت درخواست، دکمه «درخواست مشاوره» را بزنید."
    )
    await message.answer(text, parse_mode=ParseMode.HTML)


# --- پردازش دکمه‌های شیشه‌ای (Inline) ---
@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    
    if callback_query.data == "product_card":
        web_app = WebAppInfo(url="https://apvira.co.ir/c/1X16W")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 مشاهده دموی زنده", web_app=web_app)],
            [InlineKeyboardButton(text="💳 درخواست مشاوره و خرید", callback_data="lead_card")]
        ])
        await callback_query.message.answer(
            "<b>کارت ویزیت دیجیتال (درگاه اصلی)</b>\n\n"
            "این یک کارت ویزیت زنده است. تمام اطلاعات تماس، شبکه‌های اجتماعی و خدمات شما در یک لینک.\n"
            "منو و نوبت‌دهی هم داخل همین کارت قرار می‌گیرند.",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
    elif callback_query.data == "product_booking":
        web_app = WebAppInfo(url="https://apvira.co.ir/book/1X16W")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 تجربه رزرو نوبت", web_app=web_app)],
            [InlineKeyboardButton(text="✨ شروع ۷ روز تست رایگان", url="https://apvira.co.ir/register")],
            [InlineKeyboardButton(text="💳 خرید اقساطی (۴۰٪ پیش‌پرداخت)", callback_data="lead_booking")]
        ])
        await callback_query.message.answer(
            "<b>سیستم نوبت‌دهی آنلاین</b>\n\n"
            "مشتریان شما بدون تماس تلفنی، در هر ساعت از شبانه‌روز نوبت می‌گیرند.\n\n"
            "💳 <b>این محصول را می‌توانید با ۴۰٪ پیش‌پرداخت و ۳ قسط ماهانه خریداری کنید.</b>",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
    elif callback_query.data == "product_menu":
        web_app = WebAppInfo(url="https://apvira.co.ir/menu/cafe-ayhan")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 مشاهده دموی منو", web_app=web_app)],
            [InlineKeyboardButton(text="✨ شروع ۷ روز تست رایگان", url="https://apvira.co.ir/register")],
            [InlineKeyboardButton(text="💳 خرید اقساطی", callback_data="lead_menu")]
        ])
        await callback_query.message.answer(
            "<b>منوی دیجیتال رستوران</b>\n\n"
            "با اسکن QR کد، مشتریان منوی شما را می‌بینند و سفارش می‌دهند. بدون هزینه چاپ!\n\n"
            "💳 <b>خرید اقساطی این محصول هم فعال است!</b>",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
    elif callback_query.data.startswith("lead_"):
        product_type = callback_query.data.split("_")[1]
        await state.update_data(interest=product_type)
        await callback_query.message.answer("<b>عالیه! لطفاً اسم سالن یا رستورانت رو بنویس:</b>", parse_mode=ParseMode.HTML)
        await state.set_state(LeadForm.waiting_for_name)

@dp.message(LeadForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="ارسال شماره موبایل من 📱", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("<b>ثبت شد.</b> حالا با کلیک روی دکمه زیر، شماره موبایلت رو برام بفرست:", reply_markup=keyboard, parse_mode=ParseMode.HTML)
    await state.set_state(LeadForm.waiting_for_phone)

@dp.message(LeadForm.waiting_for_phone, lambda message: message.contact is not None or message.text)
async def process_phone(message: types.Message, state: FSMContext):
    raw_phone = message.contact.phone_number if message.contact else message.text
    clean_phone = "".join(filter(str.isdigit, raw_phone))
    if clean_phone.startswith("98") and len(clean_phone) == 12: clean_phone = "0" + clean_phone[2:]
    elif not clean_phone.startswith("0") and len(clean_phone) == 10: clean_phone = "0" + clean_phone

    user_data = await state.get_data()
    name = user_data.get('name')
    interest = user_data.get('interest')
    telegram_username = message.from_user.username or "ندارد"
    api_url = "https://apvira.co.ir/api/leads" 
    payload = {"name": name, "phone": clean_phone, "source": "Telegram Bot", "note": f"محصول: {interest} | Username: @{telegram_username}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload) as response:
                if response.status in [200, 201]:
                    await message.answer("<b>✅ عالی! درخواستت ثبت شد.</b>\nهمکاران ما به زودی باهات تماس می‌گیرن.", reply_markup=main_keyboard, parse_mode=ParseMode.HTML)
                else:
                    await message.answer("شماره دریافت شد، اما در ثبت خطایی رخ داد. دستی پیگیری می‌کنیم.", reply_markup=main_keyboard)
    except Exception:
        await message.answer("شماره دریافت شد، اما مشکل ارتباط با سرور داشتیم.", reply_markup=main_keyboard)
    await state.clear()

async def main():
    keep_alive()
    logging.basicConfig(level=logging.INFO)
    print("ربات با منوی جدید روشن شد...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
