import telebot
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

#стартовое меню
markup_menu = types.InlineKeyboardMarkup()
btn1 = types.InlineKeyboardButton('Рассчет ккал📝', callback_data='raschet')
btn2 = types.InlineKeyboardButton('Ккал известен✏️', callback_data='vvod')
btn3 = types.InlineKeyboardButton('Инфо📌', callback_data='info')
markup_menu.add(btn3)
markup_menu.row(btn1, btn2)

#меню с продуктами для Харриса
go_menu_markup = types.InlineKeyboardMarkup()
go_menu_btn1 = types.InlineKeyboardButton('Составить список продуктов', callback_data='spisok')
go_menu_btn2 = types.InlineKeyboardButton('Справка', callback_data='spravka')
go_menu_btn3 = types.InlineKeyboardButton('Вернуться в стартовое меню', callback_data='back_menu')
go_menu_markup.add(go_menu_btn1, go_menu_btn2, go_menu_btn3)

#меню составления списка продуктов и возврат при Харрисе
back_markup = InlineKeyboardMarkup()
go_btn_benedict = InlineKeyboardButton('Составить список продуктов➡️', callback_data='go1')
backbtn = InlineKeyboardButton('Назад в меню ⬅️', callback_data='back1')
back_markup.add(backbtn, go_btn_benedict)

#Последнее меню Харриса перед списком
spisok_benedict_markup = InlineKeyboardMarkup()
spisok_benedict_btn1 = InlineKeyboardButton('Показать список', callback_data='finish_benedict_spisok')
spisok_benedict_btn2 = InlineKeyboardButton('Показать мои данные', callback_data='finish_benedict_data')
spisok_benedict_markup.add(spisok_benedict_btn1, spisok_benedict_btn2)

#меню с продуктами для Маффина
go_menu_maffin_markup = types.InlineKeyboardMarkup()
go_menu_maffin_btn1 = types.InlineKeyboardButton('Составить список продуктов Маффин', callback_data='spisok_maffin')
go_menu_maffin_btn2 = types.InlineKeyboardButton('Справка', callback_data='spravka_maffin')
go_menu_maffin_btn3 = types.InlineKeyboardButton('Вернуться в стартовое меню', callback_data='back_menu_maffin')
go_menu_maffin_markup.add(go_menu_maffin_btn1, go_menu_maffin_btn2, go_menu_maffin_btn3)

#меню составления списка продуктов и возврат при Маффине
back_markup_maffin = InlineKeyboardMarkup()
go_btn_maffin = InlineKeyboardButton('Составить список продуктов Маффин➡️', callback_data='go2')
backbtn_maffin = InlineKeyboardButton('Назад в меню ⬅️', callback_data='back2')
back_markup_maffin.add(backbtn_maffin, go_btn_maffin)

#Последнее меню Маффина перед списком
spisok_maffin_markup =  InlineKeyboardMarkup()
spisok_maffin_btn1 = InlineKeyboardButton('Показать список', callback_data='finish_maffin_spisok')
spisok_maffin_btn2 = InlineKeyboardButton('Показать мои данные', callback_data='finish_maffin_data')
spisok_maffin_markup.add(spisok_maffin_btn1, spisok_maffin_btn2)

#меню  составления списка продуктов и возврат при вводе КБЖУ
back_go_vvod_markup = InlineKeyboardMarkup()
back_go_vvod_btn1 = InlineKeyboardButton('Составить список продуктов', callback_data='spisok_vvoda')
back_go_vvod_btn2 = InlineKeyboardButton('Справка', callback_data='spravka_vvod')
back_go_vvod_btn3 = InlineKeyboardButton('Вернуться в стартовое меню', callback_data='back_menu_vvod')
back_go_vvod_markup.add(back_go_vvod_btn1, back_go_vvod_btn2, back_go_vvod_btn3)

#меню списка продуктов и возврат при вводе КБЖУ
spisok_vvod_markup = InlineKeyboardMarkup()
go_back_vvod_btn1 = InlineKeyboardButton('Составить список продуктов➡️', callback_data='go3')
go_back_vvod_btn2 = InlineKeyboardButton('Назад в меню ⬅️', callback_data='vvod_back')
spisok_vvod_markup.add(go_back_vvod_btn1, go_back_vvod_btn2)

#Последнее меню ввода перед списком
vvod_spisok_markup =  InlineKeyboardMarkup()
vvod_spisok_btn1 = InlineKeyboardButton('Показать список', callback_data='finish_vvod_spisok')
vvod_spisok_btn2 = InlineKeyboardButton('Показать мои данные', callback_data='finish_vvod_data')
vvod_spisok_markup.add(vvod_spisok_btn1, vvod_spisok_btn2)

#меню возврата для ввода КБЖУ
back_vvod_markup = InlineKeyboardMarkup()
backbtn_vvod = InlineKeyboardButton('Назад в меню ⬅️', callback_data='back3')
back_vvod_markup.add(backbtn_vvod)
