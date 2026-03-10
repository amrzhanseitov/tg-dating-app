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