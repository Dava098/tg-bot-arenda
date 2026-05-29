import asyncio
import logging
import random
from datetime import date

import aiohttp

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)

from database import (
    cancel_booking, count_user_bookings, get_booking,
    get_user_bookings, init_db, save_booking,
)
from keyboard import (
    CARS, CITIES, OFFICES, TIME_OPTIONS,
    _fmt, get_calendar_keyboard, get_cancel_keyboard,
    get_captcha_keyboard, get_car_by_id, get_car_detail_keyboard,
    get_cars_keyboard, get_city_by_id, get_city_keyboard,
    get_lang_keyboard, get_phone_keyboard, get_skip_keyboard,
    get_time_by_id, get_time_keyboard, city_name,
    t, time_label,
)

import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN       = os.getenv("BOT_TOKEN")
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")
ADMIN_CHAT_ID   = os.getenv("ADMIN_CHAT_ID")

PAGE_SIZE = 3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class Rent(StatesGroup):
    captcha        = State()   # 0. Капча
    choosing_lang  = State()   # 1. Язык
    choosing_city  = State()   # 2. Город
    choosing_car   = State()   # 3. Список машин
    viewing_car    = State()   # 4. Карточка машины
    choosing_time  = State()   # 5. Время аренды
    choosing_date  = State()   # 6. Дата
    entering_name  = State()   # 7. Имя
    entering_phone = State()   # 8. Телефон
    entering_comment = State() # 9. Комментарий


router = Router()

async def send_car_photo(
    message: Message,
    car: dict,
    caption: str,
    lang: str,
    reply_markup=None,
) -> None:
    photo_url = car.get("image", "")

    if photo_url:
        try:
            await message.answer_photo(
                photo=photo_url,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )
            return
        except Exception as e:
            logger.warning("Не удалось отправить фото %s: %s", photo_url, e)


    await message.answer(caption, parse_mode="Markdown", reply_markup=reply_markup)

def _generate_captcha() -> tuple[str, int, list[int]]:
    kind = random.choice(["add", "sub", "mul"])

    if kind == "add":
        a, b   = random.randint(10, 50), random.randint(5, 30)
        expr   = f"{a} + {b}"
        answer = a + b
    elif kind == "sub":
        a, b   = random.randint(20, 60), random.randint(5, 20)
        expr   = f"{a} − {b}"
        answer = a - b
    else:  # mul
        a, b   = random.randint(2, 9), random.randint(2, 9)
        expr   = f"{a} × {b}"
        answer = a * b

    wrong = set()
    while len(wrong) < 3:
        delta = random.choice([-3, -2, -1, 1, 2, 3, 4, 5])
        w = answer + delta
        if w != answer and w > 0:
            wrong.add(w)

    options = [answer] + list(wrong)
    random.shuffle(options)
    return expr, answer, options

CAR_EMOJI = {
    "camry":"🚗","bmw5":"🏎","mercedes":"💎","audi_a6":"⚡",
    "ferrari":"🔴","lamborghini":"🟡","cadillac":"🖤",
    "lacetti":"🚙","malibu":"🚘","byd_han":"🔋",
    "voyah":"🌐","cobalt":"🚗",
}


