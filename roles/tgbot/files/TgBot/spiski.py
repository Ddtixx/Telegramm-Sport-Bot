
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

#Клава с выбором блюда Бенедикт
spisok_benedict_keyboard = InlineKeyboardMarkup()
spisok_benedict_keyboard.add(InlineKeyboardButton(text="Основное блюдо", callback_data="osnova_benedict"))
spisok_benedict_keyboard.add(InlineKeyboardButton(text="Гарнир", callback_data="garnir_benedict"))
spisok_benedict_keyboard.add(InlineKeyboardButton(text="Напиток", callback_data="napitok_benedict"))


#Клава Реролла и возврата в стартовое меню Бенедикт
reroll_spisok_benedict_keyboard = InlineKeyboardMarkup()
reroll_spisok_benedict_keyboard.add(InlineKeyboardButton(text='Реролл', callback_data='reroll_spisok_ben'))
reroll_spisok_benedict_keyboard.add(InlineKeyboardButton(text='Стартовое меню', callback_data='back_spisko_ben'))


#Клава с выбором блюда Маффин
spisok_maffin_keyboard = InlineKeyboardMarkup()
spisok_maffin_keyboard.add(InlineKeyboardButton(text="Основное блюдо", callback_data="osnova_maffin"))
spisok_maffin_keyboard.add(InlineKeyboardButton(text="Гарнир", callback_data="garnir_maffin"))
spisok_maffin_keyboard.add(InlineKeyboardButton(text="Напиток", callback_data="napitok_maffin"))

#Клава Реролла и возврата в стартовое меню Маффин
reroll_spisok_maffin_keyboard = InlineKeyboardMarkup()
reroll_spisok_maffin_keyboard.add(InlineKeyboardButton(text='Реролл', callback_data='reroll_spisok_maf'))
reroll_spisok_maffin_keyboard.add(InlineKeyboardButton(text='Стартовое меню', callback_data='back_spisko_maf'))

#Клава с выбором блюда Ввод
spisok_vvod_keyboard = InlineKeyboardMarkup()
spisok_vvod_keyboard.add(InlineKeyboardButton(text="Основное блюдо", callback_data="osnova_vvod"))
spisok_vvod_keyboard.add(InlineKeyboardButton(text="Гарнир", callback_data="garnir_vvod"))
spisok_vvod_keyboard.add(InlineKeyboardButton(text="Напиток", callback_data="napitok_vvod"))

#Клава Реролла и возврата в стартовое меню Ввод
reroll_spisok_vvod_keyboard = InlineKeyboardMarkup()
reroll_spisok_vvod_keyboard.add(InlineKeyboardButton(text='Реролл', callback_data='reroll_spisok_vvod'))
reroll_spisok_vvod_keyboard.add(InlineKeyboardButton(text='Стартовое меню', callback_data='back_spisko_vvod'))