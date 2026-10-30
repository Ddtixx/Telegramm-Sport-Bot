import math
import telebot
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from config import (
    BOT_TOKEN, ACTIVITY_MULTIPLIERS, HARRIS_BENEDICT_COEFFS,
    MIFFLIN_JEOR_COEFFS, GOAL_ADJUSTMENTS,
    PROTEIN_KCAL, FAT_KCAL, CARB_KCAL, CATEGORY_KEYWORDS,
)
from messages import *
from start_and_calc_keyboards import (
    markup_menu, go_menu_markup, back_markup, spisok_benedict_markup,
    go_menu_maffin_markup, back_markup_maffin, spisok_maffin_markup,
    back_go_vvod_markup, spisok_vvod_markup, vvod_spisok_markup, back_vvod_markup,
)
from spiski import (
    spisok_benedict_keyboard, reroll_spisok_benedict_keyboard,
    spisok_maffin_keyboard, reroll_spisok_maffin_keyboard,
    spisok_vvod_keyboard, reroll_spisok_vvod_keyboard,
)
from db import get_random_product_by_category

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, GREETING, reply_markup=markup_menu)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, GREETING, reply_markup=markup_menu)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'info':
        markup1 = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton('Расчёт ккал📝', callback_data='raschet')
        btn2 = InlineKeyboardButton('Ккал известен✉️', callback_data='vvod')
        btn3 = InlineKeyboardButton('О нас', callback_data='about')
        btn4 = InlineKeyboardButton('Ссылки', callback_data='ssilki')
        markup1.add(btn3, btn4)
        markup1.row(btn1, btn2)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Что вас интересует?', reply_markup=markup1)

    elif call.data == 'about':
        bot.send_message(call.message.chat.id, 'Мы команда разработчиков из врж🏆')

    elif call.data == 'ssilki':
        bot.send_message(call.message.chat.id, 'Наш паблик💦:')

    elif call.data in ('back', 'back1', 'back2', 'back3'):
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                         text=GREETING, reply_markup=markup_menu)

    elif call.data == 'go1':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=DATA_SAVED, reply_markup=go_menu_markup)

    elif call.data == 'go2':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=DATA_SAVED, reply_markup=go_menu_maffin_markup)

    elif call.data == 'go3':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=DATA_SAVED, reply_markup=back_go_vvod_markup)

    # --- Харрис-Бенедикт ---
    elif call.data == 'spisok':
        spisok_init = bot.send_message(call.message.chat.id, BUDGET_PROMPT)
        bot.register_next_step_handler(spisok_init, spisok_benedict_run)

    elif call.data == 'spravka':
        back_spravka_markup = InlineKeyboardMarkup()
        back_spravka_markup.add(InlineKeyboardButton('Назад в меню списков⬅️', callback_data='back_spravka'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=SPRAVKA_TEXT, reply_markup=back_spravka_markup)

    elif call.data == 'back_menu':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                         text=GREETING, reply_markup=markup_menu)

    elif call.data == 'back_spravka':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                         text=DATA_SAVED, reply_markup=go_menu_markup)

    elif call.data == 'finish_benedict_data':
        finish_data_back = InlineKeyboardMarkup()
        finish_data_back.add(InlineKeyboardButton('Назад в меню списков ⬅️', callback_data='finish_back'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=DATA_DISPLAY.format(
                                  kcal=float(math.trunc(res_end)),
                                  protein=float(math.trunc(belok)),
                                  fat=float(math.trunc(jir)),
                                  carbs=float(math.trunc(ugli))),
                              reply_markup=finish_data_back)

    elif call.data == 'finish_back':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=DATA_SAVED, reply_markup=spisok_benedict_markup)

    elif call.data == 'finish_benedict_spisok':
        selected_items = {"osnova_benedict": None, "garnir_benedict": None, "napitok_benedict": None}
        bot.send_message(call.message.chat.id, SELECT_POSITIONS, reply_markup=spisok_benedict_keyboard)

    elif call.data in ('osnova_benedict', 'garnir_benedict', 'napitok_benedict'):
        if call.data == 'osnova_benedict':
            selected_items['osnova_benedict'] = get_random_product_by_category(CATEGORY_KEYWORDS["osnova"])
        elif call.data == 'garnir_benedict':
            selected_items['garnir_benedict'] = get_random_product_by_category(CATEGORY_KEYWORDS["garnir"])
        elif call.data == 'napitok_benedict':
            selected_items['napitok_benedict'] = get_random_product_by_category(CATEGORY_KEYWORDS["napitok"])

        message_text = YOU_SELECTED
        for key, value in selected_items.items():
            if value:
                message_text += f"- {value['name']} ({value.get('calories_per_100g', 0):.0f} ккал)\n"
        message_text += f"\n({len([v for v in selected_items.values() if v])}/3)"

        if all(selected_items.values()):
            message_text += ALL_SELECTED
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=message_text, reply_markup=reroll_spisok_benedict_keyboard)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=message_text, reply_markup=spisok_benedict_keyboard)

    elif call.data == 'back_spisko_ben':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=GREETING, reply_markup=markup_menu)

    elif call.data == 'reroll_spisok_ben':
        selected_items = {"osnova_benedict": None, "garnir_benedict": None, "napitok_benedict": None}
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=SELECT_AGAIN, reply_markup=spisok_benedict_keyboard)

    # --- МафФин ---
    elif call.data == 'spisok_maffin':
        spisok_init_maffin = bot.send_message(call.message.chat.id, BUDGET_PROMPT)
        bot.register_next_step_handler(spisok_init_maffin, spisok_maffin_run)

    elif call.data == 'spravka_maffin':
        back_spravka_maffin_markup = InlineKeyboardMarkup()
        back_spravka_maffin_markup.add(InlineKeyboardButton('Назад в меню списков⬅️', callback_data='back_maffin_spravka'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=SPRAVKA_TEXT, reply_markup=back_spravka_maffin_markup)

    elif call.data == 'back_menu_maffin':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                         text=GREETING, reply_markup=markup_menu)

    elif call.data == 'back_maffin_spravka':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=DATA_SAVED, reply_markup=go_menu_maffin_markup)

    elif call.data == 'finish_maffin_data':
        finish_data_back_maffin = InlineKeyboardMarkup()
        finish_data_back_maffin.add(InlineKeyboardButton('Назад в меню списков ⬅️', callback_data='maffin_finish_back'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=DATA_DISPLAY.format(
                                  kcal=float(math.trunc(res_end2)),
                                  protein=float(math.trunc(belok2)),
                                  fat=float(math.trunc(jir2)),
                                  carbs=float(math.trunc(ugli2))),
                              reply_markup=finish_data_back_maffin)

    elif call.data == 'maffin_finish_back':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=DATA_SAVED, reply_markup=spisok_maffin_markup)

    elif call.data == 'finish_maffin_spisok':
        selected_items_maf = {"osnova_maffin": None, "garnir_maffin": None, "napitok_maffin": None}
        bot.send_message(call.message.chat.id, SELECT_POSITIONS, reply_markup=spisok_maffin_keyboard)

    elif call.data in ('osnova_maffin', 'garnir_maffin', 'napitok_maffin'):
        if call.data == 'osnova_maffin':
            selected_items_maf['osnova_maffin'] = get_random_product_by_category(CATEGORY_KEYWORDS["osnova"])
        elif call.data == 'garnir_maffin':
            selected_items_maf['garnir_maffin'] = get_random_product_by_category(CATEGORY_KEYWORDS["garnir"])
        elif call.data == 'napitok_maffin':
            selected_items_maf['napitok_maffin'] = get_random_product_by_category(CATEGORY_KEYWORDS["napitok"])

        message_text = YOU_SELECTED
        for key, value in selected_items_maf.items():
            if value:
                message_text += f"- {value['name']} ({value.get('calories_per_100g', 0):.0f} ккал)\n"
        message_text += f"\n({len([v for v in selected_items_maf.values() if v])}/3)"

        if all(selected_items_maf.values()):
            message_text += ALL_SELECTED
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=message_text, reply_markup=reroll_spisok_maffin_keyboard)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=message_text, reply_markup=spisok_maffin_keyboard)

    elif call.data == 'back_spisko_maf':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=GREETING, reply_markup=markup_menu)

    elif call.data == 'reroll_spisok_maf':
        selected_items_maf = {"osnova_maffin": None, "garnir_maffin": None, "napitok_maffin": None}
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=SELECT_AGAIN, reply_markup=spisok_maffin_keyboard)

    # --- Ручной ввод ---
    elif call.data == 'spisok_vvoda':
        spisok_init_vvoda = bot.send_message(call.message.chat.id, BUDGET_PROMPT)
        bot.register_next_step_handler(spisok_init_vvoda, spisok_vvod_run)

    elif call.data == 'spravka_vvod':
        back_spravka_vvod_markup = InlineKeyboardMarkup()
        back_spravka_vvod_markup.add(InlineKeyboardButton('Назад в меню списков⬅️', callback_data='back_spravka_vvod'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=SPRAVKA_TEXT, reply_markup=back_spravka_vvod_markup)

    elif call.data == 'back_menu_vvod':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                             text=GREETING, reply_markup=markup_menu)

    elif call.data == 'back_spravka_vvod':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=DATA_SAVED, reply_markup=back_go_vvod_markup)

    elif call.data == 'finish_vvod_data':
        finish_data_back_vvod = InlineKeyboardMarkup()
        finish_data_back_vvod.add(InlineKeyboardButton('Назад в меню списков ⬅️', callback_data='vvod_finish_back'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=DATA_DISPLAY.format(
                                  kcal=float(math.trunc(vvod_res)),
                                  protein=float(math.trunc(vvod_belok)),
                                  fat=float(math.trunc(vvod_jir)),
                                  carbs=float(math.trunc(vvod_ugli))),
                              reply_markup=finish_data_back_vvod)

    elif call.data == 'vvod_finish_back':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=DATA_SAVED, reply_markup=vvod_spisok_markup)

    elif call.data == 'finish_vvod_spisok':
        selected_items_vvod = {"osnova_vvod": None, "garnir_vvod": None, "napitok_vvod": None}
        bot.send_message(call.message.chat.id, SELECT_POSITIONS, reply_markup=spisok_vvod_keyboard)

    elif call.data in ('osnova_vvod', 'garnir_vvod', 'napitok_vvod'):
        if call.data == 'osnova_vvod':
            selected_items_vvod['osnova_vvod'] = get_random_product_by_category(CATEGORY_KEYWORDS["osnova"])
        elif call.data == 'garnir_vvod':
            selected_items_vvod['garnir_vvod'] = get_random_product_by_category(CATEGORY_KEYWORDS["garnir"])
        elif call.data == 'napitok_vvod':
            selected_items_vvod['napitok_vvod'] = get_random_product_by_category(CATEGORY_KEYWORDS["napitok"])

        message_text = YOU_SELECTED
        for key, value in selected_items_vvod.items():
            if value:
                message_text += f"- {value['name']} ({value.get('calories_per_100g', 0):.0f} ккал)\n"
        message_text += f"\n({len([v for v in selected_items_vvod.values() if v])}/3)"

        if all(selected_items_vvod.values()):
            message_text += ALL_SELECTED
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=message_text, reply_markup=reroll_spisok_vvod_keyboard)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=message_text, reply_markup=spisok_vvod_keyboard)

    elif call.data == 'back_spisko_vvod':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=GREETING, reply_markup=markup_menu)

    elif call.data == 'reroll_spisok_vvod':
        selected_items_vvod = {"osnova_vvod": None, "garnir_vvod": None, "napitok_vvod": None}
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=SELECT_AGAIN, reply_markup=spisok_vvod_keyboard)


