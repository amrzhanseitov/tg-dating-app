from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_gender_keyboard():
    
    btn_male = KeyboardButton(text="Мужской")
    btn_female = KeyboardButton(text="Женский")


    keyboard = ReplyKeyboardMarkup(
        keyboard=[ 
            [btn_male],
            [btn_female]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_main_menu_keyboard():
    btn_search_profiles = KeyboardButton(text="Моя анкета")
    btn_profile = KeyboardButton(text="Изменить анкету")
    btn_edit = KeyboardButton(text="Искать анкету")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [btn_search_profiles],
            [btn_profile],
            [btn_edit]
        ],
        resize_keyboard=True
    )
    return keyboard