def _history_list_keyboard(bookings: list, page: int, lang: str) -> InlineKeyboardMarkup:
    rows  = []
    start = page * PAGE_SIZE
    for b in bookings[start: start + PAGE_SIZE]:
        em = CAR_EMOJI.get(b["car_id"], "🚗")
        st = "✅" if b["status"] == "active" else "❌"
        rows.append([InlineKeyboardButton(
            text=f"{st}{em} {b['car_name']}  {b['rental_date']}  {_fmt(b['total_price'])} {t(lang,'sum')}",
            callback_data=f"hist:detail:{b['id']}:{page}",
        )])
    nav   = []
    total = len(bookings)
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"hist:page:{page-1}"))
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    nav.append(InlineKeyboardButton(text=f"{page+1}/{pages}", callback_data="hist:ignore"))
    if (page + 1) * PAGE_SIZE < total:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"hist:page:{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(text=t(lang,"close_btn"), callback_data="hist:close")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _detail_keyboard(booking_id: str, status: str, page: int, lang: str) -> InlineKeyboardMarkup:
    rows = []
    if status == "active":
        rows.append([InlineKeyboardButton(
            text=t(lang,"cancel_order_btn"),
            callback_data=f"hist:cancel:{booking_id}:{page}",
        )])
    rows.append([InlineKeyboardButton(
        text=t(lang,"back_to_list_btn"), callback_data=f"hist:page:{page}",
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _booking_card(b: dict, lang: str = "ru") -> str:
    em     = CAR_EMOJI.get(b["car_id"], "🚗")
    bl     = b["lang"] if b.get("lang") else lang
    st_lbl = t(bl, "status_active") if b["status"]=="active" else t(bl,"status_cancelled")
    st_em  = "✅" if b["status"]=="active" else "❌"
    comment= f"{t(bl,'comment_prefix')} _{b['comment']}_\n" if b.get("comment") else ""
    try:
        dt = b["created_at"][:16].replace("T"," ")
    except Exception:
        dt = b["created_at"]
    return (
        f"{st_em} *{t(bl,'order_num').format(id=b['id'])}*  —  {st_lbl}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{t(bl,'city_lbl')}: *{b.get('city','—')}*\n"
        f"{em} {t(bl,'car_lbl').capitalize()}: *{b['car_name']}*\n"
        f"{t(bl,'time_lbl')}: *{b['rental_time']}*\n"
        f"{t(bl,'date_lbl')}: *{b['rental_date']}*\n"
        f"{t(bl,'client_lbl')}: *{b['client_name']}*\n"
        f"{t(bl,'phone_lbl')}: *{b['phone']}*\n"
        f"{comment}"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{t(bl,'total_lbl')}: *{_fmt(b['total_price'])} {t(bl,'sum')}*\n"
        f"🕐 {dt} UTC"
    )


async def _send_history_page(
    target: Message | CallbackQuery,
    user_id: int,
    page: int,
    lang: str,
    edit: bool = False,
) -> None:
    bookings = get_user_bookings(user_id)
    total    = len(bookings)

    if total == 0:
        text = f"{t(lang,'history_title')}\n\n{t(lang,'no_bookings')}"
        msg  = target if isinstance(target, Message) else target.message
        await msg.answer(text, parse_mode="Markdown")
        return

    active   = sum(1 for b in bookings if b["status"] == "active")
    spent    = sum(b["total_price"] for b in bookings if b["status"] == "active")
    pages    = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    header = (
        f"{t(lang,'history_title')}\n\n"
        f"{t(lang,'orders_stat',total=total,active=active,cancelled=total-active,spent=_fmt(spent))}\n\n"
        f"{t(lang,'page_info',cur=page+1,total=pages)}"
    )
    kb = _history_list_keyboard(bookings, page, lang)

    if edit and isinstance(target, CallbackQuery):
        await target.message.edit_text(header, parse_mode="Markdown", reply_markup=kb)
    else:
        msg = target if isinstance(target, Message) else target.message
        await msg.answer(header, parse_mode="Markdown", reply_markup=kb)


async def _notify_admin(booking_id: str, data: dict, comment: str) -> None:
    import html as _html
    if not ADMIN_BOT_TOKEN or ADMIN_BOT_TOKEN == "ADMIN_BOT_TOKEN_HERE":
        logger.warning("⚠️ ADMIN_BOT_TOKEN не задан — уведомление не отправлено")
        return
    if not ADMIN_CHAT_ID or ADMIN_CHAT_ID == "ADMIN_CHAT_ID_HERE":
        logger.warning("⚠️ ADMIN_CHAT_ID не задан — уведомление не отправлено")
        return
    try:
        admin_bot = Bot(token=ADMIN_BOT_TOKEN)
        car_em    = CAR_EMOJI.get(data["car_id"], "🚗")
        comment_l = f"💬 <i>{_html.escape(comment)}</i>\n" if comment else ""
        text = (
            f"🔔 <b>Новая бронь #{_html.escape(str(booking_id))}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 Город: <b>{_html.escape(str(data.get('city', '—')))}</b>\n"
            f"{car_em} Автомобиль: <b>{_html.escape(str(data['car_name']))}</b>\n"
            f"⏱ Время: <b>{_html.escape(str(data['rental_time']))}</b>\n"
            f"📅 Дата: <b>{_html.escape(str(data['rental_date']))}</b>\n"
            f"👤 Клиент: <b>{_html.escape(str(data['client_name']))}</b>\n"
            f"📱 Телефон: <b>{_html.escape(str(data['phone']))}</b>\n"
            f"{comment_l}"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Итого: <b>{_fmt(data['total_price'])} сум</b>\n"
            f"🌐 Язык: {data.get('lang', 'ru').upper()}\n"
            f"👤 @{_html.escape(str(data.get('username') or '—'))}"
        )
        await admin_bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode="HTML")
        await admin_bot.session.close()
        logger.info("✅ Уведомление о брони #%s отправлено в админ-чат", booking_id)
    except Exception as e:
        logger.error("❌ Не удалось отправить уведомление админу: %s", e)


async def _notify_admin_cancel(booking: dict, cancelled_by_username: str) -> None:
    import html as _html
    if not ADMIN_BOT_TOKEN or ADMIN_BOT_TOKEN == "ADMIN_BOT_TOKEN_HERE":
        logger.warning("⚠️ ADMIN_BOT_TOKEN не задан — уведомление об отмене не отправлено")
        return
    if not ADMIN_CHAT_ID or ADMIN_CHAT_ID == "ADMIN_CHAT_ID_HERE":
        logger.warning("⚠️ ADMIN_CHAT_ID не задан — уведомление об отмене не отправлено")
        return
    try:
        admin_bot = Bot(token=ADMIN_BOT_TOKEN)
        car_em = CAR_EMOJI.get(booking["car_id"], "🚗")
        text = (
            f"❌ <b>Бронь #{_html.escape(str(booking['id']))} ОТМЕНЕНА клиентом</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 Город: <b>{_html.escape(str(booking.get('city', '—')))}</b>\n"
            f"{car_em} Автомобиль: <b>{_html.escape(str(booking['car_name']))}</b>\n"
            f"⏱ Время: <b>{_html.escape(str(booking['rental_time']))}</b>\n"
            f"📅 Дата: <b>{_html.escape(str(booking['rental_date']))}</b>\n"
            f"👤 Клиент: <b>{_html.escape(str(booking['client_name']))}</b>\n"
            f"📱 Телефон: <b>{_html.escape(str(booking['phone']))}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Сумма: <b>{_fmt(booking['total_price'])} сум</b>\n"
            f"👤 @{_html.escape(str(cancelled_by_username or '—'))}"
        )
        await admin_bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode="HTML")
        await admin_bot.session.close()
        logger.info("✅ Уведомление об отмене брони #%s отправлено в админ-чат", booking["id"])
    except Exception as e:
        logger.error("❌ Не удалось отправить уведомление об отмене: %s", e)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()

    expr, answer, options = _generate_captcha()
    await state.update_data(captcha_answer=answer, captcha_attempts=0)

    await message.answer(
        t("ru", "captcha_prompt", expr=expr),
        parse_mode="Markdown",
        reply_markup=get_captcha_keyboard(answer, options),
    )
    await state.set_state(Rent.captcha)


@router.message(Command("history"))
async def cmd_history(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang")
    if not lang:
        bookings = get_user_bookings(message.from_user.id)
        lang = bookings[0]["lang"] if bookings else "ru"
    await _send_history_page(message, message.from_user.id, page=0, lang=lang)


@router.message(F.text.in_(["❌ Отмена", "❌ Cancel", "❌ Bekor qilish"]))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await state.clear()
    await message.answer(
        t(lang, "cancel_text"),
        reply_markup=ReplyKeyboardRemove(),
    )

@router.callback_query(F.data.startswith("captcha:"), Rent.captcha)
async def captcha_answer(cb: CallbackQuery, state: FSMContext) -> None:
    parts  = cb.data.split(":")   # captcha : ok/fail : число
    result = parts[1]             # "ok" или "fail"
    data   = await state.get_data()

    if result == "ok":
        await cb.answer(t("ru", "captcha_ok"), show_alert=False)
        await cb.message.edit_text(
            "🌐 *Выберите язык / Choose language / Tilni tanlang:*",
            parse_mode="Markdown",
            reply_markup=get_lang_keyboard(),
        )
        await state.set_state(Rent.choosing_lang)
    else:
        attempts = data.get("captcha_attempts", 0) + 1
        await state.update_data(captcha_attempts=attempts)

        if attempts >= 3:
            # Генерируем новую капчу после 3 попыток
            expr, answer, options = _generate_captcha()
            await state.update_data(captcha_answer=answer, captcha_attempts=0)
            await cb.answer(t("ru", "captcha_fail"), show_alert=True)
            await cb.message.edit_text(
                t("ru", "captcha_prompt", expr=expr),
                parse_mode="Markdown",
                reply_markup=get_captcha_keyboard(answer, options),
            )
        else:
            await cb.answer(t("ru", "captcha_fail"), show_alert=True)

@router.callback_query(F.data == "hist:ignore")
async def hist_ignore(cb: CallbackQuery) -> None:
    await cb.answer()


@router.callback_query(F.data == "hist:close")
async def hist_close(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await cb.message.delete()
    await cb.answer(t(lang, "hist_closed"))


@router.callback_query(F.data.startswith("hist:page:"))
async def hist_page(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang")
    if not lang:
        bookings = get_user_bookings(cb.from_user.id)
        lang = bookings[0]["lang"] if bookings else "ru"
    page = int(cb.data.split(":")[2])
    await _send_history_page(cb, cb.from_user.id, page=page, lang=lang, edit=True)
    await cb.answer()


@router.callback_query(F.data.startswith("hist:detail:"))
async def hist_detail(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    parts = cb.data.split(":")
    bid, page = parts[2], int(parts[3])
    b = get_booking(bid)
    if not b:
        await cb.answer(t(lang, "not_found"), show_alert=True)
        return
    await cb.message.edit_text(
        _booking_card(b, lang), parse_mode="Markdown",
        reply_markup=_detail_keyboard(bid, b["status"], page, lang),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("hist:cancel:"))
async def hist_cancel(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    parts = cb.data.split(":")
    bid, page = parts[2], int(parts[3])
    if cancel_booking(bid, cb.from_user.id):
        await cb.answer(t(lang, "cancelled_ok"), show_alert=True)
        b = get_booking(bid)
        await cb.message.edit_text(
            _booking_card(b, lang), parse_mode="Markdown",
            reply_markup=_detail_keyboard(bid, b["status"], page, lang),
        )
        await _notify_admin_cancel(b, cb.from_user.username)

        cancel_messages = {
            "ru": "Извините за беспокойство. В чем проблема, из-за которой Вы отменили бронь? Буду ждать ответа.",
            "uz": "Bezovta qilganim uchun uzr. Bronni bekor qilishingizga sabab bo'lgan muammo nima? Javobingizni kutaman.",
            "en": "Sorry for the inconvenience. What was the issue that caused you to cancel your booking? I will be waiting for your answer.",
        }
        msg = cancel_messages.get(lang, cancel_messages["ru"])
        await cb.message.answer(msg)
    else:
        await cb.answer(t(lang, "cancel_fail"), show_alert=True)


@router.callback_query(F.data.startswith("lang:"), Rent.choosing_lang)
async def lang_selected(cb: CallbackQuery, state: FSMContext) -> None:
    lang = cb.data.split(":")[1]
    await state.update_data(lang=lang)
    await cb.answer()
    await cb.message.edit_text(
        t(lang, "welcome"),
        parse_mode="Markdown",
    )
    # Передаём lang в get_city_keyboard — названия городов на нужном языке
    await cb.message.answer(
        t(lang, "choose_city"),
        parse_mode="Markdown",
        reply_markup=get_city_keyboard(lang),
    )
    await state.set_state(Rent.choosing_city)

@router.callback_query(F.data.startswith("city:"), Rent.choosing_city)
async def city_selected(cb: CallbackQuery, state: FSMContext) -> None:
    data    = await state.get_data()
    lang    = data.get("lang", "ru")
    city_id = cb.data.split(":")[1]
    city    = get_city_by_id(city_id)
    if not city:
        await cb.answer("?", show_alert=True)
        return

    # Сохраняем название города на языке пользователя
    cname = city_name(city, lang)
    await state.update_data(city=cname, city_id=city_id)
    await cb.answer(cname)
    await cb.message.edit_text(
        f"📍 *{cname}*\n\n{t(lang,'choose_car')}",
        parse_mode="Markdown",
        reply_markup=get_cars_keyboard(),
    )
    await state.set_state(Rent.choosing_car)

@router.callback_query(F.data.startswith("carview:"), Rent.choosing_car)
async def car_view(cb: CallbackQuery, state: FSMContext) -> None:
    data   = await state.get_data()
    lang   = data.get("lang", "ru")
    car_id = cb.data.split(":")[1]
    car    = get_car_by_id(car_id)
    if not car:
        await cb.answer("?", show_alert=True)
        return

    await cb.answer()
    desc    = car.get(f"description_{lang}", car["description"])
    specs   = car.get(f"specs_{lang}", car["specs"])
    caption = (
        f"{car['emoji']} *{car['name']}*\n"
        f"_{desc}_\n\n"
        f"{specs}\n\n"
        f"💰 *{_fmt(car['price_per_hour'])} {t(lang,'per_hour')}*"
    )
    await cb.message.delete()

    # Отправляем AI-сгенерированное фото «на лету»
    await send_car_photo(
        message=cb.message,
        car=car,
        caption=caption,
        lang=lang,
        reply_markup=get_car_detail_keyboard(car_id, lang),
    )
    await state.set_state(Rent.viewing_car)

@router.callback_query(F.data == "cars:back", Rent.viewing_car)
async def cars_back(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await cb.answer()
    await cb.message.delete()
    await cb.message.answer(
        f"📍 *{data.get('city','—')}*\n\n{t(lang,'choose_car')}",
        parse_mode="Markdown",
        reply_markup=get_cars_keyboard(),
    )
    await state.set_state(Rent.choosing_car)

@router.callback_query(F.data.startswith("car:"), Rent.viewing_car)
async def car_selected(cb: CallbackQuery, state: FSMContext) -> None:
    data   = await state.get_data()
    lang   = data.get("lang", "ru")
    car_id = cb.data.split(":")[1]
    car    = get_car_by_id(car_id)
    if not car:
        await cb.answer("?", show_alert=True)
        return

    await state.update_data(
        car_id=car_id, car_name=car["name"],
        price_per_hour=car["price_per_hour"],
    )
    await cb.answer(f"✅ {car['name']}")
    await cb.message.answer(
        t(lang, "choose_time", car=car["name"]),
        parse_mode="Markdown",
        reply_markup=get_time_keyboard(car["price_per_hour"], lang),
    )
    await state.set_state(Rent.choosing_time)

@router.callback_query(F.data == "time:back", Rent.choosing_time)
async def time_back(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await cb.answer()
    await cb.message.answer(
        f"📍 *{data.get('city','—')}*\n\n{t(lang,'choose_car')}",
        parse_mode="Markdown",
        reply_markup=get_cars_keyboard(),
    )
    await state.set_state(Rent.choosing_car)

@router.callback_query(F.data.startswith("time:"), Rent.choosing_time)
async def time_selected(cb: CallbackQuery, state: FSMContext) -> None:
    if cb.data == "time:back":
        return
    data    = await state.get_data()
    lang    = data.get("lang", "ru")
    time_id = cb.data.split(":")[1]
    opt     = get_time_by_id(time_id)
    if not opt:
        await cb.answer("?", show_alert=True)
        return

    total = int(data["price_per_hour"] * opt["coeff"])
    lbl   = time_label(opt, lang)

    await state.update_data(
        rental_time=lbl, rental_hours=opt["hours"], total_price=total,
    )
    await cb.answer(f"✅ {lbl}")

    today = date.today()
    await cb.message.answer(
        t(lang, "choose_date", time=lbl, price=_fmt(total)),
        parse_mode="Markdown",
        reply_markup=get_calendar_keyboard(today.year, today.month, lang),
    )
    await state.set_state(Rent.choosing_date)

@router.callback_query(F.data == "cal:ignore")
async def cal_ignore(cb: CallbackQuery) -> None:
    await cb.answer()


@router.callback_query(F.data.startswith("cal:prev:"), StateFilter(Rent.choosing_date, Rent.entering_name))
async def cal_prev(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    parts = cb.data.split(":")
    year, month = int(parts[2]), int(parts[3])
    month -= 1
    if month < 1:
        month, year = 12, year - 1
    today = date.today()
    if (year, month) < (today.year, today.month):
        await cb.answer(t(lang, "prev_month_err"), show_alert=True)
        return
    await cb.message.edit_reply_markup(
        reply_markup=get_calendar_keyboard(year, month, lang))
    await cb.answer()


@router.callback_query(F.data.startswith("cal:next:"), StateFilter(Rent.choosing_date, Rent.entering_name))
async def cal_next(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    parts = cb.data.split(":")
    year, month = int(parts[2]), int(parts[3])
    month += 1
    if month > 12:
        month, year = 1, year + 1
    await cb.message.edit_reply_markup(
        reply_markup=get_calendar_keyboard(year, month, lang))
    await cb.answer()


@router.callback_query(F.data.startswith("cal:day:"), Rent.entering_name)
async def date_reselected(cb: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Rent.choosing_date)
    await date_selected(cb, state)


@router.callback_query(F.data.startswith("cal:day:"), Rent.choosing_date)
async def date_selected(cb: CallbackQuery, state: FSMContext) -> None:
    data      = await state.get_data()
    lang      = data.get("lang", "ru")
    parts     = cb.data.split(":")
    selected  = date(int(parts[2]), int(parts[3]), int(parts[4]))
    formatted = selected.strftime("%d.%m.%Y")

    # Удаляем предыдущее сообщение "введи имя", если дату меняют повторно
    prev_msg_id = data.get("date_prompt_msg_id")
    if prev_msg_id:
        try:
            await cb.bot.delete_message(chat_id=cb.message.chat.id, message_id=prev_msg_id)
        except Exception:
            pass

    await state.update_data(rental_date=formatted)
    await cb.answer(f"📅 {formatted}")
    sent = await cb.message.answer(
        t(lang, "enter_name", date=formatted),
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(lang),
    )
    await state.update_data(date_prompt_msg_id=sent.message_id)
    await state.set_state(Rent.entering_name)

@router.message(Rent.entering_name, F.text)
async def name_entered(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    name = message.text.strip()
    if len(name) < 2 or any(ch.isdigit() for ch in name):
        await message.answer(t(lang, "invalid_name"))
        return
    await state.update_data(client_name=name)
    await message.answer(
        t(lang, "enter_phone", name=name),
        parse_mode="Markdown",
        reply_markup=get_phone_keyboard(lang),
    )
    await state.set_state(Rent.entering_phone)

@router.message(Rent.entering_phone, F.contact)
async def phone_from_contact(message: Message, state: FSMContext) -> None:
    await _process_phone(message, state, message.contact.phone_number)


@router.message(Rent.entering_phone, F.text)
async def phone_from_text(message: Message, state: FSMContext) -> None:
    data   = await state.get_data()
    lang   = data.get("lang", "ru")
    raw    = message.text.strip()
    digits = raw.replace("+","").replace("-","").replace(" ","").replace("(","").replace(")","")
    if not digits.isdigit() or len(digits) < 9:
        await message.answer(t(lang, "invalid_phone"), parse_mode="Markdown")
        return
    await _process_phone(message, state, raw)


async def _process_phone(message: Message, state: FSMContext, phone: str) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await state.update_data(phone=phone)
    await message.answer(
        t(lang, "enter_comment", phone=phone),
        parse_mode="Markdown",
        reply_markup=get_skip_keyboard(lang),
    )
    await state.set_state(Rent.entering_comment)


@router.message(Rent.entering_comment, F.text)
async def comment_entered(message: Message, state: FSMContext) -> None:
    data    = await state.get_data()
    lang    = data.get("lang", "ru")
    skip_tx = t(lang, "skip_btn")
    comment = "" if message.text.strip() == skip_tx else message.text.strip()
    await _finalize(message, state, comment)


async def _finalize(message: Message, state: FSMContext, comment: str) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")

    booking_data = {
        "user_id":      message.from_user.id,
        "username":     message.from_user.username or "",
        "lang":         lang,
        "city":         data.get("city", ""),
        "car_id":       data["car_id"],
        "car_name":     data["car_name"],
        "rental_time":  data["rental_time"],
        "rental_hours": data["rental_hours"],
        "rental_date":  data["rental_date"],
        "client_name":  data["client_name"],
        "phone":        data["phone"],
        "comment":      comment,
        "total_price":  data["total_price"],
    }

    booking_id   = save_booking(booking_data)
    total_orders = count_user_bookings(message.from_user.id)
    city_id      = data.get("city_id", "tashkent")
    office       = OFFICES.get(city_id, OFFICES["tashkent"])
    car_em       = CAR_EMOJI.get(data["car_id"], "🚗")
    comment_line = f"{t(lang,'comment_prefix')} _{comment}_\n" if comment else ""

    await state.clear()

    await message.answer(
        f"{t(lang,'confirmed_title')}\n\n"
        f"{t(lang,'order_num',id=booking_id)}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{t(lang,'city_lbl')}: *{data.get('city','—')}*\n\n"
        f"{car_em} {t(lang,'car_lbl').capitalize()}: *{data['car_name']}*\n\n"
        f"{t(lang,'time_lbl')}: *{data['rental_time']}*\n\n"
        f"{t(lang,'date_lbl')}: *{data['rental_date']}*\n\n"
        f"{t(lang,'client_lbl')}: *{data['client_name']}*\n\n"
        f"{t(lang,'phone_lbl')}: *{data['phone']}*\n\n"
        f"{comment_line}"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{t(lang,'total_lbl')}: *{_fmt(data['total_price'])} {t(lang,'sum')}*\n\n"
        f"{t(lang,'manager_msg')}",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )

    await message.answer(
        f"{t(lang,'cash_title')}\n\n{t(lang,'cash_text')}",
        parse_mode="Markdown",
    )

    await message.answer(
        t(lang, "office_phone", phone=office["phone"]),
        parse_mode="Markdown",
    )

    await message.answer_venue(
        latitude=office["lat"],
        longitude=office["lon"],
        title=office["title"],
        address=office["address"],
    )

    await message.answer(
        f"{t(lang,'new_booking')}\n"
        f"📋 /history\n\n"
        f"{t(lang,'your_orders',n=total_orders)}",
        parse_mode="Markdown",
    )

    await _notify_admin(booking_id, booking_data, comment)

    logger.info(
        "Бронь #%s | user=%s | %s | %s | %s сум",
        booking_id, message.from_user.id,
        data["car_name"], data["rental_date"], data["total_price"],
    )




async def main() -> None:
    init_db()
    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    logger.info("🤖 Бот запущен!!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())