# --- Инициализация методов расчёта ---

def harris_benedict_init(message):
    if message.text == 'Продолжить':
        init = bot.send_message(message.chat.id, HARRIS_INTRO)
        bot.register_next_step_handler(init, start_benedict)
    elif message.text == 'Назад в меню':
        bot.send_message(message.chat.id, GREETING, reply_markup=markup_menu)


def mifflin_jeor_init(message):
    if message.text == 'Продолжить':
        init = bot.send_message(message.chat.id, MIFFLIN_INTRO)
        bot.register_next_step_handler(init, start_maffin)
    elif message.text == 'Назад в меню':
        bot.send_message(message.chat.id, GREETING, reply_markup=markup_menu)


# --- Калькуляторы ---

@bot.message_handler(content_types=['text'])
def start_benedict(message):
    weight1 = bot.send_message(message.chat.id, WEIGHT_PROMPT)
    bot.register_next_step_handler(weight1, weight_benedict)


def weight_benedict(message):
    global w1
    try:
        w1 = float(message.text)
    except ValueError:
        bot.send_message(message.chat.id, INVALID_NUMBER)
    height1 = bot.send_message(message.chat.id, HEIGHT_PROMPT)
    bot.register_next_step_handler(height1, height_benedict)


def height_benedict(message):
    global h1
    h1 = message.text
    age1 = bot.send_message(message.chat.id, AGE_PROMPT)
    bot.register_next_step_handler(age1, age_benedict)


