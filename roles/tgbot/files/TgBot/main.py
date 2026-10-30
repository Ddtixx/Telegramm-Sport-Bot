#telebot
import telebot
import os 
from dotenv import load_dotenv
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
#Клавы из start_and_calc_keyboards
from start_and_calc_keyboards import markup_menu, go_menu_markup, back_markup, spisok_benedict_markup, go_menu_maffin_markup, back_markup_maffin, spisok_maffin_markup, back_go_vvod_markup, vvod_spisok_markup, back_vvod_markup
#Клавы из spiski.py
from spiski import spisok_benedict_keyboard, reroll_spisok_benedict_keyboard, spisok_maffin_keyboard, reroll_spisok_maffin_keyboard, spisok_vvod_keyboard, reroll_spisok_vvod_keyboard
#сокращение для float
import math
#БД
from db import get_random_product_by_category
from services import pick_products_for_basket, format_basket

load_dotenv()

API_TOKEN = os.getenv("API")
bot = telebot.TeleBot(token= API_TOKEN, skip_pending= True)

#Список для позиций в Бенедикте
selected_items = {
    "osnova_banedict": None,
    "garnir_benedict": None,
    "napitok_benedict": None,
}
#Список для позиций в Маффине
selected_items_maf = {
     "osnova_maffin": None,
     "garnir_maffin": None,
     "napitok_maffin": None,
}
#Список для позиций в Вводе
selected_items_vvod = {
     "osnova_vvod": None,
     "garnir_vvod": None,
     "napitok_vvod": None,
}
#глобалки
global res_end, belok, ugli, jir
global res_end2, belok2, ugli2, jir2
global vvod_res, vvod_belok, vvod_ugli, vvod_jir
global summa, summa2, summa3

#команда страт
@bot.message_handler(commands = ['start'])
def start (message):
    bot.send_message(message.chat.id,
                     'Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪',
                     reply_markup=markup_menu)

#обработчик запросов inline(для всех этапов)
@bot.callback_query_handler(func=lambda callback: True)
def func (call):
    global selected_items

    if call.data == 'raschet':
        klavakoka = InlineKeyboardMarkup()
        ketchup = InlineKeyboardButton('Метод Бенедикта', callback_data='Pizda')
        mafin = InlineKeyboardButton('Метод Мафина', callback_data='Hui')
        anal = InlineKeyboardButton('Вернуться назад⬅️', callback_data='Anal')
        klavakoka.row(ketchup, mafin)
        klavakoka.add(anal)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Доступные методы', reply_markup=klavakoka)


    elif call.data == 'Pizda':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        pizda1 = types.KeyboardButton('Продолжить')
        pizda2 = types.KeyboardButton('Назад в меню')
        markup.add(pizda1, pizda2)
        pizdec = bot.send_message(call.message.chat.id, 'Выбран метод Бенедикта', reply_markup=markup)
        bot.register_next_step_handler(pizdec, pizda_init)



    elif call.data == 'Hui':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        pizda1 = types.KeyboardButton('Продолжить')
        pizda2 = types.KeyboardButton('Назад в меню')
        markup.add(pizda1, pizda2)
        huec = bot.send_message(call.message.chat.id, 'Выбран метод Маффина Сан-Жеора', reply_markup=markup)
        bot.register_next_step_handler(huec, hui_init)


    elif call.data == 'Anal':

        bot.edit_message_text(chat_id=call.message.chat.id,  message_id=call.message.message_id,
                             text = 'Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪',
                             reply_markup=markup_menu)


    elif call.data == 'vvod':
        markup_back = InlineKeyboardMarkup()
        btn_back = InlineKeyboardButton('Назад в меню⬅️', callback_data= 'back_vvod')
        markup_back.add(btn_back)
        vvod_go = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите ккал', reply_markup=markup_back)
        bot.register_next_step_handler(vvod_go, vvod_init)

    elif call.data == 'back_vvod':
        bot.edit_message_text(chat_id = call.message.chat.id, message_id=call.message.message_id,
                              text='Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪', reply_markup=markup_menu )



    elif call.data == 'info':
        markup1 = types.InlineKeyboardMarkup()
        btn4 = types.InlineKeyboardButton('О нас👥', callback_data = 'about')
        btn5 = types.InlineKeyboardButton('Ссылки❗️', callback_data='ssilki')
        btn6 = types.InlineKeyboardButton('НАЗАД⬅️', callback_data='back')


        markup1.row(btn4, btn5)
        markup1.add(btn6)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Что вас интересует?', reply_markup=markup1)


    elif call.data == 'about':
        bot.send_message(call.message.chat.id, 'Мы команда разработчиков из врж🏆')

    elif call.data == 'ssilki':
        bot.send_message(call.message.chat.id, 'Наш паблик💦:')

