import calendar
from datetime import date

from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup,
)

TEXTS = {
    "ru": {
        "choose_lang": "🌐 Выберите язык:",
        "choose_city": "📍 Выберите ваш *город*:",
        "choose_car": "🚗 Выберите *автомобиль*:",
        "choose_time": "✅ Автомобиль: *{car}*\n\n⏱ Выберите предоставленное *время аренды*:",
        "choose_date": "✅ Время аренды: *{time}*\n💰 Стоимость выбранного времени: *{price} сум*\n\n📅 Выберите *дату аренды*:",
        "enter_name": "✅ Дата аренды: *{date}*\n\n👤 Введите ваше *Фамилию и Имя*:",
        "enter_phone": "👤 Имя: *{name}*\n\n📱 Введите *номер телефона* или нажмите кнопку ниже:",
        "enter_comment": "📱 Телефон: *{phone}*\n\n💬 Введите *комментарий к заказу*\n_Например: нужно привзти машу к аэрапорту TAS( Международный Аэропорт имени Ислама Каримова )_\n\nИли нажмите *«Пропустить»*.",
        "invalid_name": "⚠️ Введите корректное имя (только буквы, минимум 2 символа).",
        "invalid_phone": "⚠️ Введите корректный номер.\nПример: *+998 99 999 99 99*",
        "cancel_text": "❌ Бронирование отменено.\n\n🚗 Новое бронирование: /start\n📋 История Ваших аренд: /history",
        "cancel_btn": "❌ Отмена",
        "skip_btn": "➡️ Пропустить",
        "send_phone_btn": "📱 Отправить мой номер телефона",
        "select_car_btn": "✅ Выбрать эту машину",
        "back_to_cars_btn": "◀️ Назад к списку машин",
        "back_to_time_btn": "◀️ Назад к машинам",
        "confirmed_title": "✅ *Бронирование подтверждено!*",
        "order_num": "🔖 Номер заказа: *#{id}*",
        "city_lbl": "📍 Город",
        "car_lbl": "автомобиль",
        "time_lbl": "⏱ Время аренды",
        "date_lbl": "📅 Дата",
        "client_lbl": "👤 Имя клиента",
        "phone_lbl": "📱 Телефон клиента",
        "total_lbl": "💰 Итоговая оплата за аренду",
        "comment_prefix": "💬 Коментарий",
        "manager_msg": "Наш менеджер свяжется с вами за 1 одень до выбранного дня аренды.",
        "cash_title": "💵 *Оплата наличными или картой в нашем офисе*",
        "cash_text": "В нашем офисе принимается оплата при получении автомобиля.\nПожалуйста, подготовьте точную сумму и документы (паспорт) заранее. Спасибо за понимание!",
        "office_phone": "📞 *Телефон нашего офиса:* `{phone}`",
        "new_booking": "🚗 Новое бронирование: /start",
        "your_orders": "Всего Вы сделали заказов: *{n}*",
        "history_title": "📋 *История аренды*",
        "no_bookings": "У Вас ещё нет бронирований.\nНажмите /start чтобы оформить аренду.",
        "orders_stat": "Всего заказов: *{total}*  (✅ {active} активных  |  ❌ {cancelled} отменённых)\n💰 Активных на сумму: *{spent} сум*",
        "page_info": "Страница {cur} из {total} — нажмите на заказ для деталей:",
        "status_active": "Активно",
        "status_cancelled": "Отменено",
        "back_to_list_btn": "◀️ К списку",
        "cancel_order_btn": "❌ Отменить это бронирование",
        "close_btn": "🔒 Закрыть",
        "cancelled_ok": "❌ Бронирование отменено",
        "cancel_fail": "Не удалось отменить — уже отменено.",
        "not_found": "Заказ не найден.",
        "hist_closed": "История закрыта",
        "prev_month_err": "Нельзя выбрать прошедший месяц.",
        "sum": "сум",
        "per_hour": "сум/час",
        "welcome": "🚗 *Добро пожаловать в Rent A Car!*\n\n📋 История аренд: /history",
        # Капча
        "captcha_prompt": "🔐 *Проверка безопасности*\n\nРешите пример, чтобы подтвердить, что Вы не Бот: *{expr} = ?*\n\nВыберите правильный ответ ниже:",
        "captcha_ok": "✅ Верно! Добро пожаловать в наш Бот.",
        "captcha_fail": "❌ Неверно. Попробуйте ещё раз.",

    },
    "en": {
        "choose_lang": "🌐 Choose a language:",
        "choose_city": "📍 Choose your *city*: ",
        "choose_car": "🚗 Choose a *car*: ",
        "choose_time": "✅ Car: *{car}*\n\n⏱ Choose rental *time*: ",
        "choose_date": "✅ Time: *{time}*\n💰 Price for selected time: *{price} UZS*\n\n📅 Choose rental *date*: ",
        "enter_name": "✅ Date: *{date}*\n\n👤 Enter your *Last Name and First Name*: ",
        "enter_phone": "👤 Name: *{name}*\n\n📱 Enter your *phone number* or press the button below: ",
        "enter_comment": "📱 Phone: *{phone}*\n\n💬 Enter an *order comment*\n_For example: deliver the car to TAS airport (Islam Karimov International Airport)_\n\nOr press *Skip*.",
        "invalid_name": "⚠️ Enter a valid name (letters only, at least 2 characters).",
        "invalid_phone": "⚠️ Enter a valid phone number.\nExample: *+998 99 999 99 99*",
        "cancel_text": "❌ Booking cancelled.\n\n🚗 New booking: /start\n📋 Your rental history: /history",
        "cancel_btn": "❌ Cancel",
        "skip_btn": "➡️ Skip",
        "send_phone_btn": "📱 Send my phone number",
        "select_car_btn": "✅ Select this car",
        "back_to_cars_btn": "◀️ Back to car list",
        "back_to_time_btn": "◀️ Back to cars",
        "confirmed_title": "✅ *Booking confirmed!*",
        "order_num": "🔖 Order number: *#{id}*",
        "city_lbl": "📍 City",
        "car_lbl": "Car",
        "time_lbl": "⏱ Rental time",
        "date_lbl": "📅 Date",
        "client_lbl": "👤 Client name",
        "phone_lbl": "📱 Client phone",
        "total_lbl": "💰 Total rental payment",
        "comment_prefix": "💬 Comment",
        "manager_msg": "Our manager will contact you 1 day before the rental date.",
        "cash_title": "💵 *Cash or card payment in our office*",
        "cash_text": "Payment is accepted in our office when receiving the car.\nPlease prepare the exact amount and documents (passport) in advance. Thank you!",
        "office_phone": "📞 *Office phone:* `{phone}`",
        "new_booking": "🚗 New booking: /start",
        "your_orders": "Total orders: *{n}*",
        "history_title": "📋 *Rental history*",
        "no_bookings": "You have no bookings yet.\nPress /start to rent a car.",
        "orders_stat": "Total orders: *{total}*  (✅ {active} active  |  ❌ {cancelled} cancelled)\n💰 Active total: *{spent} UZS*",
        "page_info": "Page {cur} of {total} — click an order for details:",
        "status_active": "Active",
        "status_cancelled": "Cancelled",
        "back_to_list_btn": "◀️ Back to list",
        "cancel_order_btn": "❌ Cancel this booking",
        "close_btn": "🔒 Close",
        "cancelled_ok": "❌ Booking cancelled",
        "cancel_fail": "Cannot cancel — already cancelled.",
        "not_found": "Order not found.",
        "hist_closed": "History closed",
        "prev_month_err": "Cannot select past month.",
        "sum": "UZS",
        "per_hour": "UZS/hour",
        "welcome": "🚗 *Welcome to Rent A Car!*\n\n📋 Rental history: /history",
        "captcha_prompt": "🔐 *Security check*\n\nSolve the equation: *{expr} = ?*\n\nChoose correct answer:",
        "captcha_ok": "✅ Correct! Welcome.",
        "captcha_fail": "❌ Wrong answer. Try again."
    },
    "uz": {
        "choose_lang": "🌐 Tilni tanlang:",
    "choose_city": "📍 O'zingizning *shahringizni* tanlang:",
    "choose_car": "🚗 *Mashina* tanlang:",
    "choose_time": "✅ Mashina: *{car}*\n\n⏱ Ijara *vaqtini* tanlang:",
    "choose_date": "✅ Ijara vaqti: *{time}*\n💰 Tanlangan vaqt narxi: *{price} so'm*\n\n📅 Ijara *sanani* tanlang:",
    "enter_name": "✅ Sana: *{date}*\n\n👤 *Familiya va ismingizni* kiriting:",
    "enter_phone": "👤 Ism: *{name}*\n\n📱 *Telefon raqamingizni* kiriting yoki pastdagi tugmani bosing:",
    "enter_comment": "📱 Telefon: *{phone}*\n\n💬 *Buyurtma uchun izoh* kiriting\n_Masalan: mashinani TAS aeroportiga (Islom Karimov nomidagi xalqaro aeroport) olib kelish kerak_\n\nYoki *“O'tkazib yuborish”* tugmasini bosing.",
    "invalid_name": "⚠️ To'g'ri ism kiriting (faqat harflar, kamida 2 ta belgi).",
    "invalid_phone": "⚠️ To'g'ri telefon raqam kiriting.\nMisol: *+998 99 999 99 99*",
    "cancel_text": "❌ Bron bekor qilindi.\n\n🚗 Yangi bron: /start\n📋 Ijara tarixi: /history",
    "cancel_btn": "❌ Bekor qilish",
    "skip_btn": "➡️ O'tkazib yuborish",
    "send_phone_btn": "📱 Telefon raqamimni yuborish",
    "select_car_btn": "✅ Shu mashinani tanlash",
    "back_to_cars_btn": "◀️ Mashinalar ro'yxatiga qaytish",
    "back_to_time_btn": "◀️ Mashinalarga qaytish",
    "confirmed_title": "✅ *Bron tasdiqlandi!*",
    "order_num": "🔖 Buyurtma raqami: *#{id}*",
    "city_lbl": "📍 Shahar",
    "car_lbl": "Mashina",
    "time_lbl": "⏱ Ijara vaqti",
    "date_lbl": "📅 Sana",
    "client_lbl": "👤 Mijoz ismi",
    "phone_lbl": "📱 Mijoz telefoni",
    "total_lbl": "💰 Umumiy to'lov",
    "comment_prefix": "💬 Izoh",
    "manager_msg": "Menejerimiz siz bilan ijara sanasidan 1 kun oldin bog'lanadi.",
    "cash_title": "💵 *Ofisda naqd yoki karta orqali to'lov*",
    "cash_text": "Mashina topshirilganda to'lov ofisimizda qabul qilinadi.\nIltimos, kerakli summani va hujjatlarni (pasport) oldindan tayyorlab qo'ying. Rahmat!",
    "office_phone": "📞 *Ofis telefonimiz:* `{phone}`",
    "new_booking": "🚗 Yangi bron: /start",
    "your_orders": "Jami buyurtmalar: *{n}*",
    "history_title": "📋 *Ijara tarixi*",
    "no_bookings": "Sizda hali bron yo'q.\nBoshlash uchun /start ni bosing.",
    "orders_stat": "Jami buyurtmalar: *{total}*  (✅ {active} faol  |  ❌ {cancelled} bekor qilingan)\n💰 Faol buyurtmalar summasi: *{spent} so'm*",
    "page_info": "Sahifa {cur} / {total} — buyurtmani bosib tafsilotlarni ko'ring:",
    "status_active": "Faol",
    "status_cancelled": "Bekor qilingan",
    "back_to_list_btn": "◀️ Ro'yxatga qaytish",
    "cancel_order_btn": "❌ Ushbu bronni bekor qilish",
    "close_btn": "🔒 Yopish",
    "cancelled_ok": "❌ Bron bekor qilindi",
    "cancel_fail": "Bekor qilib bo'lmadi — allaqachon bekor qilingan.",
    "not_found": "Buyurtma topilmadi.",
    "hist_closed": "Tarix yopildi",
    "prev_month_err": "O'tgan oyni tanlab bo'lmaydi.",
    "sum": "so'm",
    "per_hour": "so'm/soat",
    "welcome": "🚗 *Rent A Car xizmatiga xush kelibsiz!*\n\n📋 Ijara tarixi: /history",
    "captcha_prompt": "🔐 *Xavfsizlik tekshiruvi*\n\nBot emasligingizni tasdiqlash uchun misolni yeching: *{expr} = ?*\n\nTo'g'ri javobni tanlang:",
    "captcha_ok": "✅ To'g'ri! Xush kelibsiz.",
    "captcha_fail": "❌ Noto'g'ri. Qayta urinib ko'ring."
    }
}