def age_benedict(message):
    global a1
    a1 = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for label in ACTIVITY_MULTIPLIERS:
        markup.add(types.KeyboardButton(label))
    actmarkup = bot.send_message(message.chat.id, ACTIVITY_PROMPT, reply_markup=markup)
    bot.register_next_step_handler(actmarkup, activity_benedict)


def activity_benedict(message):
    global act1
    act1 = ACTIVITY_MULTIPLIERS.get(message.text, 1.2)
    sex = types.ReplyKeyboardMarkup(resize_keyboard=True)
    sex.row(types.KeyboardButton('Мужчина'), types.KeyboardButton('Женщина'))
    result1 = bot.send_message(message.chat.id, SEX_PROMPT, reply_markup=sex)
    bot.register_next_step_handler(result1, result_benedict)


def result_benedict(message):
    global res1
    coeffs = HARRIS_BENEDICT_COEFFS["male" if message.text == 'Мужчина' else "female"]
    c = coeffs
    res1 = (c["base"] + (c["weight"] * float(w1)) + (c["height"] * float(h1)) - (c["age"] * float(a1))) * float(act1)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Сушка'), KeyboardButton('Поддeржание веса'), KeyboardButton('Набор массы'))
    status = bot.send_message(message.chat.id, GOAL_PROMPT, reply_markup=markup)
    bot.register_next_step_handler(status, status_benedict)