#возврат и продолжения, после подсчета кбжу
    elif call.data == 'back':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                         text = 'Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪',
                         reply_markup=markup_menu)

    elif call.data == 'back1':
        bot.send_message(call.message.chat.id,'Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪',
                         reply_markup=markup_menu)

    elif call.data == 'back2':
        bot.send_message(call.message.chat.id, 'Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪',
                         reply_markup=markup_menu)

    elif call.data == 'back3':
        bot.send_message(call.message.chat.id,
                         'Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪',
                         reply_markup=markup_menu)

    elif call.data == 'go1':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Ваши данные сохранены!Теперь, вы можете составить список продуктов.',
                              reply_markup=go_menu_markup)

    elif call.data == 'go2':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Ваши данные сохранены!Теперь, вы можете составить список продуктов.',
                              reply_markup=go_menu_maffin_markup)

    elif call.data == 'go3':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Ваши данные сохранены!Теперь, вы можете составить список продуктов.',
                              reply_markup=back_go_vvod_markup)


#взаимосвязи после подсчета кбжу для Бенедикта
    elif call.data == 'spisok':
        spisok_init = bot.send_message(call.message.chat.id, 'Введите желаемый дневной бюджет на продукты')
        bot.register_next_step_handler(spisok_init, spisok_benedict_run)

    elif call.data == 'spravka':
        back_spravka_markup = InlineKeyboardMarkup()
        back_spravka_btn = InlineKeyboardButton('Назад в меню списков⬅️', callback_data='back_spravka')
        back_spravka_markup.add(back_spravka_btn)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Данное меню поможет составить дневной список продуктов для вашего рациона, нажмите на кнопку "Составить список продукто", затем введите желаемый дневной бюджет, и готово! Получите список продуктов на день, с характеристиками цены, бжу, ккал, и информацией в каком магазине этот продукт можно купить! ',
                              reply_markup=back_spravka_markup)

    elif call.data == 'back_menu':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                         text = 'Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪',
                         reply_markup=markup_menu)

    elif call.data == 'back_spravka':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                         text = 'Ваши данные сохранены!Теперь, вы можете составить список продуктов.',
                         reply_markup=go_menu_markup)

    elif call.data == 'finish_benedict_data':
        finish_data_back = InlineKeyboardMarkup()
        finish_back = InlineKeyboardButton('Назад в меню списков ⬅️', callback_data= 'finish_back')
        finish_data_back.add(finish_back)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'Ваш каллораж: {float(math.trunc(res_end))}  Ккал\nБелки:{float(math.trunc(belok))} г\nЖиры:{float(math.trunc(jir))} г\nУгеводы:{float(math.trunc(ugli))} г',
                                  reply_markup=finish_data_back)

    elif call.data == 'finish_back':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Ваши данные сохранены!Теперь, вы можете составить список продуктов.',
                              reply_markup=spisok_benedict_markup)