def t(lang: str, key: str, **kwargs) -> str:
    text = TEXTS.get(lang, TEXTS["ru"]).get(key, TEXTS["ru"].get(key, key))
    return text.format(**kwargs) if kwargs else text


OFFICES: dict = {
    "tashkent": {
        "lat": 41.2995, "lon": 69.2401,
        "title": "Rent A Car Tashkent",
        "address": "Мирабадский район, ул. Мустақиллик",
        "phone": "+998 71 123 45 67",
    },
    "samarkand": {
        "lat": 39.6542, "lon": 66.9597,
        "title": "Rent A Car Samarkand",
        "address": "ул. Регистан, 12",
        "phone": "+998 66 234 56 78",
    },
    "bukhara": {
        "lat": 39.7747, "lon": 64.4286,
        "title": "Rent A Car Bukhara",
        "address": "ул. Мухаммад Иқбол, 5",
        "phone": "+998 65 345 67 89",
    },
    "navoi": {
        "lat": 40.0849, "lon": 65.3792,
        "title": "Rent A Car Navoi",
        "address": "пр. Навои, 18",
        "phone": "+998 79 456 78 90",
    },
    "andijan": {
        "lat": 40.7821, "lon": 72.3442,
        "title": "Rent A Car Andijan",
        "address": "ул. Бабур, 24",
        "phone": "+998 74 567 89 01",
    },
}