def status_benedict(message):
    global res_end, belok, jir, ugli
    goal = GOAL_ADJUSTMENTS.get(message.text, GOAL_ADJUSTMENTS["Поддeржание веса"])
    res_end = float(res1) + (float(res1) * goal["calorie_delta"])
    belok = (res_end * goal["protein_ratio"]) / PROTEIN_KCAL
    jir = (res_end * goal["fat_ratio"]) / FAT_KCAL
    ugli = (res_end * goal["carb_ratio"]) / CARB_KCAL
    bot.send_message(message.chat.id,
                     HARRIS_RESULT.format(kcal=float(math.trunc(res_end)), protein=float(math.trunc(belok)),
                                          fat=float(math.trunc(jir)), carbs=float(math.trunc(ugli))),
                     reply_markup=back_markup)


# --- МафФин ---

def start_maffin(message):
    weight1 = bot.send_message(message.chat.id, WEIGHT_PROMPT)
    bot.register_next_step_handler(weight1, weight_maffin)


def weight_maffin(message):
    global w2
    w2 = message.text
    height1 = bot.send_message(message.chat.id, HEIGHT_PROMPT)
    bot.register_next_step_handler(height1, height_maffin)


def height_maffin(message):
    global h2
    h2 = message.text
    age1 = bot.send_message(message.chat.id, AGE_PROMPT)
    bot.register_next_step_handler(age1, age_maffin)


def age_maffin(message):
    global a2
    a2 = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for label in ACTIVITY_MULTIPLIERS:
        markup.add(types.KeyboardButton(label))
    actmarkup = bot.send_message(message.chat.id, ACTIVITY_PROMPT, reply_markup=markup)
    bot.register_next_step_handler(actmarkup, activity_maffin)


