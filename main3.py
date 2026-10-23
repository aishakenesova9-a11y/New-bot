import asyncio, logging, json, os
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

BOT_TOKEN = "8984060573:AAGUuxFPBUUotSqyfhTKrTtIeHnCn41hHSc"
ADMIN_ID = 8844838263 # твой ID
CARD = "4400430043429981"

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# База
DB_FILE = "users.json"
users_db = {}
orders = {}
order_counter = 500

if os.path.exists(DB_FILE):
    try:
        users_db = json.load(open(DB_FILE, 'r', encoding='utf-8'))
        # конверт ключей в int
        users_db = {int(k):v for k,v in users_db.items()}
    except: pass

def save_db():
    json.dump(users_db, open(DB_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

def get_user(uid, username, first_name):
    if uid not in users_db:
        users_db[uid] = {
            "username": username or "нет",
            "first_name": first_name,
            "kaspi_name": "не указано",
            "total_sum": 0,
            "count": 0,
            "stars": 0,
            "level": "Стартовый",
            "bonuses": "появятся после нескольких покупок",
            "reg_date": datetime.now().strftime("%Y-%m-%d"),
            "orders": []
        }
        save_db()
    return users_db[uid]

class S(StatesGroup):
    friend = State()
    check = State()
    custom_amount = State()
    kaspi_name = State()

# === ТЕКСТЫ С КРАСИВЫМ ШРИФТОМ ===
START_TEXT = """
<b><i>𝘿𝙖𝙧𝙨𝙤𝙪𝙡 𝙎𝙝𝙤𝙥</i></b>
<i>Ᏼыᴦᴏдный ɯᴏᴨ ᴦдᴇ ʙы ʍᴏжᴇᴛᴇ ᴨᴩиᴏбᴩᴇᴄᴛи ᴄᴇбᴇ чᴛᴏ - ᴛᴏ</i>
<b>ᴨᴏᴋуᴨᴀя ʙ уᴄᴧуᴦᴀх</b>

<b>𝟭) Ꮾудьᴛᴇ ʙниʍᴀᴛᴇᴧьны</b>
<b>𝟮) <i>ʙыбᴇᴩиᴛᴇ уᴄᴧуᴦу нижᴇ иɜ инᴧᴀйн ᴋнᴏᴨᴏᴋ :</i></b>
"""

KASPI_TEXT = f"""
<b>💳 <i>Реквизиты @drc1ld</i></b>

<b>𝑲𝒂𝒔𝒑𝒊 оплата :</b>
<b>Карта :</b> <code>{CARD}</code>
<b>Получатель :</b> <i>Инжу Е.</i>

<b><i>После оплаты скинтье чек с пдф файл или же фото чека</i></b>
<b>Рядом с чеком скинь свой юз @</b>
"""

# === КНОПКИ ===
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐️ 𝐊упить звёзды", callback_data="buy_stars")],
        [InlineKeyboardButton(text="👑 𝑷𝒓𝒆𝒎𝒊𝒖𝒎", callback_data="buy_premium")],
        [InlineKeyboardButton(text="💬 𝑷𝒐ддержка", callback_data="support"), InlineKeyboardButton(text="👤 𝑷𝒓𝒐𝒇𝒊𝒍𝒆", callback_data="profile")],
        [InlineKeyboardButton(text="📖 𝑰𝒏𝒔𝒕𝒓𝒖𝒄𝒕𝒊𝒐𝒏", callback_data="instruction")]
    ])

def for_whom_kb(t):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🙋‍♀️ 𝐂ебе", callback_data=f"{t}_self"), InlineKeyboardButton(text="👥 𝐃ругу", callback_data=f"{t}_friend")],
        [InlineKeyboardButton(text="↩️ 𝑵𝒂з𝒂𝒅", callback_data="main")]
    ])

def stars_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="50 - 440₸", callback_data="s_50_440"), InlineKeyboardButton(text="100 - 880₸", callback_data="s_100_880")],
        [InlineKeyboardButton(text="150 - 1320₸", callback_data="s_150_1320"), InlineKeyboardButton(text="200 - 1760₸", callback_data="s_200_1760")],
        [InlineKeyboardButton(text="250 - 2200₸", callback_data="s_250_2200"), InlineKeyboardButton(text="300 - 2640₸", callback_data="s_300_2640")],
        [InlineKeyboardButton(text="400 - 3520₸", callback_data="s_400_3520"), InlineKeyboardButton(text="500 - 4400₸", callback_data="s_500_4400")],
        [InlineKeyboardButton(text="1000 - 8800₸", callback_data="s_1000_8800"), InlineKeyboardButton(text="2000 - 17600₸", callback_data="s_2000_17600")],
        [InlineKeyboardButton(text="✨ 𝑳юбое кол-во", callback_data="s_custom")],
        [InlineKeyboardButton(text="↩️ 𝑵𝒂з𝒂𝒅", callback_data="buy_stars")]
    ])