#Отображение позиций в списке Бенедикт
    global selected_items

    if call.data == 'finish_benedict_spisok':
        selected_items = {"osnova_benedict": None, "garnir_benedict": None, "napitok_benedict": None}
        bot.send_message(call.message.chat.id, 'Выберите позиции:', reply_markup=spisok_benedict_keyboard)

    elif call.data in ['osnova_benedict', 'garnir_benedict', 'napitok_benedict']:

        if call.data == 'osnova_benedict':
            selected_items['osnova_benedict'] = get_random_product_by_category('индейка')

        elif call.data == 'garnir_benedict':
            selected_items['garnir_benedict'] = get_random_product_by_category('хлеб')

        elif call.data == 'napitok_benedict':
            selected_items['napitok_benedict'] = get_random_product_by_category('молоко')

            # Формируем текст сообщения с выбранными позициями
        message_text = "Вы выбрали:\n"
        for key, value in selected_items.items():
            if value:
                message_text += f"- {value['name']} ({value.get('calories_per_100g', 0):.0f} ккал)\n"

        message_text += f"\n({len([v for v in selected_items.values() if v])}/3)"
     
   # Проверяем, все ли позиции выбраны
        if all(selected_items.values()):  # Если все три позиции выбраны
            message_text += "\nВсе позиции выбраны. Что дальше?"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=message_text, reply_markup=reroll_spisok_benedict_keyboard)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=message_text, reply_markup=spisok_benedict_keyboard)

    elif call.data == 'back_spisko_ben':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪', reply_markup=markup_menu)

    elif call.data == 'reroll_spisok_ben':
        selected_items = {"osnova_benedict": None, "garnir_benedict": None, "napitok_benedict": None}
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите позиции заново:", reply_markup=spisok_benedict_keyboard)



#взаимосвязи после подсчета кбжу для Маффина
    elif call.data == 'spisok_maffin':
        spisok_init_maffin = bot.send_message(call.message.chat.id, 'Введите желаемый дневной бюджет на продукты')
        bot.register_next_step_handler(spisok_init_maffin, spisok_maffin_run)

    elif call.data == 'spravka_maffin':
        back_spravka_maffin_markup = InlineKeyboardMarkup()
        back_spravka_maffin_btn = InlineKeyboardButton('Назад в меню списков⬅️', callback_data='back_maffin_spravka')
        back_spravka_maffin_markup.add(back_spravka_maffin_btn)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Данное меню поможет составить дневной список продуктов для вашего рациона, нажмите на кнопку "Составить список продукто", затем введите желаемый дневной бюджет, и готово! Получите список продуктов на день, с характеристиками цены, бжу, ккал, и информацией в каком магазине этот продукт можно купить! ',
                              reply_markup=back_spravka_maffin_markup)

    elif call.data == 'back_menu_maffin':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                         text = 'Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪',
                         reply_markup=markup_menu)

    elif call.data == 'back_maffin_spravka':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Ваши данные сохранены!Теперь, вы можете составить список продуктов.',
                              reply_markup=go_menu_maffin_markup)

    elif call.data == 'finish_maffin_data':
        finish_data_back_maffin = InlineKeyboardMarkup()
        maffin_finish_back = InlineKeyboardButton('Назад в меню списков ⬅️', callback_data= 'maffin_finish_back')
        finish_data_back_maffin.add(maffin_finish_back)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Ваш каллораж: {float(math.trunc(res_end2))}  Ккал\nБелки:{float(math.trunc(belok2))} г\nЖиры:{float(math.trunc(jir2))} г\nУглеводы{float(math.trunc(ugli2))} г',
                              reply_markup=finish_data_back_maffin)

    elif call.data == 'maffin_finish_back':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Ваши данные сохранены!Теперь, вы можете составить список продуктов.',
                              reply_markup=spisok_maffin_markup)