CITIES: list[dict] = [
    {
        "id": "tashkent",
        "name_ru": "🏙 Ташкент",
        "name_en": "🏙 Tashkent",
        "name_uz": "🏙 Toshkent",
    },
    {
        "id": "samarkand",
        "name_ru": "🕌 Самарканд",
        "name_en": "🕌 Samarkand",
        "name_uz": "🕌 Samarqand",
    },
    {
        "id": "bukhara",
        "name_ru": "🏛 Бухара",
        "name_en": "🏛 Bukhara",
        "name_uz": "🏛 Buxoro",
    },
    {
        "id": "navoi",
        "name_ru": "🌿 Навои",
        "name_en": "🌿 Navoi",
        "name_uz": "🌿 Navoiy",
    },
    {
        "id": "andijan",
        "name_ru": "🌄 Андижан",
        "name_en": "🌄 Andijan",
        "name_uz": "🌄 Andijon",
    },
]


def city_name(city: dict, lang: str) -> str:
    return city.get(f"name_{lang}", city["name_ru"])


CARS: list[dict] = [
    {
        "id": "camry", "name": "Toyota Camry", "emoji": "🚗",
        "description": "Комфортный бизнес-седан для любых поездок",
        "description_en": "Comfortable business sedan for any trip",
        "description_uz": "Har qanday sayohat uchun qulay biznes-sedan",
        "specs": (
            "⚙️ *Двигатель:* 2.5L, 202 л.с.\n"
            "⛽ *Топливо:* Бензин\n🔄 *КПП:* Автомат\n"
            "👥 *Мест:* 5\n❄️ *Климат-контроль:* Есть\n"
            "🔊 *Мультимедиа:* Android Auto / CarPlay"
        ),
        "specs_en": (
            "⚙️ *Engine:* 2.5L, 202 hp\n"
            "⛽ *Fuel:* Gasoline\n🔄 *Transmission:* Automatic\n"
            "👥 *Seats:* 5\n❄️ *Climate control:* Yes\n"
            "🔊 *Multimedia:* Android Auto / CarPlay"
        ),
        "specs_uz": (
            "⚙️ *Dvigatel:* 2.5L, 202 ot kuchi\n"
            "⛽ *Yoqilg'i:* Benzin\n🔄 *KPP:* Avtomat\n"
            "👥 *O'rindiqlar:* 5\n❄️ *Iqlim nazorati:* Bor\n"
            "🔊 *Multimedia:* Android Auto / CarPlay"
        ),
        "price_per_hour": 500_000,
        "image": "https://images.hgmsites.net/med/2023-toyota-camry-se-auto-natl-angular-front-exterior-view_100857360_m.jpg",
    },
    {
        "id": "bmw5", "name": "BMW M5 F90", "emoji": "🏎",
        "description": "Премиум бизнес-класс с динамичным характером",
        "description_en": "Premium business class with dynamic character",
        "description_uz": "Dinamik xarakterli premium biznes-klass",
        "specs": (
            "⚙️ *Двигатель:* 4.4L Twin-Power Turbo, 625 л.с.\n"
            "⛽ *Топливо:* Бензин\n🔄 *КПП:* Автомат 8-ст.\n"
            "👥 *Мест:* 5\n🏁 *Разгон 0–100:* 3.3 с\n"
            "🎵 *Аудио:* Apple CarPlay / Android Auto"
        ),
        "specs_en": (
            "⚙️ *Engine:* 4.4L Twin-Power Turbo, 625 hp\n"
            "⛽ *Fuel:* Gasoline\n🔄 *Transmission:* 8-speed Auto\n"
            "👥 *Seats:* 5\n🏁 *0–100 km/h:* 3.3 s\n"
            "🎵 *Audio:* Apple CarPlay / Android Auto"
        ),
        "specs_uz": (
            "⚙️ *Dvigatel:* 4.4L Twin-Power Turbo, 625 ot kuchi\n"
            "⛽ *Yoqilg'i:* Benzin\n🔄 *KPP:* 8 pog'onali avtomat\n"
            "👥 *O'rindiqlar:* 5\n🏁 *0–100:* 3.3 sek\n"
            "🎵 *Audio:* Apple CarPlay / Android Auto"
        ),
        "price_per_hour": 800_000,
        "image": "https://hips.hearstapps.com/hmg-prod/images/2021-bmw-540i-xdrive-370-edit-1608066218.jpg?crop=0.579xw:0.487xh;0.0785xw,0.472xh&resize=1200:*",
    },
    {
        "id": "mercedes", "name": "Mercedes E-Class", "emoji": "💎",
        "description": "Элегантность, мощь и полный пакет безопасности",
        "description_en": "Elegance, power and full safety package",
        "description_uz": "Nafosati, quvvati va to'liq xavfsizlik paketi",
        "specs": (
            "⚙️ *Двигатель:* 3.0L, 381 л.с.\n"
            "⛽ *Топливо:* Дизель / Бенизин \n🔄 *КПП:* Автомат 9G-Tronic\n"
            "👥 *Мест:* 5\n🛡 *Безопасность:* Pre-Safe, Lane Assist\n"
            "🎵 *Аудио:* Apple CarPlay / Android Auto"
        ),
        "specs_en": (
            "⚙️ *Engine:* 3.0L, 381 hp\n"
            "⛽ *Fuel:* Diesel / Petrol\n🔄 *Transmission:* 9G-Tronic Auto\n"
            "👥 *Seats:* 5\n🛡 *Safety:* Pre-Safe, Lane Assist\n"
            "🎵 *Audio:* Apple CarPlay / Android Auto"
        ),
        "specs_uz": (
            "⚙️ *Dvigatel:* 3.0L, 381 ot kuchi\n"
            "⛽ *Yoqilg'i:* Dizel / Benzin\n🔄 *KPP:* 9G-Tronic avtomat\n"
            "👥 *O'rindiqlar:* 5\n🛡 *Xavfsizlik:* Pre-Safe, Lane Assist\n"
            "🎵 *Audio:* Apple CarPlay / Android Auto"
        ),
        "price_per_hour": 900_000,
        "image": "https://stimg.cardekho.com/images/carexteriorimages/930x620/Mercedes-Benz/E-Class/9790/1763471140336/front-left-side-47.jpg",
    },
    {
        "id": "audi_a6", "name": "Audi A6", "emoji": "⚡",
        "description": "Технологии будущего и цифровой комфорт",
        "description_en": "Future technologies and digital comfort",
        "description_uz": "Kelajak texnologiyalari va raqamli qulaylik",
        "specs": (
            "⚙️ *Двигатель:* 3.0L TFSI, 350 л.с.\n"
            "⛽ *Топливо:* Бензин\n🔄 *КПП:* S-Tronic 7-ст.\n"
            "👥 *Мест:* 5\n🖥 *Панель:* Полностью цифровая\n"
            "🎵 *Аудио:* Apple CarPlay / Android Auto"
        ),
        "specs_en": (
            "⚙️ *Engine:* 3.0L TFSI, 350 hp\n"
            "⛽ *Fuel:* Gasoline\n🔄 *Transmission:* S-Tronic 7-speed\n"
            "👥 *Seats:* 5\n🖥 *Dashboard:* Fully digital\n"
            "🎵 *Audio:* Apple CarPlay / Android Auto"
        ),
        "specs_uz": (
            "⚙️ *Dvigatel:* 3.0L TFSI, 350 ot kuchi\n"
            "⛽ *Yoqilg'i:* Benzin\n🔄 *KPP:* S-Tronic 7 pog'onali\n"
            "👥 *O'rindiqlar:* 5\n🖥 *Panel:* To'liq raqamli\n"
            "🎵 *Audio:* Apple CarPlay / Android Auto"
        ),
        "price_per_hour": 850_000,
        "image": "https://lh4.googleusercontent.com/proxy/AtZLVmdZt5VB_QmYufFFL5C4DI9XyicjTswDQBfFwHS_gJS-Bs-5MwvxJFcYHYFv_P7EbH8oc1BMqCsED_Y",
    },
    {
        "id": "ferrari", "name": "Ferrari LaFerrari", "emoji": "🔴",
        "description": "Гиперкар — вершина итальянского автопрома",
        "description_en": "Hypercar — the pinnacle of Italian engineering",
        "description_uz": "Giperkar — italyan avtosanoatining cho'qqisi",
        "specs": (
            "⚙️ *Двигатель:* 6.3L V12 + электро, 963 л.с.\n"
            "⛽ *Топливо:* Гибрид\n🔄 *КПП:* Роботизированная\n"
            "👥 *Мест:* 2\n🏁 *Разгон 0–100:* 2.4 с\n"
            "💨 *Макс. скорость:* 350 км/ч"
        ),
        "specs_en": (
            "⚙️ *Engine:* 6.3L V12 + electric, 963 hp\n"
            "⛽ *Fuel:* Hybrid\n🔄 *Transmission:* Robotized\n"
            "👥 *Seats:* 2\n🏁 *0–100 km/h:* 2.4 s\n"
            "💨 *Top speed:* 350 km/h"
        ),
        "specs_uz": (
            "⚙️ *Dvigatel:* 6.3L V12 + elektr, 963 ot kuchi\n"
            "⛽ *Yoqilg'i:* Gibrid\n🔄 *KPP:* Robotlashtirilgan\n"
            "👥 *O'rindiqlar:* 2\n🏁 *0–100:* 2.4 sek\n"
            "💨 *Maks. tezlik:* 350 km/soat"
        ),
        "price_per_hour": 3_000_000,
        "image": "https://www.williamloughran.co.uk//media/7431/ferrari-laferrari-2311-1.jpg",
    },
    {
        "id": "lamborghini", "name": "Lamborghini Aventador", "emoji": "🟡",
        "description": "Легендарный суперкар из Сант'Агаты",
        "description_en": "Legendary supercar from Sant'Agata",
        "description_uz": "Sant'Agatadan afsonaviy superkar",
        "specs": (
            "⚙️ *Двигатель:* 6.5L V12, 740 л.с.\n"
            "⛽ *Топливо:* Бензин\n🔄 *КПП:* Роботизированная ISR\n"
            "👥 *Мест:* 2\n🏁 *Разгон 0–100:* 2.9 с\n"
            "💨 *Макс. скорость:* 350 км/ч"
        ),
        "specs_en": (
            "⚙️ *Engine:* 6.5L V12, 740 hp\n"
            "⛽ *Fuel:* Gasoline\n🔄 *Transmission:* ISR robotized\n"
            "👥 *Seats:* 2\n🏁 *0–100 km/h:* 2.9 s\n"
            "💨 *Top speed:* 350 km/h"
        ),
        "specs_uz": (
            "⚙️ *Dvigatel:* 6.5L V12, 740 ot kuchi\n"
            "⛽ *Yoqilg'i:* Benzin\n🔄 *KPP:* ISR robotlashtirilgan\n"
            "👥 *O'rindiqlar:* 2\n🏁 *0–100:* 2.9 sek\n"
            "💨 *Maks. tezlik:* 350 km/soat"
        ),
        "price_per_hour": 2_500_000,
        "image": "https://res.cloudinary.com/unix-center/image/upload/c_limit,dpr_3.0,f_auto,fl_progressive,g_center,h_580,q_75,w_906/o28udbvaff0u8xswtull.jpg",
    },
    {
        "id": "cadillac", "name": "Cadillac Escalade", "emoji": "🖤",
        "description": "Американский премиум-внедорожник",
        "description_en": "American premium SUV",
        "description_uz": "Amerika premium yuk avtomobili",
        "specs": (
            "⚙️ *Двигатель:* 6.2L V8, 420 л.с.\n"
            "⛽ *Топливо:* Бензин\n🔄 *КПП:* Автомат 10-ст.\n"
            "👥 *Мест:* 7\n🛢 *Привод:* Полный (4WD)\n"
            "🎵 *Аудио:* Apple CarPlay / Android Auto"
        ),
        "specs_en": (
            "⚙️ *Engine:* 6.2L V8, 420 hp\n"
            "⛽ *Fuel:* Gasoline\n🔄 *Transmission:* 10-speed Auto\n"
            "👥 *Seats:* 7\n🛢 *Drive:* Full (4WD)\n"
            "🎵 *Audio:* Apple CarPlay / Android Auto"
        ),
        "specs_uz": (
            "⚙️ *Dvigatel:* 6.2L V8, 420 ot kuchi\n"
            "⛽ *Yoqilg'i:* Benzin\n🔄 *KPP:* 10 pog'onali avtomat\n"
            "👥 *O'rindiqlar:* 7\n🛢 *Yuritma:* To'liq (4WD)\n"
            "🎵 *Audio:* Apple CarPlay / Android Auto"
        ),
        "price_per_hour": 1_200_000,
        "image": "https://rightrent24.ru/upload/iblock/d3c/aabx288kgep4x5fz0w96v07u4jdwdtgo/cadillac-escalade-iv-platinum-black.jpg",
    },
    {
        "id": "lacetti", "name": "Chevrolet Lacetti", "emoji": "🚙",
        "description": "Надёжный городской седан",
        "description_en": "Reliable city sedan",
        "description_uz": "Ishonchli shahar sedani",
        "specs": (
            "⚙️ *Двигатель:* 1.6L, 109 л.с.\n"
            "⛽ *Топливо:* Бензин\n🔄 *КПП:* Механика / Автомат\n"
            "👥 *Мест:* 5\n🛡 *АБС:* Есть\n"
            "❄️ *Кондиционер:* Есть"
        ),
        "specs_en": (
            "⚙️ *Engine:* 1.6L, 109 hp\n"
            "⛽ *Fuel:* Gasoline\n🔄 *Transmission:* Manual / Auto\n"
            "👥 *Seats:* 5\n🛡 *ABS:* Yes\n"
            "❄️ *Air conditioning:* Yes"
        ),
        "specs_uz": (
            "⚙️ *Dvigatel:* 1.6L, 109 ot kuchi\n"
            "⛽ *Yoqilg'i:* Benzin\n🔄 *KPP:* Mexanik / Avtomat\n"
            "👥 *O'rindiqlar:* 5\n🛡 *ABS:* Bor\n"
            "❄️ *Konditsioner:* Bor"
        ),
        "price_per_hour": 150_000,
        "image": "https://frankfurt.apollo.olxcdn.com/v1/files/h8ysuw4tcvpq1-UZ/image",
    },
    {
        "id": "malibu", "name": "Chevrolet Malibu Premier", "emoji": "🚘",
        "description": "Стильный и современный бизнес-седан",
        "description_en": "Stylish and modern business sedan",
        "description_uz": "Zamonaviy va chiroyli biznes-sedan",
        "specs": (
            "⚙️ *Двигатель:* 2.0L Turbo, 250 л.с.\n"
            "⛽ *Топливо:* Бензин\n🔄 *КПП:* Автомат\n"
            "👥 *Мест:* 5\n❄️ *Климат-контроль:* 2-зонный\n"
            "🔊 *Мультимедиа:* Apple CarPlay / Android Auto"
        ),
        "specs_en": (
            "⚙️ *Engine:* 2.0L Turbo, 250 hp\n"
            "⛽ *Fuel:* Gasoline\n🔄 *Transmission:* Automatic\n"
            "👥 *Seats:* 5\n❄️ *Climate control:* Dual-zone\n"
            "🔊 *Multimedia:* Bose Premium"
        ),
        "specs_uz": (
            "⚙️ *Dvigatel:* 2.0L Turbo, 250 ot kuchi\n"
            "⛽ *Yoqilg'i:* Benzin\n🔄 *KPP:* Avtomat\n"
            "👥 *O'rindiqlar:* 5\n❄️ *Iqlim nazorati:* 2 zonali\n"
            "🔊 *Multimedia:* Apple CarPlay / Android Auto"
        ),
        "price_per_hour": 400_000,
        "image": "https://frankfurt.apollo.olxcdn.com/v1/files/l24zxkiv5i3y2-UZ/image;s=1011x768",
    },
    {
        "id": "byd_han", "name": "BYD Han", "emoji": "🔋",
        "description": "Флагманский электрический седан из Китая",
        "description_en": "Flagship electric sedan from China",
        "description_uz": "Xitoyning flagman elektr sedani",
        "specs": (
            "⚡ *Мотор:* Двойной электро, 517 л.с.\n"
            "🔋 *Батарея:* 85.4 кВт·ч\n🔄 *КПП:* Одноступенчатый редуктор\n"
            "👥 *Мест:* 5\n🏁 *Разгон 0–100:* 3.9 с\n"
            "🛣 *Запас хода:* 500 км"
        ),
        "specs_en": (
            "⚡ *Motor:* Dual electric, 517 hp\n"
            "🔋 *Battery:* 85.4 kWh\n🔄 *Transmission:* Single-speed\n"
            "👥 *Seats:* 5\n🏁 *0–100 km/h:* 3.9 s\n"
            "🛣 *Range:* 500 km"
        ),
        "specs_uz": (
            "⚡ *Motor:* Ikki elektr, 517 ot kuchi\n"
            "🔋 *Batareya:* 85.4 kVt·soat\n🔄 *KPP:* Bir pog'onali reduktor\n"
            "👥 *O'rindiqlar:* 5\n🏁 *0–100:* 3.9 sek\n"
            "🛣 *Qo'yim masofasi:* 500 km"
        ),
        "price_per_hour": 600_000,
        "image": "https://frankfurt.apollo.olxcdn.com/v1/files/4hxcu738yq0v2-UZ/image",
    },
    {
        "id": "voyah", "name": "Voyah Free", "emoji": "🌐",
        "description": "Премиум электро-кроссовер нового поколения",
        "description_en": "Next-generation premium electric crossover",
        "description_uz": "Yangi avlod premium elektr krossoveri",
        "specs": (
            "⚡ *Мотор:* Двойной электро, 489 л.с.\n"
            "🔋 *Батарея:* 106 кВт·ч\n🔄 *КПП:* Одноступенчатый редуктор\n"
            "👥 *Мест:* 5\n🛢 *Привод:* Полный\n"
            "🛣 *Запас хода:* 500 км"
        ),
        "specs_en": (
            "⚡ *Motor:* Dual electric, 489 hp\n"
            "🔋 *Battery:* 106 kWh\n🔄 *Transmission:* Single-speed\n"
            "👥 *Seats:* 5\n🛢 *Drive:* All-wheel\n"
            "🛣 *Range:* 500 km"
        ),
        "specs_uz": (
            "⚡ *Motor:* Ikki elektr, 489 ot kuchi\n"
            "🔋 *Batareya:* 106 kVt·soat\n🔄 *KPP:* Bir pog'onali reduktor\n"
            "👥 *O'rindiqlar:* 5\n🛢 *Yuritma:* To'liq\n"
            "🛣 *Qo'yim masofasi:* 500 km"
        ),
        "price_per_hour": 700_000,
        "image": "https://avcdn.av.by/wisiwigimage/0007/6081/5228.jpg",
    },
    {
        "id": "cobalt", "name": "Chevrolet Cobalt", "emoji": "🚗",
        "description": "Экономичный и практичный седан",
        "description_en": "Economical and practical sedan",
        "description_uz": "Tejamkor va amaliy sedan",
        "specs": (
            "⚙️ *Двигатель:* 1.5L, 106 л.с.\n"
            "⛽ *Топливо:* Бензин\n🔄 *КПП:* Механика / Автомат\n"
            "👥 *Мест:* 5\n⛽ *Расход:* 7.5 л/100 км\n"
            "❄️ *Кондиционер:* Есть"
        ),
        "specs_en": (
            "⚙️ *Engine:* 1.5L, 106 hp\n"
            "⛽ *Fuel:* Gasoline\n🔄 *Transmission:* Manual / Auto\n"
            "👥 *Seats:* 5\n⛽ *Consumption:* 7.5 L/100 km\n"
            "❄️ *Air conditioning:* Yes"
        ),
        "specs_uz": (
            "⚙️ *Dvigatel:* 1.5L, 106 ot kuchi\n"
            "⛽ *Yoqilg'i:* Benzin\n🔄 *KPP:* Mexanik / Avtomat\n"
            "👥 *O'rindiqlar:* 5\n⛽ *Iste'mol:* 7.5 L/100 km\n"
            "❄️ *Konditsioner:* Bor"
        ),
        "price_per_hour": 120_000,
        "image": "https://stat.uz/img/kobalt.jpg",
    },
]