def prem_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="3 месяца - 5500₸", callback_data="p_3_5500")],
        [InlineKeyboardButton(text="6 месяцев - 7500₸", callback_data="p_6_7500")],
        [InlineKeyboardButton(text="12 месяцев - 14000₸", callback_data="p_12_14000")],
        [InlineKeyboardButton(text="↩️ 𝑵𝒂з𝒂𝒅", callback_data="buy_premium")]
    ])

def pay_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 𝑪копировать номер", callback_data="copy")],
        [InlineKeyboardButton(text="✅ 𝒀𝒂 оплатил", callback_data="i_paid")],
        [InlineKeyboardButton(text="↩️ 𝑵𝒂з𝒂𝒅", callback_data="main")]
    ])

# === ЛОГИКА ===
@dp.message(CommandStart())
async def start(m: Message, state: FSMContext):
    await state.clear()
    get_user(m.from_user.id, m.from_user.username, m.from_user.first_name)
    try:
        await m.answer_photo(FSInputFile("main.jpg"), caption=START_TEXT, reply_markup=main_kb())
    except:
        await m.answer(START_TEXT, reply_markup=main_kb())

@dp.callback_query(F.data=="main")
async def main_c(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.answer(START_TEXT, reply_markup=main_kb())
    await c.answer()

@dp.callback_query(F.data=="buy_stars")
async def bs(c: CallbackQuery):
    await c.message.answer("<b>Кому хотите приобрести ?</b>\n\n<i><b>Курс : 1 ⭐️ - 8.8₸</b></i>", reply_markup=for_whom_kb("stars"))
    await c.answer()

@dp.callback_query(F.data=="buy_premium")
async def bp(c: CallbackQuery):
    await c.message.answer("<b>Кому хотите приобрести ? 👑</b>", reply_markup=for_whom_kb("prem"))
    await c.answer()

@dp.callback_query(F.data.endswith("_self") | F.data.endswith("_friend"))
async def whom(c: CallbackQuery, state: FSMContext):
    t = "stars" if c.data.startswith("stars") else "premium"
    target = "self" if "self" in c.data else "friend"
    await state.update_data(type=t, target=target)
    if target=="friend":
        await state.set_state(S.friend)
        await c.message.answer("<b><i>Скиньте нынешний юзернейм друга !</i></b>\n<code>@username</code>")
    else:
        await state.update_data(friend="себе")
        if t=="stars":
            await c.message.answer("<b><i>Курс : 1 звезда - 8.8₸\nВыберите нужное кол-во:</i></b>", reply_markup=stars_kb())
        else:
            await c.message.answer("<b><i>Выберите нужный пакет премиум от 3 месяцев до 12 месяцев:</i></b>", reply_markup=prem_kb())
    await c.answer()

@dp.message(S.friend)
async def get_f(m: Message, state: FSMContext):
    await state.update_data(friend=m.text)
    d = await state.get_data()
    if d['type']=="stars":
        await m.answer("<b><i>Курс : 1 звезда - 8.8₸\nВыберите нужное кол-во:</i></b>", reply_markup=stars_kb())
    else:
        await m.answer("<b><i>Выберите нужный пакет:</i></b>", reply_markup=prem_kb())
    await state.set_state(None)

@dp.callback_query(F.data.startswith("s_"))
async def s_sel(c: CallbackQuery, state: FSMContext):
    if c.data=="s_custom":
        await state.set_state(S.custom_amount)
        await c.message.answer("<b><i>Напишите любое количество звезд :\nНапример 75</i></b>")
        await c.answer()
        return
    parts = c.data.split("_")
    await state.update_data(amount=f"{parts[1]} ⭐️", sum=int(parts[2]))
    await c.message.answer(KASPI_TEXT, reply_markup=pay_kb())
    await c.answer()

@dp.message(S.custom_amount)
async def custom(m: Message, state: FSMContext):
    try:
        cnt = int(m.text)
        summ = cnt * 8.8
        await state.update_data(amount=f"{cnt} ⭐️", sum=summ)
        await m.answer(KASPI_TEXT + f"\n\n<b>Итого: {cnt} ⭐️ = {summ}₸</b>", reply_markup=pay_kb())
        await state.set_state(None)
    except:
        await m.answer("<b>Напишите только число!</b>")

@dp.callback_query(F.data.startswith("p_"))
async def p_sel(c: CallbackQuery, state: FSMContext):
    mp = {"p_3_5500": "3 месяца - 5500₸", "p_6_7500": "6 месяцев - 7500₸", "p_12_14000": "12 месяцев - 14000₸"}
    sums = {"p_3_5500": 5500, "p_6_7500": 7500, "p_12_14000": 14000}
    await state.update_data(amount=mp[c.data], sum=sums[c.data])
    await c.message.answer(KASPI_TEXT, reply_markup=pay_kb())
    await c.answer()

@dp.callback_query(F.data=="i_paid")
async def paid(c: CallbackQuery, state: FSMContext):
    await state.set_state(S.check)
    await c.message.answer("<b><i>После оплаты скиньте чек с пдф файл или же фото чека</i></b>\n\n<b>Рядом с чеком скинь свой юз @</b>")
    await c.answer()

@dp.message(S.check, F.photo | F.document | F.text)
async def check(m: Message, state: FSMContext):
    global order_counter
    order_counter+=1
    d = await state.get_data()
    u = get_user(m.from_user.id, m.from_user.username, m.from_user.first_name)
    
    order = {
        "id": order_counter,
        "type": "Telegram Stars" if d.get('type')=="stars" else "Premium",
        "amount": d.get('amount', '?'),
        "sum": d.get('sum', 0),
        "to": d.get('friend', 'себе'),
        "status": "ожидает проверку ⏳"
    }
    u["orders"].append(order)
    save_db()
    
    orders[order_counter]={
        "uid": m.from_user.id,
        "data": d,
        "order": order
    }

    await m.answer(f"<b>#{order_counter} <i>заказ.Чек отправлен на проверку админа ✅\nЖдите заказ.</i></b>")

    cap = f"""<b>🔔 <i>Новый заказ #{order_counter}</i></b>

🪪 <b>ID:</b> <code>{m.from_user.id}</code>
👤 <b>Юзер:</b> @{m.from_user.username}
<b>Кому:</b> <i>{d.get('friend','себе')}</i>
<b>Что:</b> {order['type']} - {order['amount']}
<b>Сумма:</b> {order['sum']} тг
<b>Текст:</b> {m.caption or m.text or ''}"""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data=f"acc_{order_counter}"), InlineKeyboardButton(text="❌ Отклонить", callback_data=f"dec_{order_counter}")]
    ])

    try:
        if m.photo:
            await bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=cap, reply_markup=kb)
        elif m.document:
            await bot.send_document(ADMIN_ID, m.document.file_id, caption=cap, reply_markup=kb)
        else:
            await bot.send_message(ADMIN_ID, cap, reply_markup=kb)
    except Exception as e:
        print(e)
    await state.clear()