# Отображение позиций в списке Маффина
    global selected_items_maf
    if call.data == 'finish_maffin_spisok':
        selected_items_maf = {"osnova_maffin": None, "garnir_maffin": None, "napitok_maffin": None}
        bot.send_message(call.message.chat.id, 'Выберите позиции:', reply_markup=spisok_maffin_keyboard)

    elif call.data in ['osnova_maffin', 'garnir_maffin', 'napitok_maffin']:

        if call.data == 'osnova_maffin':
            selected_items_maf['osnova_maffin'] = 'Курица1'

        elif call.data == 'garnir_maffin':
            selected_items_maf['garnir_maffin'] = 'Рис1'

        elif call.data == 'napitok_maffin':
            selected_items_maf['napitok_maffin'] = 'Сок1'

            # Формируем текст сообщения с выбранными позициями
        message_text = "Вы выбрали:\n"
        for key, value in selected_items_maf.items():
            if value:
                message_text += f"- {value}\n"

        # Проверяем, все ли позиции выбраны
        if all(selected_items_maf.values()):  # Если все три позиции выбраны
            message_text += "\nВсе позиции выбраны. Что дальше?"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=message_text, reply_markup=reroll_spisok_maffin_keyboard)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=message_text, reply_markup=spisok_maffin_keyboard)

    elif call.data == 'back_spisko_maf':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪',
                              reply_markup=markup_menu)

    elif call.data == 'reroll_spisok_maf':
        selected_items_maf = {"osnova_maffin": None, "garnir_maffin": None, "napitok_maffin": None}
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите позиции заново:", reply_markup=spisok_maffin_keyboard)


#Взаимосвязи после подсечта кбжу для ручного ввода
    elif call.data == 'spisok_vvoda':
        spisok_init_vvoda = bot.send_message(call.message.chat.id, 'Введите желаемый дневной бюджет на продукты')
        bot.register_next_step_handler(spisok_init_vvoda, spisok_vvod_run)

    elif call.data == 'spravka_vvod':
        back_spravka_vvod_markup = InlineKeyboardMarkup()
        back_spravka_vvod_btn = InlineKeyboardButton('Назад в меню списков⬅️', callback_data='back_spravka_vvod')
        back_spravka_vvod_markup.add(back_spravka_vvod_btn)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Данное меню поможет составить дневной список продуктов для вашего рациона, нажмите на кнопку "Составить список продукто", затем введите желаемый дневной бюджет, и готово! Получите список продуктов на день, с характеристиками цены, бжу, ккал, и информацией в каком магазине этот продукт можно купить! ',
                              reply_markup=back_spravka_vvod_markup)

    elif call.data == 'back_menu_vvod':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                             text='Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪',
                             reply_markup=markup_menu)

    elif call.data == 'back_spravka_vvod':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Ваши данные сохранены!Теперь, вы можете составить список продуктов.',
                              reply_markup=back_go_vvod_markup)

    elif call.data == 'finish_vvod_data':
        finish_data_back_vvod = InlineKeyboardMarkup()
        vvod_finish_back = InlineKeyboardButton('Назад в меню списков ⬅️', callback_data='vvod_finish_back')
        finish_data_back_vvod.add(vvod_finish_back)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'Ваш каллораж: {float(math.trunc(vvod_res))}  Ккал\nБелки:{float(math.trunc(vvod_belok))} г\nЖиры:{float(math.trunc(vvod_jir))} г\nУглеводы:{float(math.trunc(vvod_ugli))} г',
                                  reply_markup=finish_data_back_vvod)

    elif call.data == 'vvod_finish_back':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Ваши данные сохранены!Теперь, вы можете составить список продуктов.',
                              reply_markup=vvod_spisok_markup)

#Отображение позиций в списке для ввода
    global selected_items_vvod
    if call.data == 'finish_vvod_spisok':
        selected_items_vvod = {"osnova_vvod": None, "garnir_vvod": None, "napitok_vvod": None}
        bot.send_message(call.message.chat.id, 'Выберите позиции:', reply_markup=spisok_vvod_keyboard)
    elif call.data in ['osnova_vvod', 'garnir_vvod', 'napitok_vvod']:

        if call.data == 'osnova_vvod':
            selected_items_vvod['osnova_vvod'] = 'Курица2'

        elif call.data == 'garnir_vvod':
            selected_items_vvod['garnir_vvod'] = 'Рис2'

        elif call.data == 'napitok_vvod':
            selected_items_vvod['napitok_vvod'] = 'Сок2'

            # Формируем текст сообщения с выбранными позициями
        message_text = "Вы выбрали:\n"
        for key, value in selected_items_vvod.items():
            if value:
                message_text += f"- {value}\n"

        # Проверяем, все ли позиции выбраны
        if all(selected_items_vvod.values()):  # Если все три позиции выбраны
            message_text += "\nВсе позиции выбраны. Что дальше?"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=message_text, reply_markup=reroll_spisok_vvod_keyboard)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=message_text, reply_markup=spisok_vvod_keyboard)

    elif call.data == 'back_spisko_vvod':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪',
                              reply_markup=markup_menu)

    elif call.data == 'reroll_spisok_vvod':
        selected_items_vvod = {"osnova_vvod": None, "garnir_vvod": None, "napitok_vvod": None}
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите позиции заново:", reply_markup=spisok_vvod_keyboard)

