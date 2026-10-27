import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ⬇️⬇️ توکن خودت رو اینجا بذار ⬇️⬇️
TOKEN = "8835382268:AAGkKdZYq08Al-fbfTRmxsM05xR8v86Aieg"
# ⬇️⬇️ آدرس صفحه ثبت‌نام سایتت رو اینجا بذار ⬇️⬇️
REGISTER_URL = "https://apvira.co.ir/register"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class LeadForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="کارت ویزیت دیجیتال (درگاه اصلی)", callback_data="product_card")],
        [InlineKeyboardButton(text="سیستم نوبت‌دهی (سالن‌ها)", callback_data="product_booking")],
        [InlineKeyboardButton(text="منوی دیجیتال (رستوران‌ها)", callback_data="product_menu")]
    ])
    await message.answer(
        "سلام! به دموی محصولات آپ‌ویرا خوش آمدید.\n"
        "کارت ویزیت دیجیتال ما، درگاه ورود به تمام محصولات است.\n"
        "کدام محصول را می‌خواهید از نزدیک تجربه کنید؟", 
        reply_markup=keyboard
    )

@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    
    # ۱. کارت ویزیت (درگاه اصلی)
    if callback_query.data == "product_card":
        web_app = WebAppInfo(url="https://apvira.co.ir/c/1X16W")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 مشاهده دموی کارت ویزیت", web_app=web_app)],
            [InlineKeyboardButton(text="می‌خواهم کارت ویزیت خودم را بسازم", callback_data="lead_card")]
        ])
        await callback_query.message.answer(
            "این یک کارت ویزیت دیجیتال زنده است. توجه کن که چطور گزینه‌های منو و نوبت‌دهی داخل خود کارت قرار گرفته‌اند.\n"
            "هر کسب‌وکاری با هر شغلی می‌تواند این کارت را داشته باشد.", 
            reply_markup=keyboard
        )
        
    # ۲. سیستم نوبت‌دهی
    elif callback_query.data == "product_booking":
        web_app = WebAppInfo(url="https://apvira.co.ir/book/1X16W")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 تجربه رزرو نوبت (مثل مشتری)", web_app=web_app)],
            [InlineKeyboardButton(text="✨ شروع ۷ روز تست رایگان پنل", url=REGISTER_URL)],
            [InlineKeyboardButton(text="درخواست مشاوره تلفنی", callback_data="lead_booking")]
        ])
        await callback_query.message.answer(
            "این دقیقاً همان صفحه‌ای است که مشتریان شما می‌بینند.\n\n"
            "👉 **پیشنهاد می‌کنم همین الان یک نوبت تستی رزرو کنی** تا ببینی سیستم چطور کار می‌کند و پیامک تایید برایت ارسال می‌شود.", 
            reply_markup=keyboard
        )
        
    # ۳. منوی دیجیتال
    elif callback_query.data == "product_menu":
        web_app = WebAppInfo(url="https://apvira.co.ir/menu/cafe-ayhan")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 مشاهده دموی منوی دیجیتال", web_app=web_app)],
            [InlineKeyboardButton(text="✨ شروع ۷ روز تست رایگان", url=REGISTER_URL)],
            [InlineKeyboardButton(text="درخواست مشاوره برای رستوران", callback_data="lead_menu")]
        ])
        await callback_query.message.answer("این منوی دیجیتال است. مشتریان شما با اسکن QR کد می‌توانند منو را ببینند:", reply_markup=keyboard)
        
    # شروع فرم جذب لید
    elif callback_query.data.startswith("lead_"):
        product_type = callback_query.data.split("_")[1]
        await state.update_data(interest=product_type)
        
        await callback_query.message.answer("عالیه! لطفاً اسم سالن، رستوران یا کسب‌وکارت رو بنویس:")
        await state.set_state(LeadForm.waiting_for_name)

@dp.message(LeadForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="ارسال شماره موبایل من 📱", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("ثبت شد. حالا با کلیک روی دکمه زیر، شماره موبایلت رو برام بفرست تا تیم ما باهات تماس بگیره:", reply_markup=keyboard)
    await state.set_state(LeadForm.waiting_for_phone)

@dp.message(LeadForm.waiting_for_phone, lambda message: message.contact is not None or message.text)
async def process_phone(message: types.Message, state: FSMContext):
    raw_phone = message.contact.phone_number if message.contact else message.text
    
    # --- تمیز کردن شماره موبایل ---
    # حذف هر کاراکتری غیر از عدد
    clean_phone = "".join(filter(str.isdigit, raw_phone))
    
    # اگر با 98 شروع شده بود (مثلا 98919...) تبدیلش کن به 09...
    if clean_phone.startswith("98") and len(clean_phone) == 12:
        clean_phone = "0" + clean_phone[2:]
    # اگر با 0 شروع نشده بود و 10 رقم بود، 0 به اولش اضافه کن
    elif not clean_phone.startswith("0") and len(clean_phone) == 10:
        clean_phone = "0" + clean_phone
    # -----------------------------

    user_data = await state.get_data()
    name = user_data.get('name')
    interest = user_data.get('interest')
    telegram_username = message.from_user.username or "ندارد"

    api_url = "https://apvira.co.ir/api/leads" 
    
    payload = {
        "name": name,
        "phone": clean_phone, # <--- اینجا از شماره تمیز شده استفاده میکنیم
        "source": "Telegram Bot",
        "note": f"محصول: {interest} | Username: @{telegram_username}"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload) as response:
                print(f"STATUS: {response.status}")
                print(f"RESPONSE: {await response.text()}")
                
                if response.status in [200, 201]:
                    await message.answer("✅ عالی! درخواستت با موفقیت ثبت شد. همکاران ما به زودی باهات تماس می‌گیرن.", reply_markup=ReplyKeyboardRemove())
                else:
                    await message.answer("شماره دریافت شد، اما در ثبت خطایی رخ داد. به زودی دستی پیگیری می‌کنیم.", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        print(f"EXCEPTION: {e}")
        await message.answer("شماره دریافت شد، اما مشکل ارتباط با سرور داشتیم. دستی پیگیری می‌کنیم.", reply_markup=ReplyKeyboardRemove())

    await state.clear()

async def main():
     keep_alive()
    logging.basicConfig(level=logging.INFO)
    print("ربات با قیف فروش جدید روشن شد...")
    await dp.start_polling(bot)
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
if __name__ == "__main__":
    asyncio.run(main())