@dp.callback_query(F.data.startswith("acc_") | F.data.startswith("dec_"))
async def admin(c: CallbackQuery):
    act, oid = c.data.split("_")
    oid=int(oid)
    o = orders.get(oid)
    if not o:
        await c.answer("Не найден")
        return
    u = users_db.get(o['uid'])
    if act=="acc":
        if u:
            u["total_sum"]+=o["order"]["sum"]
            u["count"]+=1
            if "Stars" in o["order"]["type"]:
                try: u["stars"]+=int(o["order"]["amount"].split()[0])
                except: pass
            o["order"]["status"]="выдан ✅"
            if u["count"]>=3: u["level"]="Продвинутый"
            if u["count"]>=10: u["level"]="VIP"
            save_db()
        await bot.send_message(o['uid'], f"<b>#{oid} <i>заказ выдан.\nСпасибо за покупку 🍡</i></b>")
        await c.message.edit_caption(caption=c.message.caption+"\n\n<b>✅ ВЫДАН</b>", reply_markup=None)
    else:
        if u: o["order"]["status"]="отменен ❌"
        await bot.send_message(o['uid'], f"<b>#{oid} <i>заказ отклонен. Свяжитесь с поддержкой @drc1ld</i></b>")
        await c.message.edit_caption(caption=c.message.caption+"\n\n<b>❌ ОТКЛОНЕН</b>", reply_markup=None)
    await c.answer()