#инициализация для методов подсчета кбжу
def pizda_init(message):
    if message.text == 'Продолжить':
       init = bot.send_message(message.chat.id, 'Выбран рассчет по Методу Харрис-Бенедикта, основанный на расчета базального и активного метобализма')
       bot.register_next_step_handler(init, start_benedict)


    elif message.text == 'Назад в меню':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Рассчет ккал📝', callback_data='raschet')
        btn2 = types.InlineKeyboardButton('Ккал известен✏️', callback_data='vvod')
        btn3 = types.InlineKeyboardButton('Инфо📌', callback_data='info')
        markup.add(btn3)
        markup.row(btn1, btn2)
        bot.send_message(message.chat.id,
                         'Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪',
                         reply_markup=markup)


def hui_init(message):
    if message.text == 'Продолжить':
       init = bot.send_message(message.chat.id, 'Выбран расчет по методу Маффина, который был разработан в 2005 г')
       bot.register_next_step_handler(init, start_maffin)


    elif message.text == 'Назад в меню':

        bot.send_message(message.chat.id,
                         'Привет! Я бот помошник, который предназначен облегчить тебе процесс выбора продуктов для массанабора/сушки💪',
                         reply_markup=markup_menu)



#калькуляторы
@bot.message_handler(content_types=['text'])

#бенедикт
def start_benedict(message):
    weight1 = bot.send_message(message.chat.id, 'Введите свой вес')
    bot.register_next_step_handler(weight1, weight_benedict)

def weight_benedict(message):
    global w1
    try:
        w1 = float(message.text)
    except ValueError:
        bot.send_message(message.chat.id, 'Введите корректное число')


    height1 = bot.send_message(message.chat.id, 'Введите свой рост')
    bot.register_next_step_handler(height1, height_benedict)

def height_benedict(message):
    global h1
    h1 = message.text
    age1 = bot.send_message(message.chat.id, 'Введите свой возраст')
    bot.register_next_step_handler(age1, age_benedict)

def age_benedict(message):
    global a1
    a1 = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btnact1 = types.KeyboardButton('сверх низкий')
    btnact2 = types.KeyboardButton('низкий')
    btnact3 = types.KeyboardButton('средний')
    btnact4 = types.KeyboardButton('высокий')
    btnact5 = types.KeyboardButton('спортивный')
    markup.add(btnact1, btnact2, btnact3, btnact4, btnact5)

    actmarkup = bot.send_message(message.chat.id, 'Выберете уровень активности', reply_markup=markup)
    bot.register_next_step_handler(actmarkup, activity_benedict)

def activity_benedict(message):
    global act1
    act1 = message.text
    if message.text == 'сверх низкий':
        act1 = 1.2
    elif message.text == 'низкий':
        act1 = 1.375
    elif message.text == 'средний':
         act1 = 1.55
    elif message.text == 'высокий':
         act1 = 1.725
    elif message.text == 'спортивный':
         act1 = 1.9

    sex = types.ReplyKeyboardMarkup(resize_keyboard=True)

    sex1 = types.KeyboardButton('Мужчина')

    sex2 = types.KeyboardButton('Женщина')

    sex.row(sex1, sex2)

    result1=bot.send_message(message.chat.id, 'Выберете пол', reply_markup=sex)

    bot.register_next_step_handler(result1, result_benedict)