TIME_OPTIONS: list[dict] = [
    {"id": "1h", "label_ru": "⏱ 1 час", "label_en": "⏱ 1 hour", "label_uz": "⏱ 1 soat", "hours": 1, "coeff": 1.0},
    {"id": "10h", "label_ru": "🕙 10 часов", "label_en": "🕙 10 hours", "label_uz": "🕙 10 soat", "hours": 10,
     "coeff": 9.0},
    {"id": "1d", "label_ru": "📅 1 день", "label_en": "📅 1 day", "label_uz": "📅 1 kun", "hours": 24, "coeff": 20.0},
]


def _fmt(price: int) -> str:
    return f"{price:,}".replace(",", " ")


def get_car_by_id(car_id: str) -> dict | None:
    return next((c for c in CARS if c["id"] == car_id), None)


def get_time_by_id(time_id: str) -> dict | None:
    return next((t for t in TIME_OPTIONS if t["id"] == time_id), None)


def get_city_by_id(city_id: str) -> dict | None:
    return next((c for c in CITIES if c["id"] == city_id), None)


def time_label(opt: dict, lang: str) -> str:
    return opt.get(f"label_{lang}", opt["label_ru"])


def get_lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇺🇸 English", callback_data="lang:en")],
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz")],
    ])


def get_city_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=city_name(c, lang),
            callback_data=f"city:{c['id']}",
        )]
        for c in CITIES
    ])