def activity_maffin(message):
    global act2
    act2 = ACTIVITY_MULTIPLIERS.get(message.text, 1.2)
    sex = types.ReplyKeyboardMarkup(resize_keyboard=True)
    sex.row(types.KeyboardButton('Мужчина'), types.KeyboardButton('Женщина'))
    result1 = bot.send_message(message.chat.id, SEX_PROMPT, reply_markup=sex)
    bot.register_next_step_handler(result1, result_maffin)


def result_maffin(message):
    global res2
    key = "male" if message.text == 'Мужчина' else "female"
    c = MIFFLIN_JEOR_COEFFS[key]
    res2 = ((c["weight"] * float(w2)) + (c["height"] * float(h2)) - (c["age"] * float(a2)) + c["base"]) * float(act2)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Сушка'), KeyboardButton('Поддержание веса'), KeyboardButton('Набор массы'))
    status = bot.send_message(message.chat.id, GOAL_PROMPT, reply_markup=markup)
    bot.register_next_step_handler(status, status_maffin)


def status_maffin(message):
    global res_end2, belok2, jir2, ugli2
    goal = GOAL_ADJUSTMENTS.get(message.text, GOAL_ADJUSTMENTS["Поддержание веса"])
    res_end2 = float(res2) + (float(res2) * goal["calorie_delta"])
    belok2 = (res_end2 * goal["protein_ratio"]) / PROTEIN_KCAL
    jir2 = (res_end2 * goal["fat_ratio"]) / FAT_KCAL
    ugli2 = (res_end2 * goal["carb_ratio"]) / CARB_KCAL
    bot.send_message(message.chat.id,
                     MIFFLIN_RESULT.format(kcal=float(math.trunc(res_end2)), protein=float(math.trunc(belok2)),
                                           fat=float(math.trunc(jir2)), carbs=float(math.trunc(ugli2))),
                     reply_markup=back_markup_maffin)


# --- Ручной ввод ---

@bot.message_handler(content_types=['text'])
def vvod_init(message):
    global vvod_res
    vvod_res = float(message.text)
    v1 = bot.send_message(message.chat.id, PROTEIN_PROMPT, reply_markup=back_vvod_markup)
    bot.register_next_step_handler(v1, vvod_b)


def vvod_b(message):
    global vvod_belok
    vvod_belok = float(message.text)
    v2 = bot.send_message(message.chat.id, FAT_PROMPT, reply_markup=back_vvod_markup)
    bot.register_next_step_handler(v2, vvod_j)


def vvod_j(message):
    global vvod_jir
    vvod_jir = float(message.text)
    v3 = bot.send_message(message.chat.id, CARB_PROMPT, reply_markup=back_vvod_markup)
    bot.register_next_step_handler(v3, vvod_u)


def vvod_u(message):
    global vvod_ugli
    vvod_ugli = float(message.text)
    bot.send_message(message.chat.id,
                     MANUAL_RESULT.format(kcal=float(math.trunc(vvod_res)), protein=float(math.trunc(vvod_belok)),
                                           fat=float(math.trunc(vvod_jir)), carbs=float(math.trunc(vvod_ugli))),
                     reply_markup=back_go_vvod_markup)


# --- Бюджеты ---

@bot.message_handler(content_types=['text'])
def spisok_benedict_run(message):
    global summa
    try:
        summa = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, INVALID_NUMBER_EXCLAMATION)
    bot.send_message(message.chat.id, BUDGET_SAVED, reply_markup=spisok_benedict_markup)


@bot.message_handler(content_types=['text'])
def spisok_maffin_run(message):
    global summa2
    try:
        summa2 = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, INVALID_NUMBER_EXCLAMATION)
    bot.send_message(message.chat.id, BUDGET_SAVED, reply_markup=spisok_maffin_markup)


@bot.message_handler(content_types=['text'])
def spisok_vvod_run(message):
    global summa3
    try:
        summa3 = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, INVALID_NUMBER_EXCLAMATION)
    bot.send_message(message.chat.id, BUDGET_SAVED, reply_markup=vvod_spisok_markup)


bot.infinity_polling()