def result_benedict(message):


    global res1
    if message.text == 'Мужчина':
        res1 = (88.362 + (13.397 * float(w1)) + (4.799 * float(h1)) - (5.677 * float(a1))) * float(act1)

    elif message.text == 'Женщина':
        res1 = (447.593 + (9.247 * float(w1)) + (3.098 * float(h1)) - (4.330 * float(a1))) * float(act1)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton('Сушка')
    btn2 = KeyboardButton('Поддeржание веса')
    btn3 = KeyboardButton('Набор массы')
    markup.add(btn1, btn2, btn3)

    status = bot.send_message(message.chat.id, 'Выберите цель', reply_markup=markup)
    bot.register_next_step_handler(status, status_benedict)

def status_benedict(message):
    global res_end
    global belok
    global ugli
    global jir
    if message.text == 'Сушка':
        res_end = (float(res1) - (float(res1) * 0.2))
        belok = (float(res_end) * 0.35)/4
        jir = (float(res_end) * 0.30)/9
        ugli = (float(res_end) * 0.35)/4
    elif message.text == 'Набор массы':
        res_end = (float(res1) + (float(res1) * 0.2))
        belok = (float(res_end) * 0.25) / 4
        jir = (float(res_end) * 0.30) / 9
        ugli = (float(res_end) * 0.45) / 4
    else:
        res_end = res1
        belok = (float(res_end) * 0.20) / 4
        jir = (float(res_end) * 0.30) / 9
        ugli = (float(res_end) * 0.50) / 4


    bot.send_message(message.chat.id,
                     f'Ваш результат по методу Харриса-Бенедикта: {float(math.trunc(res_end))} Ккал\n\nВаша норма БЖУ: \nБелки: {float(math.trunc(belok))} г\nЖиры: {float(math.trunc(jir))} г\nУглеводы: {float(math.trunc(ugli))}г',
                     reply_markup=back_markup)


#мафин
def start_maffin(message):
    weight1 = bot.send_message(message.chat.id, 'Введите свой вес')
    bot.register_next_step_handler(weight1, weight_maffin)

def weight_maffin(message):
    global w2
    w2 = message.text
    height1 = bot.send_message(message.chat.id, 'Введите свой рост')
    bot.register_next_step_handler(height1, height_maffin)

def height_maffin(message):
    global h2
    h2 = message.text
    age1 = bot.send_message(message.chat.id, 'Введите свой возраст')
    bot.register_next_step_handler(age1, age_maffin)

def age_maffin(message):
    global a2
    a2 = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btnact1 = types.KeyboardButton('сверх низкий')
    btnact2 = types.KeyboardButton('низкий')
    btnact3 = types.KeyboardButton('средний')
    btnact4 = types.KeyboardButton('высокий')
    btnact5 = types.KeyboardButton('спортивный')
    markup.add(btnact1, btnact2, btnact3, btnact4, btnact5)

    actmarkup = bot.send_message(message.chat.id, 'Выберете уровень активности', reply_markup=markup)
    bot.register_next_step_handler(actmarkup, activity_maffin)

def activity_maffin(message):
    global act2
    act2 = message.text
    if message.text == 'сверх низкий':
        act2 = 1.2
    elif message.text == 'низкий':
        act2 = 1.375
    elif message.text == 'средний':
         act2 = 1.55
    elif message.text == 'высокий':
         act2 = 1.725
    elif message.text == 'спортивный':
         act2 = 1.9

    sex = types.ReplyKeyboardMarkup(resize_keyboard=True)

    sex1 = types.KeyboardButton('Мужчина')

    sex2 = types.KeyboardButton('Женщина')

    sex.row(sex1, sex2)

    result1=bot.send_message(message.chat.id, 'Выберете пол', reply_markup=sex)

    bot.register_next_step_handler(result1, result_maffin)