def get_cars_keyboard() -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(CARS), 2):
        row = []
        for car in CARS[i:i + 2]:
            row.append(InlineKeyboardButton(
                text=f"{car['emoji']} {car['name']}",
                callback_data=f"carview:{car['id']}",
            ))
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_car_detail_keyboard(car_id: str, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "select_car_btn"), callback_data=f"car:{car_id}")],
        [InlineKeyboardButton(text=t(lang, "back_to_cars_btn"), callback_data="cars:back")],
    ])


def get_time_keyboard(price_per_hour: int, lang: str) -> InlineKeyboardMarkup:
    rows = []
    for opt in TIME_OPTIONS:
        total = int(price_per_hour * opt["coeff"])
        lbl = time_label(opt, lang)
        rows.append([InlineKeyboardButton(
            text=f"{lbl}  —  {_fmt(total)} {t(lang, 'sum')}",
            callback_data=f"time:{opt['id']}",
        )])
    rows.append([InlineKeyboardButton(
        text=t(lang, "back_to_time_btn"),
        callback_data="time:back",
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


_MONTHS_RU = ["", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
              "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
_MONTHS_EN = ["", "January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
_MONTHS_UZ = ["", "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
              "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"]
_WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def get_calendar_keyboard(year: int, month: int, lang: str = "ru") -> InlineKeyboardMarkup:
    today = date.today()
    cal = calendar.monthcalendar(year, month)
    months = {"ru": _MONTHS_RU, "en": _MONTHS_EN, "uz": _MONTHS_UZ}.get(lang, _MONTHS_RU)
    rows: list[list[InlineKeyboardButton]] = []

    rows.append([
        InlineKeyboardButton(text="◀️", callback_data=f"cal:prev:{year}:{month}"),
        InlineKeyboardButton(text=f"  {months[month]} {year}  ", callback_data="cal:ignore"),
        InlineKeyboardButton(text="▶️", callback_data=f"cal:next:{year}:{month}"),
    ])
    rows.append([
        InlineKeyboardButton(text=d, callback_data="cal:ignore") for d in _WEEKDAYS
    ])
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="cal:ignore"))
                continue
            d = date(year, month, day)
            if d < today:
                row.append(InlineKeyboardButton(text=f"·{day}·", callback_data="cal:ignore"))
            elif d == today:
                row.append(InlineKeyboardButton(text=f"[{day}]", callback_data=f"cal:day:{year}:{month}:{day}"))
            else:
                row.append(InlineKeyboardButton(text=str(day), callback_data=f"cal:day:{year}:{month}:{day}"))
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_captcha_keyboard(correct: int, options: list[int]) -> InlineKeyboardMarkup:
    import random
    shuffled = options[:]
    random.shuffle(shuffled)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=str(opt),
            callback_data=f"captcha:{'ok' if opt == correct else 'fail'}:{opt}",
        ) for opt in shuffled]
    ])


def get_phone_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "send_phone_btn"), request_contact=True)],
            [KeyboardButton(text=t(lang, "cancel_btn"))],
        ],
        resize_keyboard=True, one_time_keyboard=True,
    )


def get_cancel_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "cancel_btn"))]],
        resize_keyboard=True,
    )


def get_skip_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "skip_btn"))],
            [KeyboardButton(text=t(lang, "cancel_btn"))],
        ],
        resize_keyboard=True, one_time_keyboard=True,
    )