@dp.callback_query(F.data=="support")
async def sup(c: CallbackQuery):
    await c.message.answer("<b>💬 <i>Поддержка:</i></b>\n\n<b>Мой юз телеграмм @drc1ld</b>\n<i>Пиши, отвечаю быстро 🍡</i>", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="↩️ 𝑵𝒂з𝒂𝒅", callback_data="main")]]))
    await c.answer()

@dp.callback_query(F.data=="profile")
async def prof(c: CallbackQuery):
    u = get_user(c.from_user.id, c.from_user.username, c.from_user.first_name)
    last = ""
    if u["orders"]:
        for od in u["orders"][-2:][::-1]:
            last+=f"#{od['id']} · {od['type']} · {od['amount']} · {od['sum']} тг · {od['status']}\n"
    else:
        last="Пока нет заказов"
    txt = f"""👤 <b><i>Профиль</i></b>

🪪 <b>ID:</b> <code>{c.from_user.id}</code>
🔗 <b>Username:</b> @{c.from_user.username}
ℹ️ <b>Имя в Kaspi/MBANK:</b> <i>{u['kaspi_name']}</i>
💰 <b>Сумма покупок:</b> <i>{u['total_sum']} тг</i>
🎁 <b>Количество покупок:</b> {u['count']}
⭐ <b>Куплено Stars:</b> {u['stars']}
⭐ <b>Уровень:</b> <i>{u['level']}</i>
🎁 <b>Бонусы:</b> <i>{u['bonuses']}</i>

📅 <b>Дата регистрации:</b> {u['reg_date']}

📦 <b><i>Последние заказы:</i></b>
{last}"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 𝑴𝒐𝒊 заказы", callback_data="my_orders")],
        [InlineKeyboardButton(text="👤 Изменить имя в Kaspi/MBANK", callback_data="change_kaspi")],
        [InlineKeyboardButton(text="↩️ 𝑵𝒂з𝒂𝒅", callback_data="main")]
    ])
    await c.message.answer(txt, reply_markup=kb)
    await c.answer()

@dp.callback_query(F.data=="my_orders")
async def myo(c: CallbackQuery):
    u = get_user(c.from_user.id, c.from_user.username, c.from_user.first_name)
    if not u["orders"]:
        await c.message.answer("<b><i>У вас пока нет заказов 📦</i></b>")
    else:
        txt = "<b>📦 <i>Ваши заказы:</i></b>\n\n"
        for od in u["orders"][-10:][::-1]:
            txt+=f"#{od['id']} · {od['type']} · {od['amount']} · {od['sum']} тг · {od['status']}\n"
        await c.message.answer(txt)
    await c.answer()

@dp.callback_query(F.data=="change_kaspi")
async def ch_kas(c: CallbackQuery, state: FSMContext):
    await state.set_state(S.kaspi_name)
    await c.message.answer("<b><i>Напиши как тебя зовут в Kaspi / MBANK\nНапример: Инжу Е.</i></b>")
    await c.answer()

@dp.message(S.kaspi_name)
async def save_kas(m: Message, state: FSMContext):
    u = get_user(m.from_user.id, m.from_user.username, m.from_user.first_name)
    u["kaspi_name"]=m.text
    save_db()
    await m.answer(f"<b>✅ Сохранено: <i>{m.text}</i></b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="👤 Профиль", callback_data="profile")]]))
    await state.clear()

@dp.callback_query(F.data=="instruction")
async def inst(c: CallbackQuery):
    txt = """<b>📖 <i>Инструкция</i></b>

<b>𝟭)</b> <i>Выбираете нужный пакет который вам нужен !</i>
<b>𝟮)</b> <i>Выбирайте для вас или для друга</i>
<b>𝟯)</b> <i>Когда выберите , скиньте деньги через каспий банк !</i>

<b>После отправьте чек</b>
<b>𝟰)</b> <i>После этого я проверю и приму чек</i>

<b><i>Всем удачных покупок ! 😊</i></b>"""
    await c.message.answer(txt, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="↩️ 𝑵𝒂з𝒂𝒅", callback_data="main")]]))
    await c.answer()

@dp.callback_query(F.data=="copy")
async def copy_c(c: CallbackQuery):
    await c.answer(f"Номер {CARD} скопирован!", show_alert=True)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())