def result_maffin(message):


    global res2
    if message.text == 'Мужчина':
        res2 = ((10 * float(w2)) + (6.25 * float(h2)) - (5 * float(a2) + 5)) * float(act2)

    elif message.text == 'Женщина':
        res2 = ((10 * float(w2)) + (6.25 * float(h2)) - (5 * float(a2) - 161)) * float(act2)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton('Сушка')
    btn2 = KeyboardButton('Поддержание веса')
    btn3 = KeyboardButton('Набор массы')
    markup.add(btn1, btn2, btn3)

    status = bot.send_message(message.chat.id, 'Выберите цель', reply_markup=markup)
    bot.register_next_step_handler(status, status_maffin)

def status_maffin(message):
    global res_end2
    global belok2
    global jir2
    global ugli2
    if message.text == 'Сушка':
        res_end2 = (float(res2) - (float(res2) * 0.2))
        belok2 = (float(res_end2) * 0.35) / 4
        jir2 = (float(res_end2) * 0.30) / 9
        ugli2 = (float(res_end2) * 0.35) / 4
    elif message.text == 'Поддержание веса':
        res_end2 = res2
        belok2 = (float(res_end2) * 0.20) / 4
        jir2 = (float(res_end2) * 0.30) / 9
        ugli2 = (float(res_end2) * 0.50) / 4
    elif message.text == 'Набор массы':
        res_end2 = (float(res2) + (float(res2) * 0.2))
        belok2 = (float(res_end2) * 0.25) / 4
        jir2 = (float(res_end2) * 0.30) / 9
        ugli2 = (float(res_end2) * 0.45) / 4


    bot.send_message(message.chat.id, f'Ваш результат по методу Маффина: {float(math.trunc(res_end2))} Ккал\n\nВаша норма БЖУ: \nБелки: {float(math.trunc(belok2))} г\nЖиры: {float(math.trunc(jir2))} г\nУглеводы: {float(math.trunc(ugli2))}г', reply_markup=back_markup_maffin)

#ввод самостоятельно
@bot.message_handler(content_types=['text'])
def vvod_init(message):
    global vvod_res
    vvod_res = float(message.text)
    v1 = bot.send_message(message.chat.id, 'Введите норму белков', reply_markup=back_vvod_markup)
    bot.register_next_step_handler(v1,vvod_b)
def vvod_b(message):
    global vvod_belok
    vvod_belok = float(message.text)
    v2 = bot.send_message(message.chat.id, 'Введите норму жиров',reply_markup=back_vvod_markup)
    bot.register_next_step_handler(v2, vvod_j)
def vvod_j(message):
    global vvod_jir
    vvod_jir = float(message.text)
    v3 = bot.send_message(message.chat.id, 'Введите норму углеводов',reply_markup=back_vvod_markup)
    bot.register_next_step_handler(v3, vvod_u)
def vvod_u(message):
    global vvod_ugli
    vvod_ugli = float(message.text)
    bot.send_message(message.chat.id, f'Ваш каллораж: {float(math.trunc(vvod_res))} Ккал\n\nВаша норма БЖУ: \nБелки: {float(math.trunc(vvod_belok))} г\nЖиры: {float(math.trunc(vvod_jir))} г\nУглеводы: {float(math.trunc(vvod_ugli))}г', reply_markup=back_go_vvod_markup)


#бюджеты
@bot.message_handler(content_types=['text'])
#бюджет для бенедикта
def spisok_benedict_run(message):
    global summa
    try:
        summa = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, 'Введите корректное число!')
    bot.send_message(message.chat.id, 'Ваш дневной бюджет сохранен!', reply_markup=spisok_benedict_markup)
#бюджет для маффина
def spisok_maffin_run(message):
    global summa2
    try:
        summa2 = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, 'Введите корректное число!')
    bot.send_message(message.chat.id, 'Ваш дневной бюджет сохранен!', reply_markup=spisok_maffin_markup)
#бюджет для ручного ввода
def spisok_vvod_run(message):
    global summa3
    try:
        summa3 = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, 'Введите корректное число!')
    bot.send_message(message.chat.id, 'Ваш дневной бюджет сохранен!', reply_markup=vvod_spisok_markup)


bot.infinity_